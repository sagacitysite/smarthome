import requests
from threading import Thread
from time import sleep

from air_intake_servo import AirIntakeServoMotor
from temperature_sensors import TemperatureSensors
from relay import Relay
from mqtt import MqttClient

# TODO
# * Summer program: start pump every x weeks for a short period

class Heatcontrol(Thread):

	def __init__(self):
		"""
		Init Heatcontrol
		"""
		super().__init__()

		# Instantiate MQTT client
		self.client = MqttClient()

		# Instantiate temperature sensors
		self.sensors = TemperatureSensors()

		# Instantiate servo motor
		self.servo = AirIntakeServoMotor()

		# Instantiate pump relay
		self.pump = Relay(22)

		# Define a flag that indicates a running thread
		self.is_running = True

		# Variable to store current fireplace temperature
		self.t_fireplace = 0

		# Counting variables to count up/down a succession of
		# temperature increases/decreases
		self.count_up = 0
		self.count_down = 0

		# Flags indicating if fireplace is heating or cooling
		self.is_heating = False
		self.is_cooling = False

		# Define interval length in seconds
		self.interval = 10

		# Define after how many intervals the sensors/actuators are evaluated
		# The final interval in seconds calculates as interval_count x interval
		self.interval_count_sensors = 1
		self.interval_count_actuators = 6

		# Get parameters from server
		self.profile = self.get_profile()
		print('self.profile', self.profile)

		# Subscribe to changes of fireplace parameters and add a callback function
		# that is called if an MQTT message arrives
		self.client.subscribe('fireplace/parameter', qos=2)
		self.client.on_message('fireplace/parameter', self.on_fireplace_parameter)


	def on_fireplace_parameter(self, message):
		"""
		When a fireplace parameter is published from MQTT, update the value in the profile
		"""
		self.profile[message.key] = message.value
		print('self.profile', self.profile)


	def get_profile(self):
		"""
		Request profile values from nodejs server
		"""
		r = requests.get('http://localhost:4000/profile')
		
		if r.status_code == 200:
			return r.json()
		else:
			return {}


	def update_and_evaluate_sensors(self):
		"""
		Update sensor values (i.e. temperatures)
		"""
		# Store previous value of fireplace temperature
		t_fireplace_previous = self.t_fireplace

		for name in list(self.sensors.sensor_map.keys()):
			temp = self.sensors.get_temperature(name)

			# Send temp to MQTT broker
			if name == 'room':
				self.client.publish(f'room/temperature', temp)
			if name == 'tank_top':
				self.client.publish(f'buffertank/temperature/top', temp)
			if name == 'tank_bottom':
				self.client.publish(f'buffertank/temperature/bottom', temp)
			if name == 'fireplace':
				self.client.publish(f'fireplace/temperature', temp, qos=2)
				# Update object's fireplace temperature
				self.t_fireplace = temp

		# Evaluate if fireplace temperature has increased of decreased
		if int(self.t_fireplace) < int(t_fireplace_previous):  # Lower than before
			self.count_up = 0  # Reset count up
			self.count_down += 1  # Increase count down
		elif int(self.t_fireplace) > int(t_fireplace_previous):  # Higher than before
			self.count_down = 0  # Reset count down
			self.count_up += 1  # Increase count up

		# If we count sufficiently up, we switch from cooling to heating state
		if self.is_cooling and self.count_up >= 3:
			self.client.publish(f'fireplace/heating_state', True, qos=2)
			self.is_cooling = False
			self.is_heating = True
		
		# If we count sufficiently down, we switch from heating to cooling state
		if self.is_heating and self.count_down >= 3:
			self.client.publish(f'fireplace/heating_state', False, qos=2)
			self.is_cooling = True
			self.is_heating = False


	def adjust_air_opening(self, opening):
		"""
		Adjust fireplace air opening and publish to mqtt broker
		"""
		self.servo.adjust_air_opening(opening)
		self.client.publish(f'fireplace/servo', opening, qos=2)


	def switch_pump_relay(self, state):
		"""
		Switch pump relay (on/off) and publish to mqtt broker
		"""
		self.pump.set_state(state)
		self.client.publish(f'fireplace/pump', state, qos=2)


	def evaluate_and_update_actuators(self):
		"""
		Update actuator values:
		* Pump relay
		* Servo motor for air intake
		"""
		# Shorthand for profile values
		p = self.profile

		# Switch ON pump relay
		if (
				not self.pump.is_open and
				self.t_fireplace >= p.t_relais_on and
				self.is_heating
			):
			self.switch_pump_relay(True)

		# Switch OFF pump relay
		# TODO improve with exhaust temperature for cases where buffer is hotter than 73 degree
		if (
				self.pump.is_open and
				self.t_fireplace <= p.t_relais_off and
				self.is_cooling
				# or self.t_exhaust < xx
		):
			self.switch_pump_relay(False)

		# Close air intake half when we're heating up
		if (
				self.servo.state_air_intake != self.servo.INTAKE_CLOSE_HALF and
				self.t_fireplace >= p.t_air_intake_close_half and
				self.t_fireplace < p.t_air_intake_close and
				self.is_heating
			):
			self.servo.state_air_intake = self.servo.INTAKE_CLOSE_HALF
			self.adjust_air_opening(50)

		# Close air intake when we're heating up
		if (
				self.servo.state_air_intake != self.servo.INTAKE_CLOSE and
				self.t_fireplace >= p.t_air_intake_close and
				self.is_heating
			):
			self.servo.state_air_intake = self.servo.INTAKE_CLOSE
			self.adjust_air_opening(p.air_intake_opening_at_full_burn)

		# Open air intake when we're cooling down
		if (
				self.servo.state_air_intake != self.servo.INTAKE_OPEN and
				self.t_fireplace <= p.t_air_intake_open and
				self.is_cooling
			):
			self.servo.state_air_intake = self.servo.INTAKE_OPEN
			self.adjust_air_opening(100)


	def run(self):
		"""
		Run infinite loop, read sensor data and control motor/relay
		"""
		print('heatcontrol running')
		counter = 0
		while self.is_running:
			# Execute every interval
			if counter % self.interval_count_sensors == 0:
				self.update_and_evaluate_sensors()

			"""
			# Execute every twelvth interval
			# NOTE Don't update actuators when servos are refreshed
			if counter % self.interval_count_actuators == 0:
				self.evaluate_and_update_actuators()
			"""

			# Wait until next interval
			sleep(self.interval)

			# Update counter, reset after latest interval count
			counter += 1
			if counter % self.interval_count_actuators == 0:
				counter = 0


	def stop(self):
		"""
		Stop loop and kill thread
		"""
		# Stop loop
		self.is_running = False
		# Wait one iteration
		sleep(self.interval+1)
		# Stop servo
		self.servo.stop()
		# Disconnect MQTT client
		self.client.disconnect()
		# Kill thread
		self.join()

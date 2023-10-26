import requests
import json
from threading import Thread
from time import sleep

from air_intake_servo import AirIntakeServoMotor
from temperature_sensors import TemperatureSensors
from relay import Relay
from mqtt import MqttClient

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
		# Init with actual temperature
		self.t_fireplace = self.sensors.get_temperature('fireplace')

		# Counting variables to count up/down a succession of
		# temperature increases/decreases
		self.count_up = 0
		self.count_down = 0

		# Flags indicating if fireplace is heating or cooling
		self.is_heating = False
		self.is_cooling = True

		# Define interval length in seconds
		self.interval = 10

		# Define after how many intervals the sensors/actuators are evaluated
		# The final interval in seconds calculates as interval_count x interval
		self.interval_count_sensors = 1
		self.interval_count_actuators = 3

		# Get parameters from server
		self.profile = self.get_profile()
		self.has_changed = []  # Array to indicate profile value that have recently changed

		# Subscribe to changes of fireplace parameters and add a callback function
		# that is called if an MQTT message arrives
		self.client.subscribe('fireplace/parameter', qos=2)
		self.client.on_message('fireplace/parameter', self.on_fireplace_parameter)

		self.client.subscribe('fireplace/boost')
		self.client.on_message('fireplace/boost', self.on_fireplace_boost)

		self.client.subscribe('fireplace/final')
		self.client.on_message('fireplace/final', self.on_fireplace_final)


	def on_fireplace_final(self, message_as_string):
		state = int(message_as_string)
		if state == 0:
			self.servo.state_air_intake = self.servo.INTAKE_OPEN	
		elif state == 1:
			self.servo.state_air_intake = self.servo.INTAKE_FINAL
			self.adjust_air_opening(100)


	def on_fireplace_boost(self, message_as_string):
		state = int(message_as_string)
		if state == 0:
			self.servo.state_air_intake = self.servo.INTAKE_OPEN	
		elif state == 1:
			self.servo.state_air_intake = self.servo.INTAKE_BOOST
			self.adjust_air_opening(100)


	def on_fireplace_parameter(self, message_as_string):
		"""
		When a fireplace parameter is published from MQTT, update the value in the profile
		"""
		message = json.loads(message_as_string)
		self.profile[message['key']] = message['value']
		# Store changed key
		self.has_changed.append(message['key'])


	def set_state(self, key, value):
		"""
		Patch fireplace state value
		"""
		json = { 'key': key, 'value': value }
		r = requests.patch('http://localhost:4000/fireplace/state', json=json)


	def get_profile(self):
		"""
		Request profile values from nodejs server
		"""
		r = requests.get('http://localhost:4000/fireplace/profile')
		
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

		# Evaluate if fireplace temperature has increased or decreased
		if int(self.t_fireplace) < int(t_fireplace_previous):  # Lower than before
			self.count_up = 0  # Reset count up
			self.count_down += 1  # Increase count down
		elif int(self.t_fireplace) > int(t_fireplace_previous):  # Higher than before
			self.count_down = 0  # Reset count down
			self.count_up += 1  # Increase count up

		# If we count sufficiently up, we switch from cooling to heating state
		if self.is_cooling and self.count_up >= 3:
			self.set_state('heating_state', 1)
			#self.client.publish(f'fireplace/heating_state', 1, qos=2)
			self.is_cooling = False
			self.is_heating = True
		
		# If we count sufficiently down, we switch from heating to cooling state
		if self.is_heating and self.count_down >= 3:
			self.set_state('heating_state', 0)
			#self.client.publish(f'fireplace/heating_state', 0, qos=2)
			self.is_cooling = True
			self.is_heating = False


	def adjust_air_opening(self, opening):
		"""
		Adjust fireplace air opening and publish to mqtt broker
		"""
		self.servo.adjust_air_opening(opening)
		self.set_state('servo', opening)
		#self.client.publish(f'fireplace/servo', opening, qos=2)


	def switch_pump_relay(self, state):
		"""
		Switch pump relay (on/off) and publish to mqtt broker
		"""
		self.pump.set_state(state)
		self.set_state('pump', int(state))
		#self.client.publish(f'fireplace/pump', int(state), qos=2)


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
				# Default case
				(
					self.is_heating and
					not self.pump.is_open and
					self.t_fireplace >= p['t_relais_on']
				) or
				# If t_relais_off value has changed to a lower value, we possibly need
				# to switch on the pump again in the current cycle
				(
					't_relais_off' in self.has_changed and
					self.is_cooling and
					not self.pump.is_open and
					self.t_fireplace > p['t_relais_off']
				)
			):
			self.switch_pump_relay(True)

		# Switch OFF pump relay
		# TODO improve with exhaust temperature for cases where buffer is hotter than 73 degree
		if (
				# Default case
				(
					self.is_cooling and
					self.pump.is_open and
					self.t_fireplace <= p['t_relais_off']
					# or self.t_exhaust < xx
				) or
				# If t_relais_on value has changed to a higher value, we possibly need
				# to switch off the pump again in the current cycle
				(
					't_relais_on' in self.has_changed and
					self.is_heating and
					self.pump.is_open and
					self.t_fireplace < p['t_relais_on']
				)
		):
			self.switch_pump_relay(False)

		# If one of the air intake temperature parameters has changed, set air intake
		# state to undefined, which forces a re-evaluation of the conditions below
		# NOTE The undefined state (and therefore the old fireplace state) remains,
		#      until one of the conditions below was met
		if (
				't_air_intake_close_half' in self.has_changed or
				't_air_intake_close' in self.has_changed or
				't_air_intake_open' in self.has_changed
			):
			self.servo.state_air_intake = self.servo.INTAKE_UNDEFINED

		# If the air intake at full burn has changed and we are currently in
		# closed servo state, adapt the opening to the new parameter value
		if (
				'air_intake_opening_at_full_burn' in self.has_changed and
				self.servo.state_air_intake == self.servo.INTAKE_CLOSE
			):
			self.adjust_air_opening(p['air_intake_opening_at_full_burn'])

		# Close air intake half when we're heating up
		if (
				self.servo.state_air_intake != self.servo.INTAKE_FINAL and
				self.servo.state_air_intake != self.servo.INTAKE_BOOST and
				self.servo.state_air_intake != self.servo.INTAKE_CLOSE_HALF and
				self.t_fireplace >= p['t_air_intake_close_half'] and
				self.t_fireplace < p['t_air_intake_close'] and
				self.is_heating
			):
			self.servo.state_air_intake = self.servo.INTAKE_CLOSE_HALF
			self.adjust_air_opening(50)

		# Close air intake when we're heating up
		if (
				self.servo.state_air_intake != self.servo.INTAKE_FINAL and
				self.servo.state_air_intake != self.servo.INTAKE_BOOST and
				self.servo.state_air_intake != self.servo.INTAKE_CLOSE and
				self.t_fireplace >= p['t_air_intake_close'] and
				self.is_heating
			):
			self.servo.state_air_intake = self.servo.INTAKE_CLOSE
			self.adjust_air_opening(p['air_intake_opening_at_full_burn'])

		# Open air intake when we're cooling down
		if (
				self.servo.state_air_intake != self.servo.INTAKE_BOOST and
				self.servo.state_air_intake != self.servo.INTAKE_OPEN and
				self.t_fireplace <= p['t_air_intake_open'] and
				self.is_cooling
			):
			self.servo.state_air_intake = self.servo.INTAKE_OPEN
			self.adjust_air_opening(100)
			# If we're cooling down and final burn was active,
			# inform server that final state ends now
			if self.servo.state_air_intake == self.servo.INTAKE_FINAL:
				self.set_state('final', 0)


	def run(self):
		"""
		Run infinite loop, read sensor data and control motor/relay
		"""
		counter = 0
		while self.is_running:
			# Execute every interval
			if counter % self.interval_count_sensors == 0:
				self.update_and_evaluate_sensors()

			# Execute every twelvth interval
			if counter % self.interval_count_actuators == 0:
				self.evaluate_and_update_actuators()
				# Clear has_changed array
				self.has_changed = []

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

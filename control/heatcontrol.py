from threading import Thread
from time import sleep

from air_intake_servo import AirIntakeServoMotor
from temperature_sensors import TemperatureSensors
from pump_relay import FireplacePumpRelay
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
		self.pump = FireplacePumpRelay

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
		self.interval_count_sensors = 1
		self.interval_count_actuators = 6
		self.interval_count_servo_refresh = 60

		# Configuration values
		# TODO get from node.js API (see below), this part can be deleted at some point

		default_profile = {
			't_relais_on': 40,
			't_relais_off': 70,
			't_air_intake_close_half': 35,
			't_air_intake_close': 45,
			't_air_intake_open': 65,
			'air_intake_opening_at_full_burn': 0
		}

		self.profiles = {
			'default':{
				**default_profile
			}, 
			'bjork': {
				**default_profile
			},
			'gran': {
				**default_profile,
				'air_intake_opening_at_full_burn': 20
			}
		}


	def update_and_evaluate_sensors(self):
		"""
		Update sensor values (i.e. temperatures)
		"""
		# Store previous value of fireplace temperature
		t_fireplace_previous = self.t_fireplace

		for name in list(self.sensors.sensor_map.keys()):
			temp = self.sensors.get_temperature(name)

			# Send temp to MQTT broker
			self.client.publish(f'temperature/{name}', temp)

			# Update object's fireplace temperature
			if name == 'fireplace':
				self.t_fireplace = temp

		# Evaluate if fireplace temperature has increased of decreased
		if int(self.t_fireplace) < int(t_fireplace_previous):  # Lower than before
			self.count_up = 0  # Reset count up
			self.count_down += 1  # Increase count down
		elif int(self.t_fireplace) > int(t_fireplace_previous):  # Higher than before
			self.count_down = 0  # Reset count down
			self.count_up += 1  # Increase count up

		# If we count sufficiently up, we are in heating state
		if self.count_up >= 3:
			self.is_cooling = False
			self.is_heating = True
		
		# If we count sufficiently down, we are in cooling state
		if self.count_down >= 3:
			self.is_cooling = True
			self.is_heating = False


	def adjust_air_opening(self, opening):
		"""
		Adjust fireplace air opening and publish to mqtt broker
		"""
		self.servo.adjust_air_opening(opening)
		self.client.publish(f'servo/fireplace', opening)


	def switch_relais(self, state):
		"""
		Switch relais (on/off) and publish to mqtt broker
		"""
		self.pump.set_state(state)
		self.client.publish(f'pump/fireplace', state)


	def evaluate_and_update_actuators(self, p):
		"""
		Update actuator values:
		* Pump relais
		* Servo motor for air intake
		"""
		# Switch ON relais
		if self.t_fireplace >= p.t_relais_on and self.is_heating:
			self.switch_relais(1)

		# Switch OFF relais
		# TODO improve with exhaust temperature for cases where buffer is hotter than 73 degree
		if (self.t_fireplace <= p.t_relais_off and self.is_cooling): # or self.t_exhaust < xx:
			self.switch_relais(0)

		# Close air intake half when we're heating up
		if (
				self.servo.state_air_intake != self.servo.INTAKE_CLOSE_HALF and
				self.t_fireplace >= p.t_air_intake_close_half and
				self.t_fireplace < p.t_air_intake_close and
				self.is_heating
			):
			self.adjust_air_opening(50)

		# Close air intake when we're heating up
		if (
				self.servo.state_air_intake != self.servo.INTAKE_CLOSE and
				self.t_fireplace >= p.t_air_intake_close and
				self.is_heating
			):
			self.adjust_air_opening(p.air_intake_opening_at_full_burn)

		# Open air intake when we're cooling down
		if (
				self.servo.state_air_intake != self.servo.INTAKE_OPEN and
				self.t_fireplace <= p.t_air_intake_open and
				self.is_cooling
			):
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
			if counter % self.interval_count_actuators == 0 and counter % self.interval_count_servo_refresh != 0:
				# Get profile values
				# NOTE this needs to be called regularly to allow on-the-fly profile changes by the user
				# NOTE currently profile values are only used for actuators, but this MAY CHANGE
				# TODO get all profile values from Node.js server (not only the profile name), since some profile values are possibly manually overwritten
				# TODO improve stability: use previous profile, if Node.js server is not available, therefore store profile always in object (would also bin p to self, which is nicer to use)
				# p = self.server.get_profile()
				# p = self.profiles[profile_name] if profile_name in self.profiles else self.profiles['default']
				p = self.profiles['default']

				self.evaluate_and_update_actuators(p)
			"""

			"""
			# Refresh servo
			if counter % self.interval_count_servo_refresh == 0:
				self.adjust_air_opening(self.servo.state_air_intake)
			"""

			# Wait until next interval
			sleep(self.interval)

			# Update counter, reset after latest interval count
			counter += 1
			if counter % self.interval_count_servo_refresh == 0:
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

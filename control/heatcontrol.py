from threading import Thread
from time import sleep

from air_intake_servo import AirIntakeServoMotor
from temperature_sensors import TemperatureSensors

# TODO
# * Summer program: start pump every x weeks for a short period
# * Renew servo position every x minutes

class Heatcontrol(Thread):

	def __init__(self):
		"""
		Init Heatcontrol
		"""
		super().__init__()

		# Instantiate temperature sensors
		self.sensors = TemperatureSensors()

		# Instantiate servo motor
		self.servo = AirIntakeServoMotor()

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

		# Configuration values, get from node.js API

		self.interval = 1 #15 # Define interval length in seconds

		self.air_profiles = {
			'low': 0,
			'medium': 25,
			'high': 50
		}

		self.air_profile = 'low'

		self.t_relais_on = 40
		self.t_relais_off = 70

		self.t_air_intake_close_half = 35
		self.t_air_intake_close = 45
		self.t_air_intake_open = 65


	def get_air_profile_value(self, air_profile_name):
		"""
		Get air intake opening percentage value, based on air profile name
		"""
		return self.air_profiles[air_profile_name]


	def update_temperatures(self):
		"""

		"""
		t_fireplace = 0
		for name in list(self.sensors.sensor_map.keys()):
			temp = self.sensors.get_temperature(name)
			# TODO send temp to API
			if name == 'fireplace':
				t_fireplace = temp

		return t_fireplace

		#t_room = self.sensors.get_temperature('room')
		#t_tank_top = self.sensors.get_temperature('tank_top')
		#t_tank_bottom = self.sensors.get_temperature('tank_bottom')


	def run(self):
		"""
		Run infinite loop, read sensor data and control motor/relay
		"""
		while self.is_running:

			# Get temperatues
			t_room = self.sensors.get_temperature('room')
			t_tank_top = self.sensors.get_temperature('tank_top')
			t_tank_bottom = self.sensors.get_temperature('tank_bottom')

			# Get current temperature from fireplace
			t_fireplace = self.sensors.get_temperature('fireplace')
			t_fireplace_previous = self.t_fireplace

			# Lower than before
			if t_fireplace < t_fireplace_previous:
				self.count_up = 0  # Reset count up
				self.count_down += 1  # Increase count down
			# Higher than before
			elif t_fireplace > t_fireplace_previous:
				self.count_down = 0  # Reset count down
				self.count_up += 1  # Increase count up

			# Update fireplace temperatue
			self.t_fireplace = t_fireplace

			# If we count sufficiently up, we are in heating state
			if self.count_up >= 3:
				self.is_cooling = False
				self.is_heating = True
			
			# If we count sufficiently down, we are in cooling state
			if self.count_down >= 3:
				self.is_cooling = True
				self.is_heating = False

			# Switch ON relais
			if t_fireplace >= self.t_relais_on and self.is_heating:
				pass

			# Switch OFF relais
			# TODO improve with exhaust temperature for cases where buffer is hotter than 73 degree
			if (t_fireplace <= self.t_relais_off and self.is_cooling): # or self.t_exhaust < xx:
				pass

			# Close air intake half when we're heating up
			if t_fireplace >= self.t_air_intake_close_half and self.is_heating:
				self.servo.adjust_air_opening(50)

			# Close air intake when we're heating up
			if t_fireplace >= self.t_air_intake_close and self.is_heating:
				value = self.get_air_profile_value(self.air_profile)
				self.servo.adjust_air_opening(value)

			# Open air intake when we're cooling down
			if t_fireplace <= self.t_air_intake_open and self.is_cooling:
				self.servo.adjust_air_opening(100)

			# Wait until next interval
			sleep(self.interval)


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
		# Kill thread
		self.join()

from w1thermsensor import W1ThermSensor

class TemperatureSensors():

	def __init__(self):
		"""
		Init temperature sensors
		"""

		# Get list of temperature sensors
		self.sensors = W1ThermSensor.get_available_sensors()

		# Map sensor name to sensor id
		# NOTE 'fireplace' is required
		self.sensor_map = {
			'fireplace': '3c01d075dea7'
			#'tank_top': '',
			#'tank_bottom': '',
			#'room': ''
		}


	def get_sensor_by_name(self, sensor_name):
		"""
		Get a temperature sensor by sensor name
		"""

		# Get sensor id by sensor name
		sensor_id = self.sensor_map[sensor_name]
		# Filter sensor by sensor id
		filtered = list(filter(lambda s: s.id == sensor_id, self.sensors))

		# Check if filtered value was found
		# Either raise exception or return filtered sensor
		if len(filtered) == 0:
			raise Exception('Sensor not found: sensor defective or sensor name not correct.')
		else:
			return filtered[0]


	def get_temperature(self, sensor_name):
		"""
		Get temperature from sensor by sensor name
		"""

		# Find sensor
		sensor = self.get_sensor_by_name(sensor_name)
		# Return rounded temperature
		return int(round(sensor.get_temperature(), 0))

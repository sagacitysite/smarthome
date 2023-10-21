import RPi.GPIO as GPIO

class Relay():

	def __init__(self, PIN):
		"""
		Init pump relay
		"""

		# Init PIN
		self.relay_PIN = PIN
		# Flag indicating state of relay
		self.is_open = False

		# Setup GPIO PIN for relay
		GPIO.setup(self.relay_PIN, GPIO.OUT)

		# Start program with closed relay
		self.close()


	def set_state(self, state):
		"""
		Set pump state based on a boolean variable
		"""
		if state == True:
			self.open()
		else:
			self.close()


	def open(self):
		"""
		Open relay
		"""
		GPIO.output(self.relay_PIN, GPIO.LOW)
		self.is_open = True


	def close(self):
		"""
		Close relay
		"""
		GPIO.output(self.relay_PIN, GPIO.HIGH)
		self.is_open = False

import RPi.GPIO as GPIO

class FireplacePumpRelay():

	def __init__(self):
		"""
		Init pump relay
		"""

		# Init PIN
		self.relay_PIN = 22
		# Flag indicating state of relay
		self.is_pump_running = False

		# Setup GPIO PIN for relay
		GPIO.setup(self.relay_PIN, GPIO.OUT)

		# Start program with stopped pump
		self.stop()


	def set_state(self, state):
		"""
		Set pump state based on a boolean variable
		"""
		if state == True:
			self.start()
		else:
			self.stop()


	def start(self):
		"""
		Start pump via opening relay
		"""
		GPIO.output(self.relay_PIN, GPIO.HIGH)
		self.is_pump_running = True


	def stop(self):
		"""
		Stop pump via closing relay
		"""
		GPIO.output(self.relay_PIN, GPIO.LOW)
		self.is_pump_running = False

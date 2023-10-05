from time import sleep
import RPi.GPIO as GPIO

class AirIntakeServoMotor():

	def __init__(self):
		"""
		Init servor motor
		"""

		# Init PIN and PWM frequency
		servoPIN = 17
		pwmFrequency = 50

		# Delay in seconds after new position command was executed
		self.delay = 1

		# Duty values for servo control
		self.duty_open = 7.75
		self.duty_closed = 3.25
		self.duty_diff = self.duty_open - self.duty_closed
		self.duty_hundredth = self.duty_diff/100

		# Setup GPIO PIN for servo motor
		GPIO.setup(servoPIN, GPIO.OUT)

		# Initliaize and start servo PWM control
		self.servo = GPIO.PWM(servoPIN, pwmFrequency)
		self.servo.start(0)


	def stop(self):
		"""
		Stop servo pwm
		"""
		self.servo.stop()


	def get_duty_from_percentage(self, percentage):
		"""
		Calculate duty from percantage value
		"""

		return self.duty_closed + self.duty_hundredth*percentage


	def adjust_air_opening(self, percentage):
		"""
		Adjust opening of fireplace air intake
		"""

		# Calculate duty from opening percentage
		duty = get_duty_from_percentage(percentage)
		# Adjust servo to given position
		self.servo.ChangeDutyCycle(7.75)
		# Wait some time to make sure that the final position is reached
		sleep(self.delay)
		# Stop servo activiy
		self.servo.ChangeDutyCycle(0)

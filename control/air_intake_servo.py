from time import sleep
import RPi.GPIO as GPIO

from relay import Relay

class AirIntakeServoMotor():

	def __init__(self):
		"""
		Init servor motor
		"""

		# Init PIN and PWM frequency
		servo_PIN = 17
		pwm_frequency = 50

		# Delay in seconds after new position command was executed
		self.servo_delay = 1

		# Delay in seconds after relay was opened and before position is changed
		# and before relay is closed and after position was changed
		self.relay_delay = 0.5

		# Duty values for servo control
		self.duty_open = 7.75
		self.duty_closed = 3.25
		self.duty_diff = self.duty_open - self.duty_closed
		self.duty_hundredth = self.duty_diff/100

		# Variable indicating the opening of the air intake
		self.air_intake_opening = 100

		# Variable indicating air intake state
		self.INTAKE_UNDEFINED = -1
		self.INTAKE_OPEN = 0
		self.INTAKE_CLOSE_HALF = 1
		self.INTAKE_CLOSE = 2
		self.INTAKE_BOOST = 3
		self.INTAKE_FINAL = 4
		self.state_air_intake = self.INTAKE_OPEN

		# Realy for servo
		self.relay = Relay(27)

		# Setup GPIO PIN for servo motor
		GPIO.setup(servo_PIN, GPIO.OUT)

		# Initliaize and start servo PWM control
		self.servo = GPIO.PWM(servo_PIN, pwm_frequency)
		self.servo.start(0)
		self.adjust_air_opening(self.air_intake_opening)


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

		# Store new opening in object
		self.air_intake_opening = percentage

		# Calculate duty from opening percentage
		duty = self.get_duty_from_percentage(percentage)

		# Open relay
		self.relay.open()
		sleep(self.relay_delay)

		# Adjust servo to given position
		self.servo.ChangeDutyCycle(duty)
		# Wait some time to make sure that the final position is reached
		sleep(self.servo_delay)
		# Stop servo activiy
		self.servo.ChangeDutyCycle(0)

		# Close relay
		sleep(self.relay_delay)
		self.relay.close()

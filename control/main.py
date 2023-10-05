import atexit
import RPi.GPIO as GPIO

from heatcontrol import Heatcontrol

# Set GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Instantiate and run heatcontrol
heatcontrol = Heatcontrol()
heatcontrol.start()

# Define cleanup function that is called at exit
def cleanup():
	"""
	Run cleanup commands, e.g. stop threads, GPIO cleanup
	"""
	heatcontrol.stop()
	GPIO.cleanup()

# At exit, run cleanup function
atexit.register(cleanup)

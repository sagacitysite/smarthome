#import asyncio
#import signal
#from gmqtt import Client as Mqtt
from events import Events
from paho.mqtt.client import Client as Mqtt

class MqttClient():

	def __init__(self):
		"""
		Initialize MQTT client
		"""
		# Dict to store MQTT topic/event pairs
		self.events = {}

		# Crate MQTT client
		self.mqtt = Mqtt('control')

		# Register MQTT events
		self.mqtt.on_connect = self.on_mqtt_connect
		self.mqtt.on_message = self.on_mqtt_message
		self.mqtt.on_disconnect = self.on_mqtt_disconnect
		self.mqtt.on_subscribe = self.on_mqtt_subscribe

		# Connect to MQTT broker
		self.mqtt.connect('192.168.1.126')

		# Run client in background
		self.mqtt.loop_start()


	def add_event(self, topic):
		"""
		Adds an event object as value for a topic
		"""
		self.events[topic] = Events()


	def disconnect(self):
		"""
		"""
		self.mqtt.disconnect()
		self.mqtt.loop_stop()


	def publish(self, topic, message, qos=1):
		self.mqtt.publish(topic, message, qos)


	def subscribe(self, topic, qos=1):
		"""
		Subcribes a new topic to MQTT and adds an event for the topic 
		"""
		if topic not in self.events:
			self.add_event(topic)
			self.mqtt.subscribe(topic, qos=qos)


	def on_message(self, topic, cb):
		"""
		Adds a callback function to event updates on the given topic target
		"""
		target = self.events[topic]
		target.on_change += cb


	def on_mqtt_connect(self, client, userdata, flags, rc):
		"""
		Called when MQTT is connected
		"""
		print('connected')


	def on_mqtt_message(self, client, userdata, msg):
		"""
		Called when MQTT receives a message
		"""
		message = msg.payload.decode()
		# Triggers the event of the specific topic and hands over the payload
		target = self.events[msg.topic]
		target.on_change(message)


	def on_mqtt_disconnect(self, client, userdata, rc):
		"""
		Called when MQTT disconnects
		"""
		pass


	def on_mqtt_subscribe(self, client, userdata, mid, granted_qos):
		"""
		Called when MQTT subscription was added
		"""
		pass

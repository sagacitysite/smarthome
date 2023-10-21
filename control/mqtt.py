#import asyncio
#import signal
#from gmqtt import Client as Mqtt
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
		self.mqtt.connect('localhost')

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
		print('publish', topic, message)
		self.mqtt.publish(topic, message, qos)


	def subscribe(self, topic, cb, qos=1):
		"""
		Subcribes a new topic to MQTT and adds an event for the topic 
		"""
		print('subscribe', topic, qos)
		if topic not in self.events:
			self.add_event(topic)
			self.mqtt.subscribe(topic, qos=qos)


	def on_message(self, topic, cb):
		"""
		Adds a callback function to event updates on the given topic target
		"""
		target = self.events[topic]
		target.on_change += cb


	def on_mqtt_connect(self, client, flags, rc, properties):
		"""
		Called when MQTT is connected
		"""
		print('connected')


	def on_mqtt_message(self, client, topic, payload, qos, properties):
		"""
		Called when MQTT receives a message
		"""
		print('message reveived', payload)
		# Triggers the event of the specific topic and hands over the payload
		target = self.events[topic]
		target.on_change(payload)


	def on_mqtt_disconnect(self, client, packet, exc=None):
		"""
		Called when MQTT disconnects
		"""
		pass


	def on_mqtt_subscribe(self, client, mid, qos, properties):
		"""
		Called when MQTT subscription was added
		"""
		pass

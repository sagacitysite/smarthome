#import asyncio
#import signal
#from gmqtt import Client as Mqtt
from paho.mqtt.client import Client as Mqtt

class MqttClient():

	def __init__(self):
		"""
		"""
		self.mqtt = Mqtt('control')

		self.mqtt.on_connect = self.on_connect
		self.mqtt.on_message = self.on_message
		self.mqtt.on_disconnect = self.on_disconnect
		self.mqtt.on_subscribe = self.on_subscribe

		self.mqtt.connect('localhost')

		self.mqtt.loop_start()


	def disconnect(self):
		"""
		"""
		self.mqtt.disconnect()
		self.mqtt.loop_stop()


	def publish(self, path, message, qos=1):
		print('publish', path, message)
		self.mqtt.publish(path, message, qos)


	def subscribe(self, path, qos=1):
		self.mqtt.subscribe(path, qos)


	def on_connect(self, client, flags, rc, properties):
		print('connected')


	def on_message(self, client, topic, payload, qos, properties):
		print('message reveived', payload)


	def on_disconnect(self, client, packet, exc=None):
		pass


	def on_subscribe(self, client, mid, qos, properties):
		pass

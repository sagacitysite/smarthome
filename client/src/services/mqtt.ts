// @ts-ignore
import * as mqtt from 'mqtt/dist/mqtt.min';

// List of topic subscriptions
const subscriptions: string[] = [
	'fireplace/temperature',
	'fireplace/servo',
	'fireplace/pump',
	'fireplace/parameter',
	'fireplace/heating_state',
	'buffertank/temperature/top',
	'buffertank/temperature/bottom'
];

// Event targets
const eventTargets: any = {};

export function startMqttClient() {

	// Create event targets
	for (const topic of subscriptions) {
		eventTargets[topic] = new EventTarget()
	}

	// Define options and connect
	const options: object = {
		keepalive: 60,
		clientId: 'screen'
	}
	const client = mqtt.connect('ws://192.168.1.74:9001', options);

	// On connect, add subscriptions
	client.on('connect', () => {
		for (const topic of subscriptions) {
			if (topic.startsWith('fireplace')) {
				client.subscribe(topic, { 'qos': 2 });
			} else {
				client.subscribe(topic);
			}
		}
	});

	// On message, dispatch event to event target of specfic topic
	client.on('message', (topic: string, raw: any) => {
		// Byte message to string
		const message: string = raw.toString();

		// Define custom event that carries the message
		const event = new CustomEvent(topic, {
			'detail': { message }
		});

		// Dispatch event to target, defined by the topic
		eventTargets[topic].dispatchEvent(event);
	});

	// Disconnect before window closes
	window.onbeforeunload = function(){
		client.end();
	}
}

/**
 * Adds an event listener to the event target that corresponds to a MQTT topic
 * The callback for the event listener is wrapped to directly provide the message,
 * instead of the pure event
 */
export function onMessage(topic: string, cb: Function) {
	const target = eventTargets[topic];
	target.addEventListener(topic, (event: CustomEvent) => {
		cb(event.detail.message);
	});
}

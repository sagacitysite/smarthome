// @ts-ignore
import * as mqtt from 'mqtt/dist/mqtt.min';

// Event targets
const eventTargets: any = {};

let client: any;

export function startMqttClient() {

	// Define options and connect
	const options: object = {
		keepalive: 60,
		clientId: 'screen'
	}
	if (client === undefined) {
		client = mqtt.connect('ws://192.168.1.126:9001', options);
	}

	// On connect, add subscriptions
	client.on('connect', () => {
		console.log('connect');
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
 * Subscribes a topic to a MQTT server
 * It adds an event target to the list of targets
 * 
 * @param {string} topic
 * @param {number} qos Quality of service (0, 1 or 2)
 */
export function subscribe(topic: string, qos: number) {
	// If quality of service is not given, use default value
	if (qos === undefined) qos = 1;

	// Subscribe to topic
	client.subscribe(topic, { 'qos': qos });

	// Add event target
	if (!(topic in eventTargets)) {
		eventTargets[topic] = new EventTarget();
	}
}

/**
 * Adds an event listener to the event target that corresponds to a MQTT topic
 * The callback for the event listener is wrapped to directly provide the message,
 * instead of the pure event
 * 
 * @param {string} topic
 * @param {Function} cb Callback function that is called when the event is triggered
 */
export function onMessage(topic: string, cb: Function) {
	const target = eventTargets[topic];
	target.addEventListener(topic, (event: CustomEvent) => {
		cb(event.detail.message);
	});
}

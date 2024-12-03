import * as mqtt from 'mqtt';

// Init mqtt
const options = {
	keepalive: 60,
	clientId: 'server'
}
export const client = mqtt.connect('ws://localhost:9001', options);

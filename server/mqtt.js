import * as mqtt from 'mqtt';

// Init mqtt
const options = {
	keepalive: 60,
	clientId: 'server'
}
export const client = mqtt.connect('ws://192.168.1.74:9001', options);

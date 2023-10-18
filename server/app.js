// Import official packages
import express from 'express';
import bodyParser from 'body-parser';

// Import own objects
import { Profile } from './profile.js';
import { client } from './mqtt.js';

// Initialize express app
const app = express();

// Allow access requests from everywhere
app.use(function (req, res, next) {
	res.setHeader('Access-Control-Allow-Origin', '*');
	res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE');
	res.setHeader('Access-Control-Allow-Headers', 'X-Requested-With,content-type');
	next();
});

// JSON Parser for post requests
const jsonParser = bodyParser.json()

// Instantiate profile
const profile = new Profile();

// Used from Python control script, get the currently selected profile
// Takes into accont overwritten values
app.get('/profile', (req, res) => {
	res.send(profile.getValues())
});

// Used from frontend to overwrite profile values
app.patch('/profile', jsonParser, (req, res) => {
	// Get key and value from profile to update
	const key = req.body.key;
	const value = req.body.value;

	// Update value in profile and get status
	const wasSuccessful = profile.updateValue(key, value);

	if (wasSuccessful) {
		// If update was successful, publish profile vaue to all subscribers
		const parameter = JSON.stringify({ 'key': key, 'value': value });
		client.publish('fireplace/parameter', parameter, { 'qos': 2 });
		// Send ok to client
		res.send('OK');
	} else {
		res.status(400);
		res.send('Key not found in profile.');
	}
});

// Start server
const port = 4000;
app.listen(port, () => console.log(`The server is listening on port ${port}.`));

// Disconnect MQTT client before exit
// Source: https://stackoverflow.com/a/49392671/2692283
const exitConditioons = [`exit`, `SIGINT`, `SIGUSR1`, `SIGUSR2`, `uncaughtException`, `SIGTERM`];
exitConditioons.forEach((eventType) => {
	process.on(eventType, (eventType) => {
		client.end();
		process.exit();
	});
});

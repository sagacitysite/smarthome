// Import official packages
import express from 'express';
import bodyParser from 'body-parser';

// Import own objects
import { Fireplace } from './data/fireplace.js';
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

// Instantiate fireplace
const fireplace = new Fireplace();

// Used from all clients to get the current profile parameter set
// Takes into accont overwritten values
app.get('/fireplace/profile', (req, res) => {
	res.send(fireplace.getParameter())
});

// Used from frontend to overwrite profile parameter values
app.patch('/fireplace/profile', jsonParser, (req, res) => {
	// Get key and value from profile parameter to update
	const key = req.body.key;
	const value = req.body.value;

	// Update parameter value in profile and get status
	const wasSuccessful = fireplace.updateParameter(key, value);

	if (wasSuccessful) {
		// If update was successful, publish profile value to all subscribers
		const parameter = JSON.stringify({ 'key': key, 'value': value });
		client.publish('fireplace/parameter', parameter, { 'qos': 2 });
		// Send ok to client
		res.send('OK');
	} else {
		res.status(400);
		res.send('Key not found in profile parameters.');
	}
});

// Used from all clients to get the current fireplace state
app.get('/fireplace/state', (req, res) => {
	res.send(fireplace.getState())
});

// Used from all clients to change the fireplace state
app.patch('/fireplace/state', jsonParser, (req, res) => {
	// Get key and value from state to update
	const key = req.body.key;
	const value = req.body.value;

	// Update parameter value in profile and get status
	const wasSuccessful = fireplace.updateState(key, value);

	if (wasSuccessful) {
		// If update was successful, publish state value to all subscribers
		client.publish(`fireplace/${key}`, value);
		// Send ok to client
		res.send('OK');
	} else {
		res.status(400);
		res.send('Key not found in fireplace state.');
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

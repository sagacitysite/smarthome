// Import official packages
import express from 'express';
import bodyParser from 'body-parser';

// Import own objects
import { Profile } from './profile.js';

// Initialize express app
const app = express();

// Allow access requests from everywhere
app.use(function (req, res, next) {
	res.setHeader('Access-Control-Allow-Origin', '*');
	res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE');
	res.setHeader('Access-Control-Allow-Headers', 'X-Requested-With,content-type');
	next();
});

// Instantiate profile
const profile = new Profile();

/**
 * Send the selected profile to the client
 * 
 * @param {*} req
 * @param {*} res
 */
function getProfileValues(req, res) {
	res.send(profile.getValues());
}


/**
 * Change value from selected profile
 * 
 * @param {*} req
 * @param {*} res
 */
function updateProfileValue (req, res) {
	// Get key and value from profile to update
	const key = req.body.key;
	const value = req.body.value;

	// Update value in profile and get status
	const status = profile.updateValue(key, value);

	// Set status for response
	res.status(status);

	// Add messages, depending on status code
	if (status == 200) {
		res.send('OK');
	}
	else if (status == 400) {
		res.send('Key not found in profile.');
	}
}


// JSON Parser for post requests
const jsonParser = bodyParser.json()

// Used from Python control script, get the currently selected profile
// Takes into accont overwritten values
app.get('/profile', getProfileValues);

// Used from frontend to overwrite profile values
app.patch('/profile', jsonParser, updateProfileValue);

// Start server
const port = 4000;
app.listen(port, () => console.log(`The server is listening on port ${port}.`));

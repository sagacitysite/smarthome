// Import official packages
import { express } from 'express';
import { bodyParser } from 'body-parser';

// Import own objects
import { profiles } from 'data/profiles.js';

// Initialize express app
const app = express();

// Allow access requests from everywhere
app.use(function (req, res, next) {
	res.setHeader('Access-Control-Allow-Origin', '*');
	res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE');
	res.setHeader('Access-Control-Allow-Headers', 'X-Requested-With,content-type');
	next();
});

// Store currently selected profile name and the selected profile itself
let profileName = 'default';
let selectedProfile = profiles[profileName];

/**
 * Send the selected profile to the client
 * 
 * @param {*} req
 * @param {*} res
 */
function getProfile(req, res) {
	res.send(selectedProfile);
}

/**
 * Set profile name and also update selected profile
 * 
 * @param {*} req
 * @param {*} res
 */
function setProfileName(req, res) {
	// Get profile name from body
	const name = req.body.name;

	if (name in profiles) {
		// Set profile name and update selected profile
		profileName = name;
		selectedProfile = profiles[name];
		// Send OK
		res.send('OK');
	} else {
		// If name was not found in profiles, send 'Bad request'
		res.status(400);
		res.send('Profile name is not valid.');
	}
}

/**
 * Change value from selected profile
 * 
 * @param {*} req
 * @param {*} res
 */
function setValue (req, res) {
	// Get key and value from profile to update
	const key = req.body.key;
	const value = req.body.value;

	if (key in selectedProfile) {
		// Update selected profile value
		selectedProfile[key] = value;
		// Send OK
		res.send('OK');
	} else {
		// If key was not found in selectedProfile, send 'Bad request'
		res.status(400);
		res.send('Key not found in profile.');
	}
}

// JSON Parser for post requests
const jsonParser = bodyParser.json()

// Used from Python control script, get the currently selected profile
// Takes into accont overwritten values
app.get('/profile', getProfile);

// Used from frontend, where user chooses the heating profile
app.post('/profile_name', jsonParser, setProfileName);  // Just store this in memory, after reboot just use 'default'

// Used from frontend to overwrite profile values
app.post('/set_value', jsonParser, setValue);

// Start server
const port = 4000;
app.listen(port, () => console.log(`The server is listening on port ${port}.`));

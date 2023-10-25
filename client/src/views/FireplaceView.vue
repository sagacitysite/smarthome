<script setup lang="ts">
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiThermometer, mdiCog, mdiPlus, mdiMinus, mdiRocketLaunch, mdiWeatherDust } from '@mdi/js';
import { ref, reactive, onMounted } from 'vue';

import { Fireplace } from '../services/fireplace';
import { subscribe, onMessage } from '../services/mqtt';
import { get, patch } from '../services/http';
import { formatTime } from '../services/time';

const settings = reactive({
	't_relais_on': { 'label': 'Relay ON', 'value': 0, 'unit': '°', 'step': 1, 'isUpdating': false },
	't_relais_off': { 'label': 'Relay OFF', 'value': 0, 'unit': '°', 'step': 1, 'isUpdating': false },
	't_air_intake_close_half': { 'label': 'Half close air intake', 'value': 0, 'unit': '°', 'step': 1, 'isUpdating': false },
	't_air_intake_close': { 'label': 'Full close air intake', 'value': 0, 'unit': '°', 'step': 1, 'isUpdating': false },
	't_air_intake_open': { 'label': 'Open air intake', 'value': 0, 'unit': '°', 'step': 1, 'isUpdating': false },
	'air_intake_opening_at_full_burn': { 'label': 'Opening at full close', 'value': 0, 'unit': '%', 'step': 5, 'isUpdating': false }
});

// Variable to store fireplace graphic object
let fireplace;

// Boost
const boostSeconds = 3;
let isBoost = ref(false);
let boostLabel = ref('Boost');
let boostTimer;

// Final
let isFinal = ref(false);

// This flag is used to indicate which tab is opened (Status / Settings)
let isSetting = ref(false);

// Get canvas element from DOM
const canvas = ref('canvas');

/**
 * Get profile values from server and update settings values
 */
async function getSettingsValuesFromServer() {
	get('/fireplace/profile').then((res) => {
		// Update local values
		for (const key in settings) {
			settings[key].value = res.data[key]
		}

		// Subscribe to fireplace parameters with qos of 2
		subscribe('fireplace/parameter', 2);

		// Register event handler for parameters
		onMessage('fireplace/parameter', (message) => {
			// Parse message from event details
			const p = JSON.parse(message);
			// Update value
			settings[p.key].value = p.value;
			// Activate form, wait at least some milliseconds to make it look nice
			setTimeout(() => {
				settings[p.key].isUpdating = false;
			}, 100);
		});
	});
}

/**
 * Get fireplace state values from server
 */
async function getStateValuesFromServer() {
	get('/fireplace/state').then((res) => {
		for (const [key, value] of Object.entries(res.data)) {
			const topic = `fireplace/${key}`;
			// Update state
			updateState(topic, value)
			// Subscribe to fireplace states
			subscribe(topic);
			// Register event handler for the current state
			onMessage(topic, updateState.bind(this, topic));
		}
	});
}

function updateState(topic, state) {
	if (topic == 'fireplace/temperature') {
		fireplace.setTemperatureFireplace(state);
	}

	if (topic == 'fireplace/servo') {
		fireplace.setServoOpening(state);
	}

	if (topic == 'fireplace/pump') {
		if (parseInt(state) == 0) {
			fireplace.stopPump();
		} else {
			fireplace.startPump();
		}
	}

	if (topic == 'fireplace/heating_state') {
		if (parseInt(state) == 0) {
			fireplace.isCooling();
		} else {
			fireplace.isHeating();
		}
	}

	if (topic == 'fireplace/boost') {
		console.log(topic, state);
	}
}

/**
 * Publish new profile value via the MQTT client
 * 
 * @param {string} key Key of the profile parameter
 * @param {string|number} newValue Updated value of the profile parameter
 */
function patchParameter(key, newValue) {

	// Check if we are allowed to edit
	if (settings[key].isUpdating) return;

	// Check if value exceeds limits
	if (newValue < 0 || newValue > 100) return;

	// Deactivate form for specific parameter
	settings[key].isUpdating = true;

	// Send key/value to nodejs server
	// The nodejs server then sends the new value via MQTT
	const data = { 'key': key, 'value': newValue };
	patch('/fireplace/profile', data).catch((err) => {
		setTimeout(() => {
			settings[key].isUpdating = false;
		}, 100);
	});
}

function patchState(key, newValue) {
	// Send key/value to nodejs server
	// The nodejs server then sends the new value via MQTT
	const data = { 'key': key, 'value': newValue };
	patch('/fireplace/state', data);
}

function clearBoost() {
	clearInterval(boostTimer);
	patchState('boost', '0');
	isBoost.value = false;
	boostLabel.value = 'Boost';
}

function boost() {
	if (isBoost.value) {
		// If Boost is already active, stop timer and Boost
		clearBoost();
	}
	else {
		// If Boost is not active, start it and stop it automaticall after 3 minutes
		patchState('boost', '1');
		isBoost.value = true;
		let seconds = boostSeconds;
		boostTimer = setInterval(() => {
			if (seconds == 0) {
				clearBoost();
			} else {
				let m = formatTime(parseInt(seconds / 60));
				let s = formatTime(seconds % 60);
				boostLabel.value = `${m}:${s}`;
			}
			seconds -= 1;
		}, 1000);
	}
}

function final() {
	console.log('final', isFinal.value);
	if (isFinal.value) {
		client.publish('fireplace/final', '0');
		isFinal.value = false;
	} else {
		client.publish('fireplace/final', '1');
		isFinal.value = true;
	}
}

onMounted(async () => {
	// Init fireplace
	fireplace = new Fireplace(canvas.value);
	await fireplace.build();

	// Get profile from server and store in settings
	getSettingsValuesFromServer();

	// Get state from server
	getStateValuesFromServer();

	// Subscribe to buffer tank and register event handler
	subscribe('buffertank/temperature/top');
	onMessage('buffertank/temperature/top', (message) => {
		fireplace.setTemperatureTankTop(message);
	});
	subscribe('buffertank/temperature/bottom');
	onMessage('buffertank/temperature/bottom', (message) => {
		fireplace.setTemperatureTankBottom(message);
	});
});
</script>

<template>
	<div class="window">
		<section class="status" v-show="!isSetting">
			<canvas id="canvas" ref="canvas" resize></canvas>
			<div class="manual-control">
				<a @click="boost()" :class="{ 'active': isBoost }">
					<svg-icon class="icon icon-margin" type="mdi" :path="mdiRocketLaunch"></svg-icon> <span>{{ boostLabel }}</span>
				</a>
				<a @click="final()" :class="{ 'active': isFinal }">
					<svg-icon class="icon icon-margin" type="mdi" :path="mdiWeatherDust"></svg-icon> <span>Final</span>
				</a>
			</div>
		</section>
		<section class="setting-wrapper" v-show="isSetting">
			<div class="setting">
				<div class="setting-row" :class="{ 'updating': s.isUpdating }" v-for="(s, key) in settings">
					<a @click="patchParameter(key, s.value-s.step)">
						<svg-icon class="icon" type="mdi" :path="mdiMinus"></svg-icon>
					</a>
					<span class="value">{{ s.value }}{{ s.unit }}</span>
					<a @click="patchParameter(key, s.value+s.step)">
						<svg-icon class="icon" type="mdi" :path="mdiPlus"></svg-icon>
					</a>
					<span class="label">{{ s.label }}</span>
				</div>
			</div>
		</section>
	</div>
	<div class="tabs">
		<ul>
			<li>
				<a @click="isSetting = false" :class="{ 'active': !isSetting }">
					<svg-icon class="icon icon-margin" type="mdi" :path="mdiThermometer"></svg-icon> <span>Status</span>
				</a>
			</li>
			<li>
				<a @click="isSetting = true" :class="{ 'active': isSetting }">
					<svg-icon class="icon icon-margin" type="mdi" :path="mdiCog"></svg-icon> <span>Settings</span>
				</a>
			</li>
		</ul>
	</div>
</template>

<style scoped>
#canvas {
	width: 100%;
	height: 80vh;
}

a {
	display: flex;
	align-items: center;
	cursor: pointer;
	font-size: 16px;
	margin: 0 5px;
	border-radius: 5px;
}

.icon-margin {
	margin-right: 0.25rem;
}

.window {
	height: 80vh;
}

.tabs {
	height: 20vh;
	padding-top: 10px;
}

.tabs ul {
	list-style: none;
	padding: 0;
	display: flex;
	align-items: center;
	justify-content: center;
}

.tabs ul li a {
	padding: 0 18px 0 15px;
	height: 50px;
	line-height: 50px;
}

.tabs ul li a.active {
	background-color: var(--black-highlight);
}

.status {
	position: relative;
}

.status .manual-control {
	position: absolute;
	display: flex;
	justify-content: center;
	top: 25px;
	left: 0;
	right: 0;
}

.status .manual-control a {
	padding: 0 18px 0 15px;
	height: 50px;
	line-height: 50px;
	background-color: var(--black-highlight);
}

.status .manual-control a.active {
	background-color: var(--black-soft);
}

.setting-wrapper {
	text-align: center;
}

.setting {
	display: inline-block;
	padding: 30px;
	margin: 0 auto;
}

.setting-row {
	display: flex;
	margin-bottom: 10px;
	opacity: 1;
}

.setting-row.updating {
	opacity: 0.5;
}

.setting .value {
	color: var(--white);
	text-align: center;
	font-size: 20px;
	height: 30px;
	width: 55px;
	line-height: 30px;
}

.setting .label {
	margin-left: 12px;
	font-size: 18px;
	line-height: 30px;
}

.setting a {
	color: var(--white);
	background-color: var(--black-highlight);
	padding: 5px;
}

.setting a.soft {
	background-color: var(--black-soft);
}

.setting a.soft .icon {
	color: var(--grey-500);
}
</style>

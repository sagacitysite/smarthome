<script setup lang="ts">
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiThermometer, mdiCog, mdiPlus, mdiMinus } from '@mdi/js';
import { ref, reactive, onMounted } from 'vue';
import axios from 'axios';

import { Fireplace } from '../services/fireplace';
import { onMessage } from '../services/mqtt';

const settings = reactive({
	't_relais_on': { 'label': 'Relay ON', 'value': 0, 'unit': '°', 'isUpdating': false },
	't_relais_off': { 'label': 'Relay OFF', 'value': 0, 'unit': '°', 'isUpdating': false },
	't_air_intake_close_half': { 'label': 'Half close air intake', 'value': 0, 'unit': '°', 'isUpdating': false },
	't_air_intake_close': { 'label': 'Full close air intake', 'value': 0, 'unit': '°', 'isUpdating': false },
	't_air_intake_open': { 'label': 'Open air intake', 'value': 0, 'unit': '°', 'isUpdating': false },
	'air_intake_opening_at_full_burn': { 'label': 'Opening at full close', 'value': 0, 'unit': '%', 'isUpdating': false }
});

// Variable to store fireplace graphic object
let fireplace;

// This flag is used to indicate which tab is opened (Status / Settings)
let isSetting = ref(false);

// Get canvas element from DOM
const canvas = ref('canvas');

/**
 * Get profile values from server and update settings values
 */
async function updateSettingsValuesFromServer() {
	axios.get('http://192.168.1.74:4000/profile').then((res) => {
		for (const key in settings) {
			settings[key].value = res.data[key]
		}
	});
}

/**
 * Publish new profile value via the MQTT client
 * 
 * @param {string} key Key of the profile parameter
 * @param {string|number} newValue Updated value of the profile parameter
 */
function publishNewValue(key, newValue) {

	// Check if we are allow to edit
	if (settings[key].isUpdating) return;

	// Check if value exceeds limits
	if (newValue < 0 || newValue > 100) return;

	// Deactivate form for specific parameter
	settings[key].isUpdating = true;

	// Send key/value to nodejs server
	// The nodejs server then sends the new value via MQTT
	const data = { 'key': key, 'value': newValue };
	axios.patch('http://192.168.1.74:4000/profile', data).catch((err) => {
		setTimeout(() => {
			settings[key].isUpdating = false;
		}, 100);
	});
}

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

onMessage('fireplace/temperature', (message) => {
	console.log('on', 'fireplace/temperature', message);
	fireplace.setTemperatureFireplace(message);
});

onMessage('fireplace/servo', (message) => {
	console.log('on', 'fireplace/servo', message);
	fireplace.setServoOpening(message);
});

onMessage('fireplace/pump', (message) => {
	console.log('on', 'fireplace/pump', message);
	if (parseInt(message) == 0) {
		fireplace.stopPump();
	} else {
		fireplace.startPump();
	}
});

onMessage('fireplace/heating_state', (message) => {
	console.log('on', 'fireplace/heating_state', message);
	if (parseInt(message) == 0) {
		fireplace.isCooling();
	} else {
		fireplace.isHeating();
	}
});

onMessage('buffertank/temperature/top', (message) => {
	fireplace.setTemperatureTankTop(message);
});

onMessage('buffertank/temperature/bottom', (message) => {
	fireplace.setTemperatureTankBottom(message);
});

onMounted(async () => {
	// Init fireplace
	fireplace = new Fireplace(canvas.value);
	await fireplace.build();

	// Get profile from server and store in settings
	updateSettingsValuesFromServer();
});
</script>

<template>
	<div class="window">
		<section class="status" v-show="!isSetting">
			<canvas id="canvas" ref="canvas" resize></canvas>
		</section>
		<section class="setting-wrapper" v-show="isSetting">
			<div class="setting">
				<div class="setting-row" :class="{ 'updating': s.isUpdating }" v-for="(s, key) in settings">
					<a @click="publishNewValue(key, s.value-1)">
						<svg-icon class="icon" type="mdi" :path="mdiMinus"></svg-icon>
					</a>
					<span class="value">{{ s.value }}{{ s.unit }}</span>
					<a @click="publishNewValue(key, s.value+1)">
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
					<svg-icon class="icon" type="mdi" :path="mdiThermometer"></svg-icon> <span>Status</span>
				</a>
			</li>
			<li>
				<a @click="isSetting = true" :class="{ 'active': isSetting }">
					<svg-icon class="icon" type="mdi" :path="mdiCog"></svg-icon> <span>Settings</span>
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

.tabs .icon {
	margin-right: 0.25rem;
}

.tabs ul li a {
	padding: 0 18px 0 15px;
	height: 50px;
	line-height: 50px;
}

.tabs ul li a.active {
	background-color: var(--black-highlight);
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

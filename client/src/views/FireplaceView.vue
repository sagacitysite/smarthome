<script setup lang="ts">
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiThermometer, mdiCog, mdiPlus, mdiMinus } from '@mdi/js';
import { ref, onMounted } from 'vue'
//import * as mqtt from 'mqtt';
import * as mqtt from 'mqtt/dist/mqtt.min'

import { Fireplace } from '../drawings/fireplace';

const settings = [
	{ 'key': 't_relais_on', 'label': 'Relay ON', 'value': 40, 'unit': '°' },
	{ 'key': 't_relais_off', 'label': 'Relay OFF', 'value': 70, 'unit': '°' },
	{ 'key': 't_air_intake_close_half', 'label': 'Half close air intake', 'value': 35, 'unit': '°' },
	{ 'key': 't_air_intake_close', 'label': 'Full close air intake', 'value': 45, 'unit': '°' },
	{ 'key': 't_air_intake_open', 'label': 'Open air intake', 'value': 65, 'unit': '°' },
	{ 'key': 'air_intake_opening_at_full_burn', 'label': 'Opening at full close', 'value': 0, 'unit': '%' }
]

// TODO get values from nodejs server
// Rather use mqtt instead of http? just for the case that another interface changes values?

let isSetting = ref(false);

// Get canvas element from DOM
const canvas = ref('canvas');

onMounted(async () => {
	const fireplace = new Fireplace(canvas.value);
	await fireplace.build();

	/*fireplace.setTemperatureFireplace(50);
	fireplace.setTemperatureTankAbove(70);
	fireplace.setTemperatureTankBelow(30);

	setTimeout(() => {
		fireplace.isHeating();
	}, 2000);

	setTimeout(() => {
		fireplace.startPump();
	}, 6000);*/

	// Init mqtt
	const options = {
		keepalive: 60,
		clientId: 'screen'
	}
	let client = mqtt.connect('ws://192.168.1.74:9001', options);

	client.on("connect", () => {
		client.subscribe("temperature/fireplace", (err) => {
			if (!err) {
				console.log('subscribed');
			}
		});
	});

	client.on("message", (topic, message) => {
		console.log(topic);
		console.log(message);
		console.log(message.toString());
		if (topic == 'temperature/fireplace') {
			fireplace.setTemperatureFireplace(message.toString())
		}
		if (topic == 'temperature/tank_top') {
			fireplace.setTemperatureTankTop(message.toString())
		}
		if (topic == 'temperature/tank_bottom') {
			fireplace.setTemperatureTankBottom(message.toString())
		}
		if (topic == 'temperature/room') {
			// TODO
		}
		if (topic == 'servo/fireplace') {
			// TODO
		}
		if (topic == 'pump/fireplace') {
			// TODO
		}
		//client.end();
	});
});

</script>

<template>
	<div class="window">
		<section class="status" v-show="!isSetting">
			<canvas id="canvas" ref="canvas" resize></canvas>
		</section>
		<section class="setting" v-show="isSetting">
			<div class="setting-row" v-for="s in settings">
				<a @click="">
					<svg-icon class="icon" type="mdi" :path="mdiMinus"></svg-icon>
				</a>
				<span class="value">{{ s.value }}{{ s.unit }}</span>
				<a @click="">
					<svg-icon class="icon" type="mdi" :path="mdiPlus"></svg-icon>
				</a>
				<span class="label">{{ s.label }}</span>
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

.setting {
	padding: 30px;
}

.setting-row {
	display: flex;
	margin-bottom: 10px;
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
</style>

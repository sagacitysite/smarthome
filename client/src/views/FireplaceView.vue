<script setup lang="ts">
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiThermometer, mdiCog } from '@mdi/js';
import { ref, onMounted } from 'vue'
//import * as mqtt from 'mqtt';
import * as mqtt from 'mqtt/dist/mqtt.min'

import { Fireplace } from '../drawings/fireplace';

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
		<section class="setting" v-show="isSetting">Setting</section>
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

.icon {
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
	display: flex;
	align-items: center;
	cursor: pointer;
	font-size: 16px;
	line-height: 50px;
	padding: 0 18px 0 15px;
	margin: 0 5px;
	border-radius: 5px;
}

.tabs ul li a.active {
	background-color: var(--black-highlight);
}
</style>

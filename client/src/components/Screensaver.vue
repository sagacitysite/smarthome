<script setup lang="ts">
import { ref, onBeforeUnmount } from 'vue';

import SvgIcon from '@jamescoyle/vue-icon';
import { mdiFire, mdiWaterBoiler, mdiHeatingCoil } from '@mdi/js';

import { getClockTime } from '../services/time';

import { onMessage } from '../services/mqtt';

let time = ref('');
let fireplaceTemperature = ref('00');
let tankTemperatureTop = ref('00');
let tankTemperatureBottom = ref('00');
let floorHeatingTemperature = ref('00');

const clock = setInterval(() => {
	time.value = getClockTime();
}, 5000);

onBeforeUnmount(() => {
	clearInterval(clock);
});

onMessage('fireplace/temperature', (temp) => {
	fireplaceTemperature.value = temp;
});

onMessage('buffertank/temperature/top', (temp) => {
	tankTemperatureTop.value = temp;
});

onMessage('buffertank/temperature/bottom', (temp) => {
	tankTemperatureBottom.value = temp;
});

</script>

<template>
<div class="wrapper">
	<div>
		<div class="time">{{ time }}</div>
		<div class="fireplace-temperature">
			<svg-icon class="icon" type="mdi" :path="mdiFire"></svg-icon>
			<span>{{ fireplaceTemperature }}°</span>
			&nbsp;
			<svg-icon class="icon" type="mdi" :path="mdiWaterBoiler"></svg-icon>
			<span>{{ tankTemperatureTop }}°</span>/<span>{{ tankTemperatureBottom }}°</span>
			&nbsp;
			<svg-icon class="icon" type="mdi" :path="mdiHeatingCoil"></svg-icon>
			<span>{{ floorHeatingTemperature }}°</span>
		</div>
	</div>
</div>
</template>

<style scoped>
.wrapper {
	display: flex;
	height: 100%;
	width: 100%;
	justify-content: center;
	align-items: center;
}

.time {
	color: var(--white);
	font-size: 100px;
	font-weight: 100;
	line-height: 1;
}

.fireplace-temperature {
	text-align: center;
	margin-top: 15px;
	font-size: 20px;
	color: var(--grey-500);
	line-height: 1;
}

.icon {
	color: var(--grey-500);
}
</style>

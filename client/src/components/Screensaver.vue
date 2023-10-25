<script setup lang="ts">
import { ref, onBeforeUnmount } from 'vue';

import { getClockTime } from '../services/time';

let time = ref('');

const clock = setInterval(() => {
	time.value = getClockTime();
}, 5000);

onBeforeUnmount(() => {
	clearInterval(clock);
});

</script>

<template>
<div class="wrapper">
	<div class="time">{{ time }}</div>
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
	font-size: 100px;
	line-height: 1;
}
</style>

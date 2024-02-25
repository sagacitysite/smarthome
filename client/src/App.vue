<script setup lang="ts">
import { RouterView } from 'vue-router';
import Menu from './components/menu/Menu.vue';
import Screensaver from './components/Screensaver.vue';
import { startMqttClient } from './services/mqtt';
import { ref, onMounted, onBeforeUnmount } from 'vue';

// Start mqtt client
startMqttClient();

let showScreensaver = ref(false);
let timer;

function startTimer() {
	timer = setTimeout(() => {
		showScreensaver.value = true;
	//}, 3*60*1000)
	}, 5*1000)
}

startTimer();

function onClickPage(event) {
	clearTimeout(timer);
	startTimer();
}

onMounted(() => {
	document.addEventListener('click', onClickPage);
});

onBeforeUnmount(() => {
	document.removeEventListener('click', onClickPage);
});
</script>

<template>
	<main>
		<router-view v-slot="{ Component }">
			<keep-alive include="FireplaceView">
				<component :is="Component" />
			</keep-alive>
		</router-view>
	</main>

	<div id="menu">
		<Menu />
	</div>

	<div id="screensaver" v-show="showScreensaver" @click="showScreensaver = false;">
		<Screensaver />
	</div>
</template>

<style scoped>
main {
	width: 80%;
}

#menu {
	width: 20%;
}

#screensaver {
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	background-color: var(--black);
}
</style>

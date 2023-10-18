<script setup lang="ts">
import { RouterView } from 'vue-router';
import Menu from './components/menu/Menu.vue';
import { startMqttClient } from './services/mqtt';

// Start mqtt client
startMqttClient();

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
</template>

<style scoped>
main {
	width: 80%;
}

#menu {
	width: 20%;
}
</style>

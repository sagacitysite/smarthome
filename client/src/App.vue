<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router';
import Menu from './components/Menu.vue';
</script>

<template>
	<main>
		<RouterView />
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

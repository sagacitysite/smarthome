<script setup lang="ts">
import MenuItem from './MenuItem.vue';
import { mdiFire, mdiLightbulb } from '@mdi/js';

const menuItems = [
	{ label: 'Fireplace', route: '/', icon: mdiFire },
	{ label: 'Lamps', route: '/lamps', icon: mdiLightbulb }
];
</script>

<template>
	<nav>
		<MenuItem v-for="li in menuItems" :label="li.label" :route="li.route" :icon="li.icon"></MenuItem>
	</nav>
</template>

<style scoped>
nav {
	background-color: var(--black-soft);
	padding: 20px 0;
	height: 100vh;
}
</style>

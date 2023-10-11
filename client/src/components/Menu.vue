<script setup lang="ts">
import MenuItem from './MenuItem.vue';
</script>

<template>
	<nav>
		<MenuItem :label="'Fireplace'" :iconFile="'thermometer.svg'"></MenuItem>
		<MenuItem :label="'Switches'" :iconFile="'switch.svg'" :isActive="true"></MenuItem>
		<MenuItem :label="'Weather'" :iconFile="'sun.svg'"></MenuItem>
	</nav>
</template>

<style scoped>
nav {
	background-color: var(--vt-c-black-soft);
	padding: 20px 0;
	height: 100vh;
}
</style>

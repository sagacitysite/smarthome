<script setup lang="ts">
import Lamp from '../components/Lamp.vue';
</script>

<template>
	<div class="item">
		<Lamp :name="'Lamp 1'" />
	</div>
	<div class="item">
		<Lamp :name="'Lamp 2'" />
	</div>
	<div class="item">
		<Lamp :name="'Lamp 3'" />
	</div>
	<div class="item">
		<Lamp :name="'Lamp 4'" />
	</div>
</template>

<style scoped>

</style>

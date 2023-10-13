<script setup lang="ts">
import Lamp from '../components/Lamp.vue';
</script>

<template>
	<div class="window">
		<div class="item">
			<Lamp :name="'Garden'" />
		</div>
		<div class="item">
			<Lamp :name="'Corner'" />
		</div>
		<div class="item">
			<Lamp :name="'Stable'" />
		</div>
		<div class="item">
			<Lamp :name="'Lamp 4'" />
		</div>
	</div>
</template>

<style scoped>
.window {
	display: flex;
	flex-wrap: wrap;
	height: 100vh;
}
.item {
	width: 50%;
	flex: 1 0 auto;
	display: flex;
	justify-content: center;
	align-items: center;
}
</style>

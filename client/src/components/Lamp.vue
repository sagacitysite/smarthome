<script setup lang="ts">
const props = defineProps<{
	name: string
}>();

console.log(props.name);
</script>

<template>
	<div>
		<img src="../assets/icons/lightbulb-off.svg" />
		<p>{{ name }}</p>
	</div>
</template>

<style scoped>
</style>

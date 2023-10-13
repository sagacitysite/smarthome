<script setup lang="ts">
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiLightbulb, mdiLightbulbOn } from '@mdi/js';

const props = defineProps<{
	name: string
}>();
</script>

<template>
	<div>
		<svg-icon class="icon" type="mdi" :path="mdiLightbulb"></svg-icon>
		<p>{{ name }}</p>
	</div>
</template>

<style scoped>
p {
	text-align: center;
}

.icon {
	height: 80px;
	width: 80px;
}
</style>

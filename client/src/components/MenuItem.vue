<script setup lang="ts">
export interface Props {
	iconFile: string
	label: string
	isActive?: boolean
};

const props = withDefaults(defineProps<Props>(), {
	isActive: false
});
</script>

<template>
	<div class="item" :class="{ active: isActive }">
		<img :src="'src/assets/icons/'+iconFile" /> <span>{{ label }}</span>
	</div>
</template>

<style scoped>
.item {
	display: flex;
	align-items: center;
	height: 50px;
	margin: 5px 10px;
	padding: 0 5px;
	border-radius: 5px;
}

.item.active {
	background-color: #444;
}

.item img {
	height: 30px;
	padding: 5px;
}
</style>

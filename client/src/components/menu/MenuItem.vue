<script setup lang="ts">
import SvgIcon from '@jamescoyle/vue-icon';

export interface Props {
	icon: string
	label: string
	route: string
};

const props = defineProps<Props>();
</script>

<template>
	<div>
		<router-link class="item" :to="route">
			<svg-icon class="icon" type="mdi" :path="icon"></svg-icon>
			<span>{{ label }}</span>
		</router-link>
	</div>
</template>

<style scoped>
.item {
	display: flex;
	font-size: 16px;
	align-items: center;
	height: 50px;
	margin: 5px 10px;
	padding: 0 5px;
	border-radius: 5px;
}

.item.router-link-active {
	background-color: var(--black-highlight);
}

.item .icon {
	margin-right: 0.25rem;
}
</style>

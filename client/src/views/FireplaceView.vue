<script setup lang="ts">
import SvgIcon from '@jamescoyle/vue-icon';
//import { Project, Shape } from 'paper';
import * as paper from 'paper';
import { mdiThermometer, mdiCog } from '@mdi/js';
import { ref, onMounted } from 'vue'

let isSetting = ref(false);

function importSVGAsync(path) {
	return new Promise(function(resolve, reject) {
		paper.project.importSVG(path, function(icon) {
			resolve(icon);
		});
	});
}

// Get canvas element from DOM
const canvas = ref('canvas');
onMounted(async () => {
	drawCanvas(canvas.value);
});

// Draw fireplace and buffertank
async function drawCanvas(canvas) {
	// Setup paper
	paper.setup(canvas);

	// Shorthand for canvas center
	const ct = paper.view.center;

	const textStyle = {
		fontSize: 25,
		fontFamily: 'Roboto',
		fontWeight: 400,
		fillColor: '#fff'
	};

	// Draw fireplace
	const fp = { w: 120, h: 180 }
	const fireplaceOuter = new paper.Path.Rectangle({
		point: [ct.x-fp.w/2-150, ct.y-fp.h/2],
		size: [fp.w, fp.h],
		fillColor: '#080808',
		strokeColor: '#222222',
		strokeWidth: 5
	});
	const fpIn = { w: 90, h: 90 }
	const fireplaceInner = new paper.Path.Rectangle({
		point: [ct.x-fpIn.w/2-150, ct.y-fpIn.h/2],
		size: [fpIn.w, fpIn.h],
		fillColor: '#100b08', //'#040404',
		strokeColor: '#222222',
		strokeWidth: 2
	});
	// Icon path
	const firePath = 'fire.svg';
	const fire = await importSVGAsync(firePath);
	fire.scale(2.5);
	fire.position = new paper.Point(ct.x-150, ct.y+10);
	// Temperature fireplace
	const tempFireplace = new paper.PointText({
		point: [ct.x-150-15, ct.y-60],
		content: '30°',
		style: textStyle
	});

	// Draw watertank
	const wt = { w: 100, h: 200 }
	new paper.Path.Rectangle({
		point: [ct.x-wt.w/2+150, ct.y-110],
		size: [wt.w, wt.h],
		fillColor: '#080808',
		strokeColor: '#222222',
		strokeWidth: 5
	});
	// Temperature watertank above
	const tempWaterUp = new paper.PointText({
		point: [ct.x+150-15, ct.y-60-5],
		content: '68°',
		style: textStyle
	});
	// Temperature watertank below
	const tempWaterBelow = new paper.PointText({
		point: [ct.x+150-15, ct.y+60],
		content: '34°',
		style: textStyle
	});

	// Draw flow and return connection
	new paper.Path.Line({
		from: [ct.x+fp.w/2-150, ct.y-fp.h/2+20],
		to: [ct.x-wt.w/2+150, ct.y-fp.h/2+20],
		strokeColor: '#222222',
		strokeWidth: 3
	});
	new paper.Path.Line({
		from: [ct.x+fp.w/2-150, ct.y+fp.h/2-20],
		to: [ct.x-wt.w/2+150, ct.y+fp.h/2-20],
		strokeColor: '#222222',
		strokeWidth: 3
	});
	new paper.Path.Line({
		from: [ct.x, ct.y-fp.h/2+20],
		to: [ct.x, ct.y+fp.h/2-20],
		strokeColor: '#222222',
		strokeWidth: 3
	});

	// Draw pump
	new paper.Path.Circle({
		center: [ct.x, ct.y+fp.h/2-20],
		radius: 20,
		fillColor: '#222222'
	});

	// Icon path
	const pumpPath = 'reload.svg';
	const pump = await importSVGAsync(pumpPath);
	pump.position = new paper.Point(ct.x, ct.y+fp.h/2-20);
	paper.view.onFrame = function(event) {
		pump.rotate(2);
	}
	pump.visible = true;
	
}

</script>

<template>
	<div class="window">
		<section class="status" v-show="!isSetting">
			<canvas id="canvas" ref="canvas" resize></canvas>
		</section>
		<section class="setting" v-show="isSetting">Setting</section>
	</div>
	<div class="tabs">
		<ul>
			<li>
				<a @click="isSetting = false" :class="{ 'active': !isSetting }">
					<svg-icon class="icon" type="mdi" :path="mdiThermometer"></svg-icon> <span>Status</span>
				</a>
			</li>
			<li>
				<a @click="isSetting = true" :class="{ 'active': isSetting }">
					<svg-icon class="icon" type="mdi" :path="mdiCog"></svg-icon> <span>Settings</span>
				</a>
			</li>
		</ul>
	</div>
</template>

<style scoped>
#canvas {
	width: 100%;
	height: 80vh;
}

.icon {
	margin-right: 0.25rem;
}

.window {
	height: 80vh;
}

.tabs {
	height: 20vh;
	padding-top: 10px;
}

.tabs ul {
	list-style: none;
	padding: 0;
	display: flex;
	align-items: center;
	justify-content: center;
}

.tabs ul li a {
	display: flex;
	align-items: center;
	cursor: pointer;
	font-size: 16px;
	line-height: 50px;
	padding: 0 18px 0 15px;
	margin: 0 5px;
	border-radius: 5px;
}

.tabs ul li a.active {
	background-color: var(--black-highlight);
}
</style>

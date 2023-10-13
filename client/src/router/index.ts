import { createRouter, createWebHistory } from 'vue-router';
import FireplaceView from '../views/FireplaceView.vue';
import LampsView from '../views/LampsView.vue';

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		{
			path: '/',
			name: 'fireplace',
			component: FireplaceView
		},
		{
			path: '/lamps',
			name: 'lamps',
			component: LampsView
		}
		/*,
		{
		path: '/about',
		name: 'about',
		// route level code-splitting
		// this generates a separate chunk (About.[hash].js) for this route
		// which is lazy-loaded when the route is visited.
		component: () => import('../views/AboutView.vue')
		}*/
	]
});

export default router;

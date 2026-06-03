import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import TemplatesView from '../views/TemplatesView.vue'
import SettingsView from '../views/SettingsView.vue'
import StatsView from '../views/StatsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: DashboardView },
    { path: '/templates', name: 'templates', component: TemplatesView },
    { path: '/settings', name: 'settings', component: SettingsView },
    { path: '/stats', name: 'stats', component: StatsView },
  ],
})

export default router

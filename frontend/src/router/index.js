import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import TemplatesView from '../views/TemplatesView.vue'
import SettingsView from '../views/SettingsView.vue'
import StatsView from '../views/StatsView.vue'
import AuthView from '../views/AuthView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/auth', name: 'auth', component: AuthView },
    { path: '/', name: 'dashboard', component: DashboardView },
    { path: '/templates', name: 'templates', component: TemplatesView },
    { path: '/settings', name: 'settings', component: SettingsView },
    { path: '/stats', name: 'stats', component: StatsView },
  ],
})

router.beforeEach((to, from, next) => {
  const authenticated = sessionStorage.getItem('nexo_authenticated') === '1'
  if (to.name !== 'auth' && !authenticated) {
    next({ name: 'auth' })
  } else {
    next()
  }
})

export default router

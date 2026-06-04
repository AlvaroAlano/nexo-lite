<template>
  <div
    class="fixed inset-x-0 z-40 flex justify-center px-4"
    style="bottom: calc(env(safe-area-inset-bottom, 0px) + 1rem)"
  >
    <nav
      class="bg-brand-canvas-soft-light/95 dark:bg-brand-canvas-soft-dark/95 backdrop-blur-xl border border-brand-hairline-light dark:border-brand-hairline-dark rounded-full flex items-center p-1.5 shadow-[0_8px_24px_rgba(0,0,0,0.10),0_2px_6px_rgba(0,0,0,0.06)] gap-0.5 transition-colors duration-150"
    >
      <template v-for="(item, i) in allItems" :key="i">
        <!-- FAB — hidden on stats, context-aware action -->
        <Transition v-if="item.type === 'fab'" name="fab-pop">
          <button
            v-if="route.name !== 'stats'"
            @click="openAdd"
            class="w-10 h-10 mx-0.5 bg-brand-primary hover:bg-brand-primary-hover rounded-full flex items-center justify-center transition-all duration-200 active:scale-90 flex-shrink-0"
            :aria-label="fabLabel"
          >
            <Plus class="text-white" :size="20" stroke-width="2.5" />
          </button>
        </Transition>

        <!-- Route tab -->
        <button
          v-if="item.type === 'route'"
          @click="router.push(item.to)"
          class="flex items-center rounded-full px-3 py-2 transition-colors duration-200 min-w-[44px] justify-center active:opacity-60"
          :class="route.name === item.name
            ? 'bg-brand-primary/[0.10] dark:bg-brand-primary/[0.18] text-brand-primary dark:text-brand-primary-soft'
            : 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:text-brand-ink-light dark:hover:text-white'"
          :aria-label="item.label"
        >
          <component :is="item.icon" :size="21" stroke-width="2" class="flex-shrink-0" />
          <span
            class="overflow-hidden whitespace-nowrap text-[10px] font-semibold"
            :style="labelStyle(item.name)"
          >{{ item.label }}</span>
        </button>
      </template>
    </nav>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Home, Repeat2, Settings, BarChart2, Plus } from 'lucide-vue-next'
import { useDashboardStore } from '../../stores/dashboard.js'

const route = useRoute()
const router = useRouter()
const store = useDashboardStore()

const fabLabel = computed(() => {
  if (route.name === 'templates') return 'Adicionar recorrência'
  if (route.name === 'settings')  return 'Adicionar categoria'
  return 'Adicionar despesa'
})

const allItems = [
  { type: 'route', to: '/',          name: 'dashboard', icon: Home,      label: 'Check-in'     },
  { type: 'route', to: '/templates', name: 'templates', icon: Repeat2,   label: 'Recorrências' },
  { type: 'fab' },
  { type: 'route', to: '/settings',  name: 'settings',  icon: Settings,  label: 'Ajustes'      },
  { type: 'route', to: '/stats',     name: 'stats',     icon: BarChart2, label: 'Estatísticas' },
]

function labelStyle(name) {
  const active = route.name === name
  return {
    maxWidth: active ? '64px' : '0px',
    opacity: active ? '1' : '0',
    paddingLeft: active ? '6px' : '0px',
    transition:
      'max-width 320ms cubic-bezier(0.34,1.56,0.64,1), opacity 180ms ease, padding-left 200ms ease',
  }
}

async function openAdd() {
  if (route.name === 'templates') {
    store.quickAddTemplateOpen = true
    return
  }
  if (route.name === 'settings') {
    store.quickAddCategoryOpen = true
    return
  }
  if (route.name !== 'dashboard') {
    await router.push('/')
  }
  store.quickAddOpen = true
}
</script>

<style scoped>
.fab-pop-enter-active { animation: fab-in 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) forwards; }
.fab-pop-leave-active { animation: fab-in 0.15s ease-in reverse forwards; }
@keyframes fab-in {
  from { opacity: 0; transform: scale(0.4); }
  to   { opacity: 1; transform: scale(1); }
}
</style>

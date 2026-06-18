<template>
  <Transition
    enter-active-class="transition-[opacity,transform] duration-300 ease-out"
    leave-active-class="transition-[opacity,transform] duration-200 ease-in"
    enter-from-class="opacity-0 translate-y-3"
    leave-to-class="opacity-0 translate-y-2"
  >
  <div
    v-show="!isModalOpen"
    class="absolute bottom-3 left-1/2 -translate-x-1/2 z-[9999] w-max pointer-events-none md:hidden"
    style="padding-bottom: env(safe-area-inset-bottom, 0px);"
  >
    <!-- FAB speed-dial options (dashboard only) -->
    <Transition name="speed-dial">
      <div
        v-if="store.fabMenuOpen && route.name === 'dashboard'"
        class="pointer-events-auto flex flex-col items-center gap-2 mb-3"
      >
        <button
          @click="openLoan"
          class="flex items-center gap-2.5 bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-full pl-3.5 pr-5 py-2.5 shadow-lg text-sm font-semibold text-brand-ink-light dark:text-white hover:border-brand-primary/40 active:scale-95 transition-all"
        >
          <span class="w-6 h-6 rounded-full bg-emerald-500/15 flex items-center justify-center flex-shrink-0">
            <Handshake :size="13" class="text-emerald-600 dark:text-emerald-400" />
          </span>
          Registrar Empréstimo
        </button>
        <button
          @click="openExpense"
          class="flex items-center gap-2.5 bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-full pl-3.5 pr-5 py-2.5 shadow-lg text-sm font-semibold text-brand-ink-light dark:text-white hover:border-brand-primary/40 active:scale-95 transition-all"
        >
          <span class="w-6 h-6 rounded-full bg-brand-primary/10 flex items-center justify-center flex-shrink-0">
            <Receipt :size="13" class="text-brand-primary" />
          </span>
          Nova Despesa
        </button>
      </div>
    </Transition>

    <nav class="pointer-events-auto bg-brand-canvas-soft-light/95 dark:bg-brand-canvas-soft-dark/95 backdrop-blur-xl border border-brand-hairline-light dark:border-brand-hairline-dark rounded-full flex items-center p-2 shadow-[0_8px_24px_rgba(0,0,0,0.10),0_2px_6px_rgba(0,0,0,0.06)] gap-0.5">
        <template v-for="(item, i) in allItems" :key="i">

          <div
            v-if="item.type === 'fab'"
            class="flex items-center justify-center transition-all duration-300 ease-in-out overflow-hidden"
            :class="route.name !== 'stats' && route.name !== 'settings' ? 'w-12 mx-0.5' : 'w-0 mx-0'"
          >
            <Transition name="fab-pop">
              <button
                v-if="route.name !== 'stats' && route.name !== 'settings'"
                @click="openAdd"
                class="w-11 h-11 rounded-full flex items-center justify-center transition-all duration-200 active:scale-90 flex-shrink-0"
                :class="store.fabMenuOpen && route.name === 'dashboard'
                  ? 'bg-brand-ink-light dark:bg-white'
                  : 'bg-brand-primary hover:bg-brand-primary-hover'"
                :aria-label="fabLabel"
              >
                <X v-if="store.fabMenuOpen && route.name === 'dashboard'" class="text-white dark:text-brand-canvas-dark" :size="18" stroke-width="2.5" />
                <Plus v-else class="text-white" :size="20" stroke-width="2.5" />
              </button>
            </Transition>
          </div>

          <button
            v-if="item.type === 'route'"
            @click="router.push(item.to)"
            class="flex items-center rounded-full px-3.5 py-2.5 transition-colors duration-200 min-w-[48px] justify-center active:opacity-60"
            :class="route.name === item.name
              ? 'bg-brand-primary/[0.10] dark:bg-brand-primary/[0.18] text-brand-primary dark:text-brand-primary-soft'
              : 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:text-brand-ink-light dark:hover:text-white'"
            :aria-label="item.label"
          >
            <component :is="item.icon" :size="22" stroke-width="2" class="flex-shrink-0" />
            <span
              class="overflow-hidden whitespace-nowrap text-[10px] font-semibold"
              :style="labelStyle(item.name)"
            >{{ item.label }}</span>
          </button>

        </template>
    </nav>
  </div>
  </Transition>

  <!-- Backdrop for speed-dial -->
  <div
    v-if="store.fabMenuOpen && route.name === 'dashboard'"
    class="fixed inset-0 z-[9998] md:hidden"
    @click="store.fabMenuOpen = false"
  />
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Home, Repeat2, Settings, BarChart2, Plus, X, Handshake, Receipt } from 'lucide-vue-next'
import { useDashboardStore } from '../../stores/dashboard.js'
import { useDebtsStore } from '../../stores/debts.js'

const isModalOpen = ref(false)
let _observer

onMounted(() => {
  _observer = new MutationObserver(() => {
    isModalOpen.value = document.body.classList.contains('overflow-hidden')
    if (isModalOpen.value) store.fabMenuOpen = false
  })
  _observer.observe(document.body, { attributes: true, attributeFilter: ['class'] })
})
onUnmounted(() => _observer?.disconnect())

const route = useRoute()
const router = useRouter()
const store = useDashboardStore()
const debtsStore = useDebtsStore()

const fabLabel = computed(() => {
  if (route.name === 'templates') return 'Adicionar recorrência'
  return 'Adicionar'
})

const allItems = [
  { type: 'route', to: '/',          name: 'dashboard', icon: Home,      label: 'Check-in'     },
  { type: 'route', to: '/stats',     name: 'stats',     icon: BarChart2, label: 'Estatísticas' },
  { type: 'fab' },
  { type: 'route', to: '/templates', name: 'templates', icon: Repeat2,   label: 'Recorrências' },
  { type: 'route', to: '/settings',  name: 'settings',  icon: Settings,  label: 'Ajustes'      },
]

function labelStyle(name) {
  const active = route.name === name
  return {
    maxWidth: active ? '64px' : '0px',
    opacity: active ? '1' : '0',
    paddingLeft: active ? '6px' : '0px',
    transition:
      'max-width 320ms var(--ease-spring), opacity 180ms ease, padding-left 200ms ease',
  }
}

async function openAdd() {
  if (route.name === 'templates') {
    store.quickAddTemplateOpen = true
    return
  }
  if (route.name === 'dashboard') {
    store.fabMenuOpen = !store.fabMenuOpen
    return
  }
  await router.push('/')
  store.quickAddOpen = true
}

async function openExpense() {
  store.fabMenuOpen = false
  store.quickAddOpen = true
}

async function openLoan() {
  store.fabMenuOpen = false
  debtsStore.openLoanModal()
}
</script>

<style scoped>
.fab-pop-enter-active { animation: fab-in 0.3s var(--ease-spring) forwards; }
.fab-pop-leave-active { animation: fab-in 0.15s ease-in reverse forwards; }
@keyframes fab-in {
  from { opacity: 0; transform: scale(0.4); }
  to   { opacity: 1; transform: scale(1); }
}

.speed-dial-enter-active {
  animation: speed-dial-in 0.2s var(--ease-spring) forwards;
}
.speed-dial-leave-active {
  animation: speed-dial-in 0.12s ease-in reverse forwards;
}
@keyframes speed-dial-in {
  from { opacity: 0; transform: translateY(8px) scale(0.95); }
  to   { opacity: 1; transform: translateY(0)  scale(1); }
}
</style>

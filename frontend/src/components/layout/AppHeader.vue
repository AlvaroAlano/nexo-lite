<template>
  <header
    class="sticky top-0 z-30 bg-white/90 dark:bg-brand-canvas-dark/90 backdrop-blur-md border-b border-brand-hairline-light dark:border-brand-hairline-dark transition-colors duration-150"
    style="padding-top: env(safe-area-inset-top, 0px);"
  >
    <div class="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between gap-3">
      <!-- Logo (desktop) -->
      <RouterLink to="/" class="hidden md:flex items-center gap-2 flex-shrink-0">
        <div class="w-7 h-7 rounded-lg bg-brand-ink-light dark:bg-white flex items-center justify-center">
          <span class="text-white dark:text-brand-canvas-dark text-xs font-bold tracking-tight">N</span>
        </div>
        <span class="font-semibold text-brand-ink-light dark:text-white text-sm tracking-tight">Nexo</span>
      </RouterLink>

      <!-- Logo (mobile) -->
      <RouterLink to="/" class="flex md:hidden items-center flex-shrink-0">
        <div class="w-7 h-7 rounded-lg bg-brand-ink-light dark:bg-white flex items-center justify-center">
          <span class="text-white dark:text-brand-canvas-dark text-xs font-bold tracking-tight">N</span>
        </div>
      </RouterLink>

      <!-- Month navigation — center piece -->
      <div class="flex items-center gap-1 flex-1 justify-center md:justify-start md:flex-none">
        <button
          @click="navigate(-1)"
          :disabled="store.loading"
          class="w-8 h-8 flex items-center justify-center rounded-lg text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark disabled:opacity-30 transition-colors active:scale-90"
          aria-label="Mês anterior"
        >
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
        </button>
 
        <button
          @click="goToCurrent"
          class="px-3 py-1.5 rounded-lg font-semibold text-sm text-brand-ink-light dark:text-white hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark transition-colors min-w-[140px] text-center"
          :class="store.isReadOnly ? 'opacity-70' : ''"
        >
          {{ displayLabel }}
          <span v-if="store.isReadOnly" class="ml-1 text-[10px] font-normal text-brand-ink-mute-light dark:text-brand-ink-mute-dark">fechado</span>
        </button>
 
        <button
          @click="navigate(+1)"
          :disabled="store.loading"
          class="w-8 h-8 flex items-center justify-center rounded-lg text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark disabled:opacity-30 transition-colors active:scale-90"
          aria-label="Próximo mês"
        >
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </button>
      </div>

      <!-- Nav (desktop) + theme toggle + saving indicator -->
      <div class="flex items-center gap-2 flex-shrink-0">
        <nav class="hidden md:flex items-center gap-1">
          <RouterLink
            to="/"
            class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
            :class="$route.name === 'dashboard'
              ? 'bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark text-brand-ink-light dark:text-white'
              : 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:text-brand-ink-light dark:hover:text-white hover:bg-brand-canvas-soft-light/50 dark:hover:bg-brand-canvas-soft-dark/50'"
          >
            Check-in
          </RouterLink>
          <RouterLink
            to="/stats"
            class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
            :class="$route.name === 'stats'
              ? 'bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark text-brand-ink-light dark:text-white'
              : 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:text-brand-ink-light dark:hover:text-white hover:bg-brand-canvas-soft-light/50 dark:hover:bg-brand-canvas-soft-dark/50'"
          >
            Estatísticas
          </RouterLink>
          <RouterLink
            to="/templates"
            class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
            :class="$route.name === 'templates'
              ? 'bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark text-brand-ink-light dark:text-white'
              : 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:text-brand-ink-light dark:hover:text-white hover:bg-brand-canvas-soft-light/50 dark:hover:bg-brand-canvas-soft-dark/50'"
          >
            Recorrências
          </RouterLink>
          <RouterLink
            to="/settings"
            class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
            :class="$route.name === 'settings'
              ? 'bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark text-brand-ink-light dark:text-white'
              : 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:text-brand-ink-light dark:hover:text-white hover:bg-brand-canvas-soft-light/50 dark:hover:bg-brand-canvas-soft-dark/50'"
          >
            Ajustes
          </RouterLink>
        </nav>

        <!-- Add expense shortcut (desktop, dashboard only) -->
        <button
          v-if="$route.name === 'dashboard' && !store.isReadOnly"
          @click="store.quickAddOpen = true"
          class="hidden md:flex w-8 h-8 items-center justify-center rounded-lg bg-brand-primary text-white hover:bg-brand-primary-hover active:scale-95 transition-all"
          title="Adicionar despesa"
          aria-label="Adicionar despesa"
        >
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
        </button>

        <!-- Privacy mode toggle -->
        <button
          @click="togglePrivacy"
          class="w-8 h-8 flex items-center justify-center rounded-lg transition-colors active:scale-95"
          :class="isPrivate
            ? 'text-amber-500 bg-amber-500/10 hover:bg-amber-500/20'
            : 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark'"
          :title="isPrivate ? 'Revelar valores' : 'Ocultar valores'"
          :aria-label="isPrivate ? 'Revelar valores' : 'Ocultar valores'"
        >
          <!-- Eye-off icon (values hidden) -->
          <svg v-if="isPrivate" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
            <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
            <line x1="1" y1="1" x2="23" y2="23"/>
          </svg>
          <!-- Eye icon (values visible) -->
          <svg v-else class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
        </button>

        <button
          @click="toggleTheme"
          class="w-8 h-8 flex items-center justify-center rounded-lg text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark transition-colors active:scale-95"
          title="Alternar tema"
          aria-label="Alternar tema"
        >
          <!-- Moon icon (shows when theme is light) -->
          <svg v-if="theme === 'light'" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
          </svg>
          <!-- Sun icon (shows when theme is dark) -->
          <svg v-else class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
          </svg>
        </button>

        <div v-if="store.saving" class="flex items-center gap-1.5 text-brand-ink-mute-light dark:text-brand-ink-mute-dark text-xs ml-1">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <span class="hidden md:inline">Salvando</span>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useDashboardStore } from '../../stores/dashboard.js'
import { usePrivacyMode } from '../../composables/usePrivacyMode.js'
import { monthLabel } from '../../utils/date.js'

const store = useDashboardStore()
const { isPrivate, toggle: togglePrivacy } = usePrivacyMode()

// Local nav state — tracks what month we're displaying
const navYear = ref(null)
const navMonth = ref(null)
const theme = ref(localStorage.getItem('theme') || 'light')

onMounted(() => {
  syncFromPeriod()
  // Ensure the theme in document matches ref
  if (theme.value === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
})

watch(() => store.period, syncFromPeriod)

function syncFromPeriod() {
  if (store.period) {
    navYear.value = store.period.year
    navMonth.value = store.period.month
  }
}

const displayLabel = computed(() => {
  if (navYear.value && navMonth.value) return monthLabel(navYear.value, navMonth.value)
  if (store.period) return monthLabel(store.period.year, store.period.month)
  return '—'
})

async function navigate(direction) {
  let year = navYear.value ?? store.period?.year
  let month = navMonth.value ?? store.period?.month
  if (!year || !month) return

  month += direction
  if (month > 12) { month = 1; year++ }
  if (month < 1) { month = 12; year-- }

  navYear.value = year
  navMonth.value = month

  await store.fetchByMonth(year, month)
}

async function goToCurrent() {
  await store.fetchCurrent()
  syncFromPeriod()
}

function toggleTheme() {
  const nextTheme = theme.value === 'light' ? 'dark' : 'light'
  theme.value = nextTheme
  localStorage.setItem('theme', nextTheme)
  if (nextTheme === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}
</script>

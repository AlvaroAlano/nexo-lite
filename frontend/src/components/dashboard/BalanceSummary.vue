<template>
  <div class="font-ss01">
    <!-- Tab row + collapse toggle -->
    <div class="flex items-center gap-1 mb-3 bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-xl p-1 transition-colors duration-150">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="store.setView(tab.key)"
        class="flex-1 py-2 text-xs font-semibold rounded-lg transition-all"
        :class="store.currentView === tab.key
          ? 'bg-white dark:bg-brand-canvas-dark text-brand-primary dark:text-white shadow-stripe-1'
          : 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:text-brand-ink-light dark:hover:text-white'"
      >
        {{ tab.label }}
      </button>

      <div class="md:hidden w-px h-4 bg-brand-hairline-light dark:bg-brand-hairline-dark mx-0.5 flex-shrink-0" />

      <button
        @click="collapsed = !collapsed"
        class="md:hidden p-1.5 rounded-lg text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:text-brand-ink-light dark:hover:text-white hover:bg-white/60 dark:hover:bg-brand-canvas-dark/40 transition-all flex-shrink-0"
        :title="collapsed ? 'Expandir' : 'Recolher'"
      >
        <ChevronDown
          :size="14"
          class="transition-transform duration-300"
          :class="collapsed ? '' : 'rotate-180'"
        />
      </button>
    </div>

    <!-- Collapsible dark panel (CSS grid trick for smooth height) -->
    <div
      class="balance-collapse-grid grid transition-[grid-template-rows] duration-300 ease-in-out"
      :style="{ gridTemplateRows: collapsed ? '0fr' : '1fr' }"
    >
      <div class="min-h-0 overflow-hidden">
        <div
          class="rounded-stripe-card p-5 text-white bg-brand-canvas-dark dark:bg-brand-canvas-soft-dark/40 border border-brand-hairline-dark/30 dark:border-brand-hairline-dark/60 shadow-stripe-1 overflow-hidden"
        >
          <!-- Read-only banner -->
          <div v-if="store.isReadOnly" class="flex items-center gap-2 mb-4 bg-brand-canvas-soft-dark/30 dark:bg-brand-canvas-dark/40 border border-brand-hairline-dark/20 rounded-lg px-3 py-2">
            <svg class="w-3.5 h-3.5 text-brand-ink-mute-dark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0110 0v4"/>
            </svg>
            <span class="text-brand-ink-mute-dark text-xs">Visualização — Mês Fechado</span>
          </div>

          <!-- Sliding tab content -->
          <div class="tab-content-wrap">
            <Transition :name="tabTransition">
              <div v-if="store.currentView === 'geral'">
                <div class="flex items-center justify-between mb-4">
                  <span class="text-brand-ink-mute-dark text-xs">
                    {{ store.paidCount }}/{{ store.expenses.length }} pagos
                  </span>
                  <div class="flex items-center gap-2">
                    <div class="w-20 h-1.5 bg-zinc-800 dark:bg-zinc-900 rounded-full overflow-hidden">
                      <div class="h-full bg-emerald-500 rounded-full transition-all duration-500" :style="{ width: progressPct + '%' }" />
                    </div>
                    <span class="text-brand-ink-mute-dark text-[10px] font-tabular">{{ progressPct }}%</span>
                  </div>
                </div>

                <div class="space-y-2 mb-3">
                  <IncomeRow label="Álvaro" :value="store.incomeAlvaro" field="income_alvaro" :readonly="store.isReadOnly" />
                  <IncomeRow label="Alexandra" :value="store.incomeAlexandra" field="income_alexandra" :readonly="store.isReadOnly" />
                </div>

                <div v-if="store.carryover > 0" class="flex justify-between mb-2">
                  <span class="text-brand-ink-mute-dark text-sm">Saldo anterior</span>
                  <span class="font-tabular font-medium text-emerald-400 text-sm">+ {{ fmt(store.carryover) }}</span>
                </div>

                <div class="border-t border-brand-hairline-dark/20 my-3" />

                <div class="flex justify-between mb-1">
                  <span class="text-brand-ink-mute-dark text-sm">Comprometido</span>
                  <span class="font-tabular font-medium text-brand-ink-mute-dark text-sm">− {{ fmt(store.totalCommitted) }}</span>
                </div>

                <FreeCashDisplay :value="store.freeCash" label="Livre este mês" />
              </div>

              <div v-else-if="store.currentView === 'alvaro'">
                <IncomeRow label="Renda de Álvaro" :value="store.incomeAlvaro" field="income_alvaro" :readonly="store.isReadOnly" />
                <div class="border-t border-brand-hairline-dark/20 my-3" />
                <div class="flex justify-between mb-1">
                  <span class="text-brand-ink-mute-dark text-sm">Contas de Álvaro</span>
                  <span class="font-tabular font-medium text-brand-ink-mute-dark text-sm">− {{ fmt(alvaroCommitted) }}</span>
                </div>
                <FreeCashDisplay :value="store.saldoAlvaro" label="Saldo de Álvaro" />
              </div>

              <div v-else-if="store.currentView === 'alexandra'">
                <IncomeRow label="Renda de Alexandra" :value="store.incomeAlexandra" field="income_alexandra" :readonly="store.isReadOnly" />
                <div class="border-t border-brand-hairline-dark/20 my-3" />
                <div class="flex justify-between mb-1">
                  <span class="text-brand-ink-mute-dark text-sm">Contas de Alexandra</span>
                  <span class="font-tabular font-medium text-brand-ink-mute-dark text-sm">− {{ fmt(alexandraCommitted) }}</span>
                </div>
                <FreeCashDisplay :value="store.saldoAlexandra" label="Saldo de Alexandra" />
              </div>
            </Transition>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ChevronDown } from 'lucide-vue-next'
import { useDashboardStore } from '../../stores/dashboard.js'
import { formatCurrency } from '../../utils/currency.js'
import IncomeRow from './IncomeRow.vue'
import FreeCashDisplay from './FreeCashDisplay.vue'

const store = useDashboardStore()
const fmt = formatCurrency

const tabs = [
  { key: 'geral', label: 'Visão Geral' },
  { key: 'alvaro', label: 'Álvaro' },
  { key: 'alexandra', label: 'Alexandra' },
]

const collapsed = ref(false)

const viewOrder = { geral: 0, alvaro: 1, alexandra: 2 }
const tabTransition = ref('tab-slide-left')

watch(
  () => store.currentView,
  (to, from) => {
    const toIdx = viewOrder[to] ?? 0
    const fromIdx = viewOrder[from] ?? 0
    tabTransition.value = toIdx >= fromIdx ? 'tab-slide-left' : 'tab-slide-right'
  }
)

const progressPct = computed(() => {
  if (!store.expenses.length) return 0
  return Math.round((store.paidCount / store.expenses.length) * 100)
})

const alvaroCommitted = computed(() =>
  store.expenses
    .filter((e) => e.responsavel === 'alvaro')
    .reduce((sum, e) => sum + (parseFloat(e.amount) || 0), 0)
)

const alexandraCommitted = computed(() =>
  store.expenses
    .filter((e) => e.responsavel === 'alexandra')
    .reduce((sum, e) => sum + (parseFloat(e.amount) || 0), 0)
)
</script>

<style>
/* Desktop: always show balance panel regardless of collapsed state */
@media (min-width: 768px) {
  .balance-collapse-grid {
    display: block !important;
  }
}

/* Tab content: relative container so leaving view exits absolutely */
.tab-content-wrap {
  position: relative;
  overflow: hidden;
}

.tab-slide-left-enter-active,
.tab-slide-left-leave-active,
.tab-slide-right-enter-active,
.tab-slide-right-leave-active {
  transition: opacity 160ms ease, transform 160ms ease;
}

/* Leaving: pull out of flow so entering view sets the correct height */
.tab-slide-left-leave-active,
.tab-slide-right-leave-active {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
}

.tab-slide-left-enter-from  { opacity: 0; transform: translateX(16px); }
.tab-slide-left-leave-to    { opacity: 0; transform: translateX(-16px); }

.tab-slide-right-enter-from { opacity: 0; transform: translateX(-16px); }
.tab-slide-right-leave-to   { opacity: 0; transform: translateX(16px); }
</style>

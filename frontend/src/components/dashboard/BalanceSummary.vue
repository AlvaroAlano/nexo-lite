<template>
  <div class="font-ss01 mb-5">
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
                  <div class="flex items-center gap-2">
                    <span class="text-brand-ink-mute-dark text-xs">
                      {{ store.paidCount }}/{{ store.expenses.length }} pagos
                    </span>
                    <!-- Nota de saúde -->
                    <span
                      v-if="healthConfig"
                      class="text-[10px] font-semibold px-1.5 py-0.5 rounded-md border leading-none"
                      :class="[healthConfig.bgClass, healthConfig.textClass]"
                      :title="healthConfig.label"
                    >{{ healthScore }}</span>
                  </div>
                  <div class="flex items-center gap-2.5">
                    <div class="w-20 h-1.5 bg-zinc-800 dark:bg-zinc-900 rounded-full overflow-hidden">
                      <div class="h-full bg-emerald-500 rounded-full transition-all duration-500" :style="{ width: progressPct + '%' }" />
                    </div>
                    <span class="text-brand-ink-mute-dark text-[10px] font-tabular">{{ progressPct }}%</span>

                    <!-- Épico 2: Auditor IA -->
                    <button
                      @click="analyzeMonth"
                      :disabled="isAnalyzing"
                      class="w-6 h-6 flex items-center justify-center rounded-lg text-brand-ink-mute-dark hover:text-white hover:bg-white/10 disabled:opacity-50 transition-all active:scale-90"
                      title="Auditor IA"
                    >
                      <svg v-if="isAnalyzing" class="w-3.5 h-3.5 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <path d="M21 12a9 9 0 1 1-6.219-8.56" stroke-linecap="round"/>
                      </svg>
                      <Bot v-else :size="14" />
                    </button>
                  </div>
                </div>

                <div class="space-y-2 mb-3">
                  <IncomeRow :label="store.nameAlvaro" :value="store.incomeAlvaro" field="income_alvaro" :readonly="store.isReadOnly" />
                  <IncomeRow :label="store.nameAlexandra" :value="store.incomeAlexandra" field="income_alexandra" :readonly="store.isReadOnly" />
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

                <!-- Caixinha deste mês -->
                <div
                  v-if="store.vaultExpense"
                  class="flex items-center justify-between mt-3 px-1"
                >
                  <div class="flex items-center gap-1.5">
                    <PiggyBank :size="13" class="text-brand-ink-mute-dark flex-shrink-0" />
                    <span class="text-brand-ink-mute-dark text-sm">Caixinha</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="font-tabular text-sm" :class="store.vaultMonthPaid ? 'text-emerald-400' : 'text-brand-ink-mute-dark'">
                      {{ fmt(store.vaultMonthAmount) }}
                    </span>
                    <span
                      v-if="store.vaultMonthPaid"
                      class="text-[10px] text-emerald-500/70 bg-emerald-500/10 rounded-full px-1.5 py-0.5 leading-none"
                    >depositado</span>
                    <span
                      v-else
                      class="text-[10px] text-brand-ink-mute-dark/60 bg-zinc-800 rounded-full px-1.5 py-0.5 leading-none"
                    >pendente</span>
                  </div>
                </div>

                <!-- Missão do mês -->
                <div class="flex items-center justify-between mt-2.5 px-1">
                  <div class="flex items-center gap-1.5">
                    <span class="text-[11px]" :class="goalMet ? 'text-emerald-400' : 'text-brand-ink-mute-dark'">
                      {{ goalMet ? '✓' : '○' }}
                    </span>
                    <span class="text-[11px] text-brand-ink-mute-dark">Meta Caixinha:</span>
                  </div>
                  <div class="flex items-center gap-1.5">
                    <template v-if="!editingGoal">
                      <button
                        @click="startGoalEdit"
                        class="text-[11px] font-tabular hover:text-white transition-colors"
                        :class="goalMet ? 'text-emerald-400' : 'text-brand-ink-mute-dark'"
                        title="Alterar meta"
                      >{{ fmt(monthlyGoal) }}</button>
                    </template>
                    <template v-else>
                      <CurrencyInput
                        v-model="goalEditVal"
                        hide-prefix
                        @confirm="saveGoal"
                        @cancel="editingGoal = false"
                        @blur="saveGoal"
                        input-class="w-20 text-right text-[11px] py-0 px-1 bg-zinc-800 border border-brand-primary/40 rounded text-white font-tabular"
                      />
                    </template>
                    <div v-if="!goalMet && monthlyGoal > 0" class="w-12 h-1 bg-zinc-800 rounded-full overflow-hidden">
                      <div class="h-full bg-emerald-500/60 rounded-full transition-all duration-500" :style="{ width: goalProgress + '%' }" />
                    </div>
                  </div>
                </div>

                <!-- Épico 3: Poder de Quitação -->
                <div v-if="nextTargetDebt" class="mt-3 pt-3 border-t border-brand-hairline-dark/20 px-1">
                  <p class="text-[10px] text-brand-ink-mute-dark mb-1.5">
                    Poder de Quitação:
                    <span class="font-medium text-white/70">{{ nextTargetDebt.name }}</span>
                  </p>
                  <div class="h-1.5 w-full bg-zinc-800 rounded-full overflow-hidden">
                    <div
                      class="h-full rounded-full transition-all duration-700"
                      :class="vaultProgressPct >= 50 ? 'bg-emerald-500' : 'bg-zinc-500'"
                      :style="{ width: vaultProgressPct + '%' }"
                    />
                  </div>
                  <p class="text-[10px] font-tabular text-brand-ink-mute-dark mt-1">
                    {{ fmt(caixinhaBalance) }} / {{ fmt(nextTargetDebt.amount) }}
                    <span class="ml-1 text-white/40">({{ vaultProgressPct.toFixed(0) }}%)</span>
                  </p>
                  <p v-if="payoffEstimate === 0" class="text-[10px] text-emerald-400 mt-1">
                    Caixinha já cobre essa dívida!
                  </p>
                  <p v-else-if="payoffEstimate" class="text-[10px] text-brand-ink-mute-dark/70 mt-1 italic">
                    Com este ritmo: ~{{ payoffEstimate }} {{ payoffEstimate === 1 ? 'mês' : 'meses' }} para quitar {{ nextTargetDebt.name }}
                  </p>
                </div>
              </div>

              <div v-else-if="store.currentView === 'alvaro'">
                <IncomeRow :label="`Renda de ${store.nameAlvaro}`" :value="store.incomeAlvaro" field="income_alvaro" :readonly="store.isReadOnly" />
                <div class="border-t border-brand-hairline-dark/20 my-3" />
                <div class="flex justify-between mb-1">
                  <span class="text-brand-ink-mute-dark text-sm">Contas de {{ store.nameAlvaro }}</span>
                  <span class="font-tabular font-medium text-brand-ink-mute-dark text-sm">− {{ fmt(alvaroCommitted) }}</span>
                </div>
                <FreeCashDisplay :value="store.saldoAlvaro" :label="`Saldo de ${store.nameAlvaro}`" />
              </div>

              <div v-else-if="store.currentView === 'alexandra'">
                <IncomeRow :label="`Renda de ${store.nameAlexandra}`" :value="store.incomeAlexandra" field="income_alexandra" :readonly="store.isReadOnly" />
                <div class="border-t border-brand-hairline-dark/20 my-3" />
                <div class="flex justify-between mb-1">
                  <span class="text-brand-ink-mute-dark text-sm">Contas de {{ store.nameAlexandra }}</span>
                  <span class="font-tabular font-medium text-brand-ink-mute-dark text-sm">− {{ fmt(alexandraCommitted) }}</span>
                </div>
                <FreeCashDisplay :value="store.saldoAlexandra" :label="`Saldo de ${store.nameAlexandra}`" />
              </div>
            </Transition>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- Modal insight IA -->
  <BaseModal v-model="showInsightModal" title="Análise do Mês">
    <div class="space-y-4">
      <div class="flex items-start gap-3">
        <div class="w-8 h-8 rounded-xl bg-brand-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
          <Bot :size="15" class="text-brand-primary" />
        </div>
        <p class="text-sm text-brand-ink-light dark:text-white leading-relaxed">
          {{ aiInsight }}
        </p>
      </div>
    </div>
    <template #footer>
      <button
        @click="showInsightModal = false"
        class="w-full py-3 rounded-full border border-brand-hairline-light dark:border-brand-hairline-dark text-sm font-medium text-brand-ink-light dark:text-white hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark/40 transition-colors"
      >
        Fechar
      </button>
    </template>
  </BaseModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ChevronDown, PiggyBank, Bot } from 'lucide-vue-next'
import { useDashboardStore } from '../../stores/dashboard.js'
import { formatCurrency } from '../../utils/currency.js'
import { useGamification } from '../../composables/useGamification.js'
import IncomeRow from './IncomeRow.vue'
import FreeCashDisplay from './FreeCashDisplay.vue'
import BaseModal from '../ui/BaseModal.vue'
import CurrencyInput from '../ui/CurrencyInput.vue'

const store = useDashboardStore()
const fmt = formatCurrency

const {
  isAnalyzing, aiInsight, showInsightModal, analyzeMonth,
  vaultProgressPct, nextTargetDebt, caixinhaBalance,
  healthScore, healthConfig,
  monthlyGoal, goalMet, goalProgress, setMonthlyGoal,
  payoffEstimate,
} = useGamification()

const editingGoal  = ref(false)
const goalEditVal  = ref(0)

function startGoalEdit() {
  goalEditVal.value = monthlyGoal.value
  editingGoal.value = true
}
function saveGoal() {
  setMonthlyGoal(goalEditVal.value)
  editingGoal.value = false
}

const tabs = computed(() => [
  { key: 'geral', label: 'Visão Geral' },
  { key: 'alvaro', label: store.nameAlvaro },
  { key: 'alexandra', label: store.nameAlexandra },
])

const collapsed = computed({
  get: () => store.balanceSummaryCollapsed,
  set: (v) => { store.balanceSummaryCollapsed = v },
})

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

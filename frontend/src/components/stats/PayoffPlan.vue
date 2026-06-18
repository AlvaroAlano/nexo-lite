<template>
  <div class="font-ss01">

    <!-- ════ Sem dívidas a quitar — estado comemorativo ════ -->
    <div v-if="!payableDebts.length" class="flex flex-col items-center gap-2 py-8 text-center">
      <div class="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
        <PartyPopper :size="22" class="text-emerald-500" />
      </div>
      <p class="text-sm font-semibold text-brand-ink-light dark:text-white">Nada a quitar por aqui</p>
      <p class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark max-w-[34ch]">
        Você não tem dívidas em aberto. Quando registrar uma em "Eu devo", o plano de quitação aparece aqui.
      </p>
    </div>

    <div v-else class="space-y-5">

      <!-- ════ 1. Seletor de estratégia ════ -->
      <div>
        <p class="text-[10px] font-bold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-2">
          Estratégia
        </p>
        <div class="grid grid-cols-2 gap-2.5">
          <button
            v-for="opt in strategyOptions"
            :key="opt.key"
            @click="strategy = opt.key"
            class="text-left p-3 rounded-xl border-2 transition-all duration-150 active:scale-[.98]"
            :class="strategy === opt.key
              ? 'border-brand-primary bg-brand-primary/[0.07] dark:bg-brand-primary/10'
              : 'border-brand-hairline-light dark:border-brand-hairline-dark hover:border-brand-primary/40'"
          >
            <div class="flex items-center gap-2 mb-1">
              <component :is="opt.icon" :size="16" :class="strategy === opt.key ? 'text-brand-primary' : 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark'" />
              <span class="text-sm font-semibold text-brand-ink-light dark:text-white">{{ opt.title }}</span>
            </div>
            <p class="text-[11px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark leading-snug">{{ opt.tagline }}</p>
            <span
              v-if="opt.badge"
              class="inline-block mt-2 text-[9px] font-semibold rounded-full px-2 py-0.5 border"
              :class="opt.badgeClass"
            >{{ opt.badge }}</span>
          </button>
        </div>
      </div>

      <!-- ════ 2. Aporte mensal ════ -->
      <div>
        <div class="flex items-baseline justify-between mb-1.5">
          <p class="text-[10px] font-bold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark">
            Quanto pagar por mês
          </p>
          <button
            v-if="Math.round(budget) !== suggestedBudget && suggestedBudget > 0"
            @click="budget = suggestedBudget"
            class="text-[10px] text-brand-primary dark:text-brand-primary-soft hover:underline"
          >
            usar sugestão ({{ fmtCompact(suggestedBudget) }})
          </button>
        </div>

        <div class="flex items-center gap-2">
          <CurrencyInput
            v-model="budget"
            input-class="w-36 text-xl font-bold py-2 px-3 bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-xl text-brand-ink-light dark:text-white"
          />
          <span class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark">/ mês</span>
        </div>

        <input
          type="range"
          min="0"
          :max="sliderMax"
          step="50"
          v-model.number="budget"
          class="w-full mt-3 accent-brand-primary cursor-pointer"
        />

        <div class="flex gap-1.5 mt-1">
          <button
            v-for="chip in [-100, 100, 200]"
            :key="chip"
            @click="bump(chip)"
            class="text-[11px] font-medium rounded-lg px-2 py-1 border border-brand-hairline-light dark:border-brand-hairline-dark text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:border-brand-primary hover:text-brand-primary transition-colors"
          >{{ chip > 0 ? '+' : '' }}{{ chip }}</button>
        </div>
      </div>

      <!-- ════ 3. Resultado (hero) ════ -->
      <!-- Viável -->
      <div
        v-if="plan.feasible && plan.months > 0"
        class="rounded-2xl p-4 bg-gradient-to-br from-brand-primary/[0.10] to-emerald-500/[0.06] border border-brand-primary/20"
      >
        <p class="text-[10px] font-bold uppercase tracking-wider text-brand-primary dark:text-brand-primary-soft">
          Você fica livre em
        </p>
        <p class="text-3xl font-bold text-brand-ink-light dark:text-white tracking-tight mt-0.5">
          {{ fmtMonthLong(plan.months) }}
        </p>
        <p class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark mt-1.5 leading-relaxed">
          São <span class="font-semibold text-brand-ink-light dark:text-white">{{ plan.months }} {{ plan.months === 1 ? 'mês' : 'meses' }}</span>
          pagando <span class="font-tabular">{{ fmt(budget) }}</span> por mês.
          <template v-if="plan.totalInterest > 1">
            No caminho você paga <span class="font-tabular font-semibold text-amber-600 dark:text-amber-400">{{ fmt(plan.totalInterest) }}</span> de juros.
          </template>
          <template v-else>
            Sem juros pesando — é só manter o ritmo.
          </template>
        </p>
      </div>

      <!-- Já quitado -->
      <div v-else-if="plan.feasible" class="rounded-2xl p-4 bg-emerald-500/[0.08] border border-emerald-500/20 flex items-center gap-3">
        <CheckCircle2 :size="22" class="text-emerald-500 flex-shrink-0" />
        <p class="text-sm text-brand-ink-light dark:text-white">Tudo certo — não há saldo a quitar com esse plano.</p>
      </div>

      <!-- Inviável: juros vencem o aporte -->
      <div v-else class="rounded-2xl p-4 bg-amber-500/[0.08] border border-amber-500/25">
        <div class="flex items-center gap-2 mb-1.5">
          <AlertTriangle :size="16" class="text-amber-500 flex-shrink-0" />
          <p class="text-sm font-semibold text-amber-700 dark:text-amber-400">Os juros estão ganhando da parcela</p>
        </div>
        <p class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark leading-relaxed">
          Com <span class="font-tabular">{{ fmt(budget) }}</span>/mês você cobre menos que os
          <span class="font-tabular font-semibold text-amber-600 dark:text-amber-400">{{ fmt(plan.monthlyInterest) }}</span>/mês
          que as dívidas geram de juros — então o saldo não diminui.
        </p>
        <button
          v-if="suggestedMin > 0"
          @click="budget = suggestedMin"
          class="mt-2.5 text-xs font-semibold text-brand-primary dark:text-brand-primary-soft hover:underline"
        >
          Ajustar para {{ fmt(suggestedMin) }}/mês → quita em ~2 anos
        </button>
      </div>

      <!-- ════ 4. Comparação de estratégias ════ -->
      <div class="rounded-xl p-3 bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark/50 border border-brand-hairline-light dark:border-brand-hairline-dark flex items-start gap-2.5">
        <Lightbulb :size="15" class="text-amber-500 flex-shrink-0 mt-0.5" />
        <p class="text-[11px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark leading-relaxed">
          <template v-if="!comparison.hasInterest">
            Defina os <span class="font-medium text-brand-ink-light dark:text-white">juros (% a.m.)</span> de cada dívida no detalhe para o plano comparar quanto cada estratégia economiza.
          </template>
          <template v-else-if="comparison.cheaper === 'avalanche'">
            A <span class="font-semibold text-brand-ink-light dark:text-white">Avalanche</span> economiza
            <span class="font-tabular font-semibold text-emerald-600 dark:text-emerald-400">{{ fmt(comparison.interestDiff) }}</span> em juros<template v-if="comparison.monthsDiff > 0"> e te livra {{ comparison.monthsDiff }} {{ comparison.monthsDiff === 1 ? 'mês' : 'meses' }} antes</template>.
            <template v-if="strategy === 'avalanche'"> Você já está nela. 👏</template>
            <template v-else> A Bola de Neve dá vitórias mais rápidas, se precisar de ânimo.</template>
          </template>
          <template v-else-if="comparison.cheaper === 'snowball'">
            Aqui a <span class="font-semibold text-brand-ink-light dark:text-white">Bola de Neve</span> sai na frente — junta economia e vitórias rápidas.
          </template>
          <template v-else>
            As duas estratégias dão praticamente o mesmo resultado com estas dívidas. Escolha pela motivação.
          </template>
        </p>
      </div>

      <!-- ════ 5. Ordem de ataque (timeline) ════ -->
      <div>
        <p class="text-[10px] font-bold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-2.5">
          Ordem de ataque
        </p>
        <div class="space-y-0">
          <div
            v-for="(item, idx) in planRows"
            :key="item.id"
            class="relative flex items-center gap-3 pb-3 last:pb-0"
          >
            <!-- Linha conectora -->
            <div
              v-if="idx < planRows.length - 1"
              class="absolute left-[11px] top-6 w-px h-full bg-brand-hairline-light dark:bg-brand-hairline-dark"
            />
            <!-- Número -->
            <div
              class="relative z-10 w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-bold flex-shrink-0"
              :class="idx === 0
                ? 'bg-brand-primary text-white'
                : 'bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark text-brand-ink-mute-light dark:text-brand-ink-mute-dark'"
            >{{ idx + 1 }}</div>
            <!-- Conteúdo -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-1.5">
                <span class="text-sm font-medium text-brand-ink-light dark:text-white truncate">{{ item.name }}</span>
                <span
                  v-if="item.rate > 0"
                  class="text-[9px] font-semibold rounded-full px-1.5 py-0.5 bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 flex-shrink-0"
                >{{ fmtRate(item.rate) }}% a.m.</span>
                <span
                  v-if="idx === 0"
                  class="text-[8px] font-bold uppercase tracking-wide rounded-full px-1.5 py-0.5 bg-brand-primary/10 text-brand-primary dark:text-brand-primary-soft border border-brand-primary/20 flex-shrink-0"
                >Próxima</span>
              </div>
              <p v-if="idx === 0" class="text-[10px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark mt-0.5">
                Joga tudo aqui primeiro.
              </p>
            </div>
            <!-- Data de quitação -->
            <div class="text-right flex-shrink-0">
              <p class="text-[11px] font-tabular font-medium text-brand-ink-light dark:text-white">{{ fmt(item.balance) }}</p>
              <p class="text-[10px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark">
                {{ item.monthIndex ? `quita ${fmtMonthShort(item.monthIndex)}` : '—' }}
              </p>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Snowflake, MountainSnow, Lightbulb, AlertTriangle, CheckCircle2, PartyPopper } from 'lucide-vue-next'
import { useDebtsStore } from '../../stores/debts.js'
import { useVaultStore } from '../../stores/vault.js'
import { useDashboardStore } from '../../stores/dashboard.js'
import { usePayoffPlan } from '../../composables/usePayoffPlan.js'
import CurrencyInput from '../ui/CurrencyInput.vue'

const debtsStore = useDebtsStore()
const vault = useVaultStore()
const dashboard = useDashboardStore()

const PT_SHORT = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

onMounted(() => {
  if (!debtsStore.debts.length) debtsStore.fetchDebts()
  if (!vault.summary) vault.fetchSummary()
})

// ── Dívidas que o aporte ataca: eu devo, ativas, com saldo ────────────────────
const payableDebts = computed(() =>
  debtsStore.debts.filter(
    (d) => d.direction === 'eu_devo' && d.status !== 'quitado' && (parseFloat(d.estimated_amount) || 0) > 0
  )
)

// ── Sugestão de aporte: média de aportes na Caixinha → free cash → fallback ───
const suggestedBudget = computed(() => {
  const hist = (vault.summary?.history ?? []).map((h) => parseFloat(h.amount)).filter((a) => a > 0)
  if (hist.length) return Math.round(hist.reduce((s, a) => s + a, 0) / hist.length)
  const free = Math.round(dashboard.freeCash || 0)
  if (free > 0) return free
  return 300
})

// ── Estado: estratégia + aporte (persistidos) ─────────────────────────────────
const strategy = ref(localStorage.getItem('nexo_payoff_strategy') || 'avalanche')
const budget = ref(parseFloat(localStorage.getItem('nexo_payoff_budget')) || 0)

watch(strategy, (v) => localStorage.setItem('nexo_payoff_strategy', v))
watch(budget, (v) => localStorage.setItem('nexo_payoff_budget', String(v || 0)))

// Inicializa o aporte com a sugestão quando ela estiver disponível
watch(suggestedBudget, (s) => {
  if (!budget.value && s > 0) budget.value = s
}, { immediate: true })

function bump(delta) {
  budget.value = Math.max(0, Math.round((parseFloat(budget.value) || 0) + delta))
}

const sliderMax = computed(() => {
  const candidates = [budget.value, suggestedBudget.value * 3, plan.value.monthlyInterest * 3, 500]
  return Math.ceil(Math.max(...candidates) / 100) * 100
})

// ── Plano + comparação ────────────────────────────────────────────────────────
const { plan, comparison } = usePayoffPlan(payableDebts, budget, strategy)

// Aporte mínimo sugerido para quitar em ~24 meses quando inviável
const suggestedMin = computed(() => {
  const totalDebt = payableDebts.value.reduce((s, d) => s + (parseFloat(d.estimated_amount) || 0), 0)
  const raw = plan.value.monthlyInterest + totalDebt / 24
  return Math.ceil(raw / 50) * 50
})

// Linhas da timeline (ordem da estratégia + saldo/juros para exibir)
const planRows = computed(() =>
  plan.value.order.map((o) => {
    const debt = payableDebts.value.find((d) => d.id === o.id)
    return {
      ...o,
      balance: parseFloat(debt?.estimated_amount) || 0,
      rate: parseFloat(debt?.interest_rate) || 0,
    }
  })
)

// ── Opções de estratégia (com badges dinâmicos) ───────────────────────────────
const strategyOptions = computed(() => [
  {
    key: 'snowball',
    title: 'Bola de Neve',
    tagline: 'Menor dívida primeiro — vitórias rápidas pra manter o ânimo.',
    icon: Snowflake,
    badge: 'Mais motivação',
    badgeClass: 'bg-brand-primary/10 border-brand-primary/20 text-brand-primary dark:text-brand-primary-soft',
  },
  {
    key: 'avalanche',
    title: 'Avalanche',
    tagline: 'Maior juro primeiro — você paga menos no total.',
    icon: MountainSnow,
    badge: comparison.value.cheaper === 'avalanche' && comparison.value.interestDiff > 1
      ? `Economiza ${fmtCompact(comparison.value.interestDiff)}`
      : 'Menos juros',
    badgeClass: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400',
  },
])

// ── Formatação ────────────────────────────────────────────────────────────────
const fmt = (n) => (parseFloat(n) || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
const fmtCompact = (n) => `R$ ${Math.round(parseFloat(n) || 0).toLocaleString('pt-BR')}`
const fmtRate = (r) => (parseFloat(r) || 0).toLocaleString('pt-BR', { maximumFractionDigits: 2 })

function dateFromNow(monthsAhead) {
  const d = new Date()
  d.setDate(1)
  d.setMonth(d.getMonth() + monthsAhead)
  return d
}
const fmtMonthLong = (m) => {
  const d = dateFromNow(m)
  return `${PT_SHORT[d.getMonth()]} ${d.getFullYear()}`
}
const fmtMonthShort = (m) => {
  const d = dateFromNow(m)
  return `${PT_SHORT[d.getMonth()]}/${String(d.getFullYear()).slice(2)}`
}
</script>

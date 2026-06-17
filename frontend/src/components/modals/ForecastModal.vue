<template>
  <Teleport to="body">
    <Transition name="forecast-slide">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-[9998] bg-[#f8f9fb] dark:bg-[#0f1117] overflow-y-auto font-ss01"
      >
        <!-- ── Header sticky ──────────────────────────────────────────────── -->
        <div class="sticky top-0 z-10 bg-[#f8f9fb]/95 dark:bg-[#0f1117]/95 backdrop-blur-xl border-b border-brand-hairline-light dark:border-brand-hairline-dark px-4 md:px-8 py-4 flex items-center justify-between">
          <div>
            <h2 class="text-base font-semibold text-brand-ink-light dark:text-white">Projeção de Recorrências</h2>
            <p class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark mt-0.5">Próximos 12 meses com base nos templates ativos</p>
          </div>
          <button
            @click="$emit('update:modelValue', false)"
            class="w-8 h-8 rounded-full flex items-center justify-center text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark transition-colors"
          >
            <X :size="18" stroke-width="2.5" />
          </button>
        </div>

        <!-- ── Content ───────────────────────────────────────────────────── -->
        <div class="max-w-4xl mx-auto px-4 md:px-8 py-6 space-y-5">

          <!-- Summary cards -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div class="bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-xl p-3.5">
              <p class="text-[10px] font-semibold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-1.5">Próximo mês</p>
              <p class="text-lg font-bold font-tabular text-brand-ink-light dark:text-white leading-none">{{ fmt(nextMonthTotal) }}</p>
              <p class="text-[10px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark mt-1">{{ forecastPct }}% da renda</p>
            </div>
            <div class="bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-xl p-3.5">
              <p class="text-[10px] font-semibold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-1.5">Saldo livre</p>
              <p class="text-lg font-bold font-tabular leading-none" :class="freeForecast >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-500 dark:text-red-400'">
                {{ fmt(Math.abs(freeForecast)) }}
              </p>
              <p class="text-[10px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark mt-1">{{ freeForecast >= 0 ? 'disponível' : 'acima da renda' }}</p>
            </div>
            <div class="bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-xl p-3.5">
              <p class="text-[10px] font-semibold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-1.5">Em 12 meses</p>
              <p class="text-lg font-bold font-tabular text-emerald-600 dark:text-emerald-400 leading-none">{{ fmt(lastMonthTotal) }}</p>
              <p class="text-[10px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark mt-1">comprometido</p>
            </div>
            <div class="bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-xl p-3.5">
              <p class="text-[10px] font-semibold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-1.5">Liberado total</p>
              <p class="text-lg font-bold font-tabular text-brand-primary dark:text-brand-primary-soft leading-none">{{ fmt(totalSavings12) }}</p>
              <p class="text-[10px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark mt-1">em 12 meses</p>
            </div>
          </div>

          <!-- Motivational message -->
          <div class="bg-gradient-to-r from-brand-primary/5 via-brand-primary/3 to-emerald-500/5 border border-brand-primary/15 dark:border-brand-primary/20 rounded-xl p-4 flex items-start gap-3">
            <span class="text-2xl flex-shrink-0 leading-none mt-0.5">{{ motivational.icon }}</span>
            <p class="text-sm text-brand-ink-light dark:text-white leading-relaxed">{{ motivational.text }}</p>
          </div>

          <!-- Bar chart: 12 months -->
          <div class="bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-xl p-4 md:p-5">
            <h3 class="text-[10px] font-bold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-4">Comprometimento mês a mês</h3>
            <div class="flex items-end gap-1 md:gap-1.5" style="height: 100px;">
              <div
                v-for="(month, i) in monthlyProjection"
                :key="i"
                class="flex-1 flex flex-col items-center gap-1 group relative"
              >
                <!-- Tooltip -->
                <div class="absolute bottom-full mb-1.5 left-1/2 -translate-x-1/2 bg-brand-ink-light dark:bg-white text-white dark:text-brand-ink-light text-[9px] font-bold px-2 py-1 rounded-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 shadow-lg">
                  {{ fmt(month.total) }}
                  <div class="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-brand-ink-light dark:border-t-white" />
                </div>
                <!-- Bar -->
                <div class="w-full flex items-end justify-center" style="height: 84px;">
                  <div
                    class="w-full rounded-t-md transition-all duration-700"
                    :style="{ height: barHeight(month.total) + 'px' }"
                    :class="barColor(month.total, i)"
                  />
                </div>
                <!-- Label -->
                <span class="text-[7px] md:text-[8px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark font-medium leading-none text-center">
                  {{ month.label }}
                </span>
              </div>
            </div>
            <div class="mt-3 pt-3 border-t border-brand-hairline-light dark:border-brand-hairline-dark flex items-center justify-between text-[10px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark">
              <span>Hoje: <span class="font-tabular font-semibold text-brand-ink-light dark:text-white">{{ fmt(nextMonthTotal) }}</span></span>
              <span v-if="lastMonthTotal < nextMonthTotal">
                Daqui a 12 meses: <span class="font-tabular font-semibold text-emerald-600 dark:text-emerald-400">{{ fmt(lastMonthTotal) }}</span>
              </span>
            </div>
          </div>

          <!-- When does it breathe? -->
          <div v-if="bestReliefMonth" class="bg-emerald-500/5 dark:bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4 flex items-start gap-3">
            <span class="text-xl flex-shrink-0 mt-0.5">🌬️</span>
            <div>
              <p class="text-sm font-semibold text-brand-ink-light dark:text-white">Quando você respira</p>
              <p class="text-sm text-brand-ink-mute-light dark:text-brand-ink-mute-dark mt-0.5 leading-relaxed">
                Em <span class="font-semibold text-emerald-600 dark:text-emerald-400">{{ bestReliefMonth.label }}</span>
                você elimina {{ bestReliefMonth.count }} {{ bestReliefMonth.count === 1 ? 'parcela' : 'parcelas' }} e libera
                <span class="font-semibold font-tabular text-emerald-600 dark:text-emerald-400">{{ fmt(bestReliefMonth.relief) }}/mês</span>
                de uma vez.
              </p>
            </div>
          </div>

          <!-- 2-col grid: installments ending + breakdown -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">

            <!-- Installments ending -->
            <div v-if="installmentsEnding.length" class="bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-xl p-4">
              <h3 class="text-[10px] font-bold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-3">Parcelas a terminar</h3>
              <div class="space-y-3">
                <div v-for="t in installmentsEnding" :key="t.id" class="flex items-center gap-3">
                  <div
                    class="w-9 h-9 rounded-xl flex flex-col items-center justify-center flex-shrink-0"
                    :class="t.remaining <= 2
                      ? 'bg-emerald-500/10'
                      : t.remaining <= 5 ? 'bg-amber-500/10' : 'bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark'"
                  >
                    <span
                      class="text-sm font-bold leading-none"
                      :class="t.remaining <= 2 ? 'text-emerald-600 dark:text-emerald-400' : t.remaining <= 5 ? 'text-amber-600 dark:text-amber-400' : 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark'"
                    >{{ t.remaining }}</span>
                    <span class="text-[8px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark leading-none">mes</span>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-brand-ink-light dark:text-white truncate">{{ t.name }}</p>
                    <p class="text-[10px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark mt-0.5">
                      {{ t.installment_paid }}/{{ t.installment_total }} pagas
                    </p>
                  </div>
                  <span class="font-tabular text-sm font-semibold text-brand-ink-light dark:text-white flex-shrink-0">{{ fmt(t.base_amount) }}</span>
                </div>
              </div>
            </div>

            <!-- Breakdown by type -->
            <div class="bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-xl p-4">
              <h3 class="text-[10px] font-bold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-3">Composição do comprometimento</h3>
              <div class="space-y-3">
                <div v-for="type in breakdown" :key="type.key">
                  <div class="flex items-center justify-between text-xs mb-1">
                    <span class="text-brand-ink-light dark:text-white font-medium">{{ type.label }}</span>
                    <div class="flex items-center gap-2">
                      <span class="text-brand-ink-mute-light dark:text-brand-ink-mute-dark">{{ type.pct }}%</span>
                      <span class="font-tabular font-semibold text-brand-ink-light dark:text-white w-20 text-right">{{ fmt(type.total) }}</span>
                    </div>
                  </div>
                  <div class="h-2 w-full bg-slate-100 dark:bg-zinc-800 rounded-full overflow-hidden">
                    <div class="h-full rounded-full transition-all duration-700" :class="type.color" :style="{ width: type.pct + '%' }" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Top 5 mais pesadas -->
          <div class="bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-xl p-4">
            <h3 class="text-[10px] font-bold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-3">Top 5 mais pesadas</h3>
            <div class="divide-y divide-brand-hairline-light dark:divide-brand-hairline-dark/40">
              <div v-for="(t, i) in top5" :key="t.id" class="flex items-center gap-3 py-2.5">
                <span
                  class="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold flex-shrink-0"
                  :class="i === 0 ? 'bg-amber-400/20 text-amber-600 dark:text-amber-400' : 'bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark text-brand-ink-mute-light dark:text-brand-ink-mute-dark'"
                >{{ i + 1 }}</span>
                <span class="flex-1 text-sm text-brand-ink-light dark:text-white truncate">{{ t.name }}</span>
                <span class="text-[9px] font-bold px-2 py-0.5 rounded-full" :class="typeBadgeClass(t.expense_type)">{{ typeLabel(t.expense_type) }}</span>
                <div class="text-right flex-shrink-0">
                  <p class="font-tabular text-sm font-semibold text-brand-ink-light dark:text-white">{{ fmt(t.base_amount) }}</p>
                  <p v-if="incomeTotal" class="text-[9px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark">
                    {{ Math.round((parseFloat(t.base_amount) / incomeTotal) * 100) }}% da renda
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Accumulated savings -->
          <div class="bg-gradient-to-br from-emerald-500/5 to-brand-primary/5 border border-emerald-500/20 rounded-xl p-5 flex items-start gap-4">
            <span class="text-3xl flex-shrink-0">🏆</span>
            <div>
              <p class="text-[10px] font-bold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-1">Economia acumulada em 12 meses</p>
              <p class="text-2xl font-bold font-tabular text-emerald-600 dark:text-emerald-400">{{ fmt(totalSavings12) }}</p>
              <p class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark mt-1.5 leading-relaxed">
                Esse é o valor que você vai economizar em relação a manter o gasto atual de
                <span class="font-tabular font-semibold">{{ fmt(nextMonthTotal) }}/mês</span> por 12 meses.
                Cada parcela que termina trabalha a seu favor.
              </p>
            </div>
          </div>

          <!-- bottom spacer -->
          <div class="h-4" />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { X } from 'lucide-vue-next'

const props = defineProps({
  modelValue: Boolean,
  templates: { type: Array, default: () => [] },
  incomeTotal: { type: Number, default: 0 },
})
defineEmits(['update:modelValue'])

// ── Active templates ───────────────────────────────────────────────────────────
const activeTemplates = computed(() => props.templates.filter((t) => t.is_active))

// ── Amount resolver per template ──────────────────────────────────────────────
function templateAmount(t) {
  if (t.expense_type === 'rent') {
    const rentSum = (t.rent_items || []).reduce((s, i) => s + (parseFloat(i.amount) || 0), 0)
    return rentSum || parseFloat(t.base_amount) || 0
  }
  return parseFloat(t.base_amount) || 0
}

// ── Next month total ──────────────────────────────────────────────────────────
const nextMonthTotal = computed(() =>
  activeTemplates.value
    .filter((t) => t.expense_type !== 'installment' || (t.installment_paid ?? 0) < (t.installment_total ?? 0))
    .reduce((s, t) => s + templateAmount(t), 0)
)

const forecastPct = computed(() => {
  if (!props.incomeTotal) return 0
  return Math.min(100, Math.round((nextMonthTotal.value / props.incomeTotal) * 100))
})

const freeForecast = computed(() => props.incomeTotal - nextMonthTotal.value)

// ── 12-month projection ───────────────────────────────────────────────────────
const monthlyProjection = computed(() => {
  const now = new Date()
  return Array.from({ length: 12 }, (_, m) => {
    const date = new Date(now.getFullYear(), now.getMonth() + m + 1, 1)
    const label = date.toLocaleDateString('pt-BR', { month: 'short', year: '2-digit' })
    const total = activeTemplates.value
      .filter((t) => {
        if (t.expense_type !== 'installment') return true
        const remaining = (t.installment_total ?? 0) - (t.installment_paid ?? 0)
        return m < remaining
      })
      .reduce((s, t) => s + templateAmount(t), 0)
    return { label, total, m }
  })
})

const lastMonthTotal = computed(() =>
  monthlyProjection.value[11]?.total ?? nextMonthTotal.value
)

// savings vs keeping current spend for 12 months
const totalSavings12 = computed(() =>
  monthlyProjection.value.reduce((s, month) => s + Math.max(0, nextMonthTotal.value - month.total), 0)
)

// ── Bar chart helpers ─────────────────────────────────────────────────────────
const maxBarValue = computed(() => Math.max(...monthlyProjection.value.map((m) => m.total), 1))
const MAX_BAR_PX = 84

function barHeight(total) {
  return Math.max(4, (total / maxBarValue.value) * MAX_BAR_PX)
}

function barColor(total, i) {
  if (i === 0) return 'bg-red-400/60 dark:bg-red-500/50'
  const drop = (nextMonthTotal.value - total) / (nextMonthTotal.value || 1)
  if (drop >= 0.2) return 'bg-emerald-500/70 dark:bg-emerald-500/60'
  if (drop >= 0.05) return 'bg-brand-primary/50 dark:bg-brand-primary/40'
  return 'bg-slate-300/80 dark:bg-zinc-600/60'
}

// ── Best relief month ─────────────────────────────────────────────────────────
const bestReliefMonth = computed(() => {
  let best = null
  for (let i = 1; i < monthlyProjection.value.length; i++) {
    const relief = monthlyProjection.value[i - 1].total - monthlyProjection.value[i].total
    if (relief <= 0) continue
    const count = activeTemplates.value.filter(
      (t) => t.expense_type === 'installment' &&
             (t.installment_total ?? 0) - (t.installment_paid ?? 0) === i
    ).length
    if (!best || relief > best.relief) {
      best = { label: monthlyProjection.value[i].label, relief, count: count || 1 }
    }
  }
  return best
})

// ── Installments ending list ──────────────────────────────────────────────────
const installmentsEnding = computed(() =>
  activeTemplates.value
    .filter((t) => t.expense_type === 'installment' && (t.installment_paid ?? 0) < (t.installment_total ?? 0))
    .map((t) => ({ ...t, remaining: (t.installment_total ?? 0) - (t.installment_paid ?? 0) }))
    .sort((a, b) => a.remaining - b.remaining)
    .slice(0, 6)
)

// ── Breakdown by type ─────────────────────────────────────────────────────────
const breakdown = computed(() => {
  const total = nextMonthTotal.value || 1
  return [
    { key: 'fixed',       label: 'Fixa',      color: 'bg-brand-primary' },
    { key: 'installment', label: 'Parcelada',  color: 'bg-amber-400' },
    { key: 'variable',    label: 'Variável',   color: 'bg-slate-400 dark:bg-zinc-500' },
    { key: 'rent',        label: 'Aluguel',    color: 'bg-blue-400' },
  ]
    .map((type) => {
      const typeTotal = activeTemplates.value
        .filter((t) => t.expense_type === type.key)
        .reduce((s, t) => s + templateAmount(t), 0)
      return { ...type, total: typeTotal, pct: Math.round((typeTotal / total) * 100) }
    })
    .filter((t) => t.total > 0)
})

// ── Top 5 ────────────────────────────────────────────────────────────────────
const top5 = computed(() =>
  [...activeTemplates.value]
    .sort((a, b) => templateAmount(b) - templateAmount(a))
    .slice(0, 5)
)

// ── Motivational message ──────────────────────────────────────────────────────
const motivational = computed(() => {
  const installmentTs = activeTemplates.value.filter(
    (t) => t.expense_type === 'installment' && (t.installment_paid ?? 0) < (t.installment_total ?? 0)
  )
  const installmentAmt = installmentTs.reduce((s, t) => s + templateAmount(t), 0)
  const remainingList = installmentTs.map((t) => (t.installment_total ?? 0) - (t.installment_paid ?? 0))
  const minRemaining = remainingList.length ? Math.min(...remainingList) : 0
  const maxRemaining = remainingList.length ? Math.max(...remainingList) : 0

  if (installmentTs.length === 0 && forecastPct.value < 60) {
    return {
      icon: '🎉',
      text: `Parabéns! Você não tem nenhuma compra parcelada ativa e compromete apenas ${forecastPct.value}% da renda. Continue nesse ritmo e seu orçamento sempre terá fôlego para imprevistos.`,
    }
  }

  if (installmentTs.length === 0) {
    return {
      icon: '💚',
      text: `Nenhuma parcela ativa! Toda sua carga fixa de ${fmt(nextMonthTotal.value)}/mês é composta por despesas recorrentes previsíveis — o tipo mais fácil de controlar e planejar.`,
    }
  }

  if (minRemaining === 1) {
    const nextFreeAmt = installmentTs
      .filter((t) => (t.installment_total ?? 0) - (t.installment_paid ?? 0) === 1)
      .reduce((s, t) => s + templateAmount(t), 0)
    return {
      icon: '🏁',
      text: `Você está a 1 pagamento de liberar ${fmt(nextFreeAmt)}/mês! Não comece nenhuma compra parcelada agora — você está quase lá e esse dinheiro vai ficar livre no próximo mês.`,
    }
  }

  if (maxRemaining <= 4) {
    return {
      icon: '🌱',
      text: `Se não fizer novas compras parceladas, em ${maxRemaining} meses você vai liberar ${fmt(installmentAmt)}/mês — ${Math.round((installmentAmt / (props.incomeTotal || 1)) * 100)}% da sua renda de volta. Está quase lá.`,
    }
  }

  const saving = nextMonthTotal.value - lastMonthTotal.value
  if (saving > 100) {
    return {
      icon: '💡',
      text: `Se não fizer novas compras parceladas, em 12 meses sua carga mensal cai de ${fmt(nextMonthTotal.value)} para ${fmt(lastMonthTotal.value)} — uma redução de ${fmt(saving)}/mês. Cada novo parcelamento adia esse alívio.`,
    }
  }

  const fixedAmt = nextMonthTotal.value - installmentAmt
  return {
    icon: '📊',
    text: `Suas parcelas somam ${fmt(installmentAmt)}/mês. Sua base fixa inevitável é ${fmt(fixedAmt)}/mês. Manter o controle sobre as parcelas é o caminho mais rápido para aumentar seu saldo livre todo mês.`,
  }
})

// ── Formatters ────────────────────────────────────────────────────────────────
function fmt(n) {
  return (parseFloat(n) || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function typeLabel(t) {
  return { fixed: 'Fixa', variable: 'Variável', installment: 'Parcela', rent: 'Aluguel' }[t] || t
}

function typeBadgeClass(t) {
  return {
    fixed:       'bg-brand-primary/10 text-brand-primary dark:text-brand-primary-soft',
    installment: 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
    variable:    'bg-slate-100 text-slate-600 dark:bg-zinc-800 dark:text-zinc-400',
    rent:        'bg-blue-500/10 text-blue-600 dark:text-blue-400',
  }[t] || ''
}
</script>

<style scoped>
.forecast-slide-enter-active {
  animation: forecast-in 0.28s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}
.forecast-slide-leave-active {
  animation: forecast-in 0.18s ease-in reverse forwards;
}
@keyframes forecast-in {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>

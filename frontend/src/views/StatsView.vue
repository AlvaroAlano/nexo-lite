<template>
  <div
    class="max-w-5xl mx-auto px-4 pt-5 pb-6 font-ss01"
    @touchstart="handleTouchStart"
    @touchmove="handleTouchMove"
    @touchend="handleTouchEnd"
  >
    <PullRefreshIndicator :pull-distance="pullDistance" :refreshing="refreshing" />

    <!-- Spinner enquanto history/templates carregam -->
    <div v-if="(statsStore.loading || dashboard.loading) && !refreshing" class="flex justify-center py-16">
      <div class="w-5 h-5 rounded-full border-2 border-brand-hairline-light dark:border-brand-hairline-dark border-t-brand-primary animate-spin" />
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-5 items-start">

      <!-- 0: Caixinha — dados via useVaultStore (já integrado) -->
      <StatCard class="md:col-span-2" title="Caixinha" subtitle="Reserva financeira — aportes e rendimento acumulado">
        <VaultStats />
      </StatCard>

      <!-- 1: Dívidas Ativas — dados via useDebtsStore (já integrado) -->
      <StatCard class="md:col-span-2" title="Dívidas Ativas" subtitle="Quanto a Caixinha já cobre de cada dívida">
        <DebtsList />
      </StatCard>

      <!-- 2: Radar de Comprometimento — projeção via templates -->
      <StatCard title="Radar de Comprometimento" subtitle="Custo total previsto nos próximos 6 meses">
        <FutureRadarChart :data="futureMonthsData" />
      </StatCard>

      <!-- 3: Evolução do Saldo Livre — histórico real de períodos -->
      <StatCard title="Evolução do Saldo Livre" subtitle="Free Cash e Carryover — últimos 6 meses">
        <FreeCashChart :data="freeCashData" />
      </StatCard>

      <!-- 4: Termômetro de Liquidez — despesas do mês atual -->
      <StatCard title="Termômetro de Liquidez" subtitle="Proporção do orçamento comprometida em fixos">
        <LiquidityDonut :data="liquidityData" />
      </StatCard>

      <!-- 5: Cabo de Guerra — despesas por responsável do mês atual -->
      <StatCard title="Cabo de Guerra" subtitle="Distribuição de carga financeira entre os membros">
        <WarBar :data="warData" />
      </StatCard>

    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useDashboardStore } from '../stores/dashboard.js'
import { useStatsStore }     from '../stores/stats.js'
import { usePullToRefresh } from '../composables/usePullToRefresh.js'
import PullRefreshIndicator from '../components/ui/PullRefreshIndicator.vue'
import StatCard          from '../components/stats/StatCard.vue'
import WarBar            from '../components/stats/WarBar.vue'
import FutureRadarChart  from '../components/stats/FutureRadarChart.vue'
import LiquidityDonut    from '../components/stats/LiquidityDonut.vue'
import FreeCashChart     from '../components/stats/FreeCashChart.vue'
import VaultStats        from '../components/stats/VaultStats.vue'
import DebtsList         from '../components/stats/DebtsList.vue'

const dashboard  = useDashboardStore()
const statsStore = useStatsStore()

const PT_MONTHS = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']

onMounted(() => {
  if (!dashboard.period && !dashboard.loading) dashboard.fetchCurrent()
  if (!statsStore.history.length && !statsStore.loading) statsStore.fetchAll()
})

const { pullDistance, refreshing, handleTouchStart, handleTouchMove, handleTouchEnd } =
  usePullToRefresh(async () => {
    await Promise.all([dashboard.fetchCurrent(), statsStore.fetchAll()])
  })

// ── Cabo de Guerra — soma de despesas por responsável do mês atual ───────────
const warData = computed(() => {
  const by = { alvaro: 0, alexandra: 0, conjunto: 0 }
  for (const e of dashboard.expenses) {
    const amt = parseFloat(e.amount || 0)
    if      (e.responsavel === 'alvaro')    by.alvaro    += amt
    else if (e.responsavel === 'alexandra') by.alexandra += amt
    else                                    by.conjunto  += amt
  }
  return {
    alvaro:    { label: dashboard.nameAlvaro    || 'Álvaro',    amount: by.alvaro    },
    alexandra: { label: dashboard.nameAlexandra || 'Alexandra', amount: by.alexandra },
    conjunto:  { label: 'Conjunto',                             amount: by.conjunto  },
  }
})

// ── Termômetro — fixas + aluguel vs variáveis + parceladas ──────────────────
const liquidityData = computed(() => {
  let fixed = 0, variable = 0
  for (const e of dashboard.expenses) {
    const amt = parseFloat(e.amount || 0)
    if (e.expense_type === 'fixed' || e.expense_type === 'rent') fixed    += amt
    else                                                          variable += amt
  }
  return { fixed, variable }
})

// ── Evolução — últimos 6 meses fechados (histórico real) ────────────────────
const freeCashData = computed(() =>
  statsStore.history.slice(-6).map(p => ({
    month:     PT_MONTHS[p.month - 1],
    freeCash:  p.free_cash,
    carryover: p.carryover_balance,
  }))
)

// ── Radar — projeção dos próximos 6 meses via templates ativos ───────────────
const futureMonthsData = computed(() => {
  const now          = new Date()
  const currentMonth = now.getMonth() // 0-indexed

  return Array.from({ length: 6 }, (_, i) => {
    const label = PT_MONTHS[(currentMonth + i) % 12]

    // Mês atual: usa total real de despesas se disponível
    if (i === 0 && dashboard.expenses.length > 0) {
      return { month: label, value: Math.round(dashboard.totalCommitted) }
    }

    // Meses futuros: soma templates que ainda estarão ativos
    const projected = statsStore.templates.reduce((sum, t) => {
      if (!t.is_active) return sum
      // Parcelas: expira quando installment_paid + i >= installment_total
      if (t.installment_total != null && t.installment_paid + i >= t.installment_total) return sum
      return sum + parseFloat(t.base_amount || 0)
    }, 0)

    return { month: label, value: Math.round(projected) }
  })
})
</script>

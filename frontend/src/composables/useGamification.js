import { ref, computed, watch } from 'vue'
import { useDashboardStore } from '../stores/dashboard.js'
import { useVaultStore } from '../stores/vault.js'
import { useDebtsStore } from '../stores/debts.js'

// ── Singletons — estado compartilhado entre componentes ───────────────────────
const currentStreak    = ref(4)
const isAnalyzing      = ref(false)
const aiInsight        = ref(null)
const showInsightModal = ref(false)

// Missão do mês
const GOAL_KEY      = 'nexo_monthly_goal'
const monthlyGoal   = ref(parseFloat(localStorage.getItem(GOAL_KEY)) || 500)

// Milestones
const MILESTONES      = [500, 1000, 2000, 3000, 5000, 10000]
const DISMISSED_KEY   = 'nexo_dismissed_milestones'
const dismissedSet    = new Set(JSON.parse(localStorage.getItem(DISMISSED_KEY) || '[]'))
const activeMilestone = ref(null)
let _milestoneWatcherRegistered = false

const MOCK_INSIGHTS = [
  'Mês sob controle. Notei que a conta de energia subiu R$ 50 em relação à média, mas o aporte na Caixinha foi garantido. Mantenham o ritmo.',
  'Boa consistência. As despesas fixas estão estáveis e o aporte na Caixinha foi mantido pelo 4º mês consecutivo. Vocês estão 30% mais perto de quitar a Renner.',
  'Nada fora do comum este mês. Saldo Livre positivo e Caixinha alimentada. Foco: chegar em R$ 2.000 para quitar a Renner à vista com desconto.',
]

export function useGamification() {
  const dashboard  = useDashboardStore()
  const vault      = useVaultStore()
  const debtsStore = useDebtsStore()

  // ── Saldo da caixinha ─────────────────────────────────────────────────────
  const caixinhaBalance = computed(() => {
    const s = vault.summary
    if (s?.last_real_balance != null) return parseFloat(s.last_real_balance)
    if (s?.total_deposited  != null) return parseFloat(s.total_deposited)
    return dashboard.vaultMonthAmount || 0
  })

  // ── Próxima dívida alvo (snowball) ────────────────────────────────────────
  const nextTargetDebt = computed(() => {
    const sorted = [...debtsStore.debts]
      .sort((a, b) => parseFloat(a.estimated_amount) - parseFloat(b.estimated_amount))
    return sorted[0] ?? { name: 'Renner', amount: 2000 }
  })

  // ── Poder de Quitação (%) ─────────────────────────────────────────────────
  const vaultProgressPct = computed(() => {
    const target = parseFloat(nextTargetDebt.value?.amount) || 1
    return Math.min((caixinhaBalance.value / target) * 100, 100)
  })

  // ── Nota de saúde do mês ─────────────────────────────────────────────────
  const healthScore = computed(() => {
    const income = dashboard.incomeTotal
    if (!income) return null
    const ratio   = dashboard.freeCash / income
    const funded  = dashboard.vaultMonthPaid
    if (ratio >= 0.20 && funded) return 'A'
    if (ratio >= 0.10 && funded) return 'B'
    if (ratio >= 0.05 || funded) return 'C'
    return 'D'
  })

  const healthConfig = computed(() => ({
    A: { label: 'Excelente', textClass: 'text-emerald-400', bgClass: 'bg-emerald-500/15 border-emerald-500/20' },
    B: { label: 'Bom',       textClass: 'text-emerald-400', bgClass: 'bg-emerald-500/10 border-emerald-500/15' },
    C: { label: 'Regular',   textClass: 'text-amber-400',   bgClass: 'bg-amber-500/10  border-amber-500/20'   },
    D: { label: 'Atenção',   textClass: 'text-red-400',     bgClass: 'bg-red-500/10    border-red-500/20'     },
  }[healthScore.value] ?? null))

  // ── Missão do mês ─────────────────────────────────────────────────────────
  function setMonthlyGoal(amount) {
    monthlyGoal.value = parseFloat(amount) || 0
    localStorage.setItem(GOAL_KEY, String(monthlyGoal.value))
  }

  const goalMet = computed(() =>
    monthlyGoal.value > 0 && dashboard.vaultMonthAmount >= monthlyGoal.value
  )

  const goalProgress = computed(() => {
    if (!monthlyGoal.value) return 0
    return Math.min((dashboard.vaultMonthAmount / monthlyGoal.value) * 100, 100)
  })

  // ── Estimativa de quitação ────────────────────────────────────────────────
  const payoffEstimate = computed(() => {
    const remaining = parseFloat(nextTargetDebt.value?.amount) - caixinhaBalance.value
    if (remaining <= 0) return 0

    const history  = vault.summary?.history ?? []
    const deposits = history.map((h) => parseFloat(h.amount)).filter((a) => a > 0)
    const avg      = deposits.length
      ? deposits.reduce((s, a) => s + a, 0) / deposits.length
      : dashboard.vaultMonthAmount

    if (!avg) return null
    return Math.ceil(remaining / avg)
  })

  // ── Streak tooltip ────────────────────────────────────────────────────────
  const streakTooltip = computed(() =>
    currentStreak.value > 0
      ? `${currentStreak.value} ${currentStreak.value === 1 ? 'mês seguido' : 'meses seguidos'} guardando dinheiro para a quitação!`
      : 'Sem ofensiva ativa'
  )

  // ── Milestones ────────────────────────────────────────────────────────────
  if (!_milestoneWatcherRegistered) {
    _milestoneWatcherRegistered = true
  watch(caixinhaBalance, (val) => {
    if (activeMilestone.value) return
    for (const m of MILESTONES) {
      if (val >= m && !dismissedSet.has(m)) {
        activeMilestone.value = m
        setTimeout(dismissMilestone, 5000)
        break
      }
    }
  })
  }

  function dismissMilestone() {
    if (!activeMilestone.value) return
    dismissedSet.add(activeMilestone.value)
    localStorage.setItem(DISMISSED_KEY, JSON.stringify([...dismissedSet]))
    activeMilestone.value = null
  }

  // ── Auditor IA ────────────────────────────────────────────────────────────
  async function analyzeMonth() {
    if (isAnalyzing.value) return
    isAnalyzing.value = true
    aiInsight.value   = null
    await new Promise((r) => setTimeout(r, 1800))
    aiInsight.value        = MOCK_INSIGHTS[Math.floor(Math.random() * MOCK_INSIGHTS.length)]
    isAnalyzing.value      = false
    showInsightModal.value = true
  }

  return {
    // streak
    currentStreak, streakTooltip,
    // caixinha
    caixinhaBalance, nextTargetDebt, vaultProgressPct,
    // saúde
    healthScore, healthConfig,
    // missão
    monthlyGoal, goalMet, goalProgress, setMonthlyGoal,
    // payoff
    payoffEstimate,
    // milestone
    activeMilestone, dismissMilestone,
    // IA
    isAnalyzing, aiInsight, showInsightModal, analyzeMonth,
  }
}

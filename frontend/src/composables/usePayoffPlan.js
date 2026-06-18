import { computed, unref } from 'vue'

// ── Núcleo: simula a quitação mês a mês ───────────────────────────────────────
// debts: [{ id, name, estimated_amount, interest_rate }]  (interest_rate em % a.m.)
// monthlyBudget: quanto se destina por mês (R$)
// strategy: 'snowball' (menor saldo primeiro) | 'avalanche' (maior juro primeiro)
//
// Modelo: todo mês os juros incidem sobre o saldo de TODA dívida; o aporte é
// aplicado em ordem de prioridade (a dívida-alvo primeiro, o que sobra transborda).
// É exatamente assim que a Caixinha funciona: o pote vai inteiro na dívida da vez.
export function simulatePayoff(debts, monthlyBudget, strategy, maxMonths = 600) {
  const working = debts
    .map((d) => ({
      id: d.id,
      name: d.name,
      balance: Math.max(0, parseFloat(d.estimated_amount) || 0),
      rate: (parseFloat(d.interest_rate) || 0) / 100,
    }))
    .filter((d) => d.balance > 0)

  const orderFn =
    strategy === 'avalanche'
      ? (a, b) => b.rate - a.rate || a.balance - b.balance
      : (a, b) => a.balance - b.balance || b.rate - a.rate

  const paidOffAt = {}
  let totalInterest = 0
  let totalPaid = 0
  let month = 0

  const remaining = () => working.reduce((s, d) => s + d.balance, 0)

  if (!working.length) {
    return { feasible: true, months: 0, totalInterest: 0, totalPaid: 0, order: [], monthlyInterest: 0 }
  }

  const budget = parseFloat(monthlyBudget) || 0

  while (remaining() > 0.005 && month < maxMonths) {
    month++
    // 1. juros incidem sobre todos os saldos
    for (const d of working) {
      if (d.balance <= 0) continue
      const interest = d.balance * d.rate
      d.balance += interest
      totalInterest += interest
    }
    // 2. aporte aplicado em ordem de prioridade (transbordo)
    let left = budget
    const active = working.filter((d) => d.balance > 0).sort(orderFn)
    for (const d of active) {
      if (left <= 0) break
      const pay = Math.min(left, d.balance)
      d.balance -= pay
      left -= pay
      totalPaid += pay
      if (d.balance <= 0.005 && !(d.id in paidOffAt)) {
        d.balance = 0
        paidOffAt[d.id] = month
      }
    }
  }

  const feasible = remaining() <= 0.005

  // juros mensais no estado atual — usado para alertar quando o aporte é baixo
  const monthlyInterest = debts.reduce((s, d) => {
    const bal = parseFloat(d.estimated_amount) || 0
    const rate = (parseFloat(d.interest_rate) || 0) / 100
    return s + bal * rate
  }, 0)

  const order = debts
    .filter((d) => (parseFloat(d.estimated_amount) || 0) > 0)
    .map((d) => ({ id: d.id, name: d.name, monthIndex: paidOffAt[d.id] ?? null }))
    .sort((a, b) => (a.monthIndex ?? Infinity) - (b.monthIndex ?? Infinity))

  return {
    feasible,
    months: feasible ? month : null,
    totalInterest,
    totalPaid,
    monthlyInterest,
    order,
  }
}

// ── Composable reativo ────────────────────────────────────────────────────────
export function usePayoffPlan(debtsRef, budgetRef, strategyRef) {
  const plan = computed(() =>
    simulatePayoff(unref(debtsRef), unref(budgetRef), unref(strategyRef))
  )

  // Roda as duas estratégias para comparar economia/tempo
  const comparison = computed(() => {
    const debts = unref(debtsRef)
    const budget = unref(budgetRef)
    const snow = simulatePayoff(debts, budget, 'snowball')
    const aval = simulatePayoff(debts, budget, 'avalanche')
    if (!snow.feasible || !aval.feasible) {
      return { hasInterest: aval.totalInterest > 0.5, interestDiff: 0, monthsDiff: 0, cheaper: null }
    }
    const interestDiff = snow.totalInterest - aval.totalInterest // >0 = avalanche economiza
    const monthsDiff = snow.months - aval.months
    return {
      hasInterest: snow.totalInterest > 0.5 || aval.totalInterest > 0.5,
      interestDiff,
      monthsDiff,
      cheaper: interestDiff > 0.5 ? 'avalanche' : interestDiff < -0.5 ? 'snowball' : 'tie',
    }
  })

  return { plan, comparison }
}

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { periodsApi, expensesApi } from '../services/api.js'
import { parseCurrency } from '../utils/currency.js'

export const useDashboardStore = defineStore('dashboard', () => {
  // ── State ──────────────────────────────────────────────────────────────────
  const period = ref(null)
  const expenses = ref([])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref(null)
  const notFoundMonth = ref(false)   // true when navigating to a non-existent future month

  // Current view: 'geral' | 'alvaro' | 'alexandra'
  const currentView = ref('geral')

  // Nomes dos membros reativos persistidos no localStorage
  const nameAlvaro = ref(localStorage.getItem('name_alvaro') || 'Álvaro')
  const nameAlexandra = ref(localStorage.getItem('name_alexandra') || 'Alexandra')

  // UI flags: FAB actions per screen
  const quickAddOpen = ref(false)
  const quickAddTemplateOpen = ref(false)
  const quickAddCategoryOpen = ref(false)
  const fabMenuOpen = ref(false)
  const balanceSummaryCollapsed = ref(localStorage.getItem('nexo_balance_collapsed') === 'true')

  // ── Read-only: past months have status = 'closed' ─────────────────────────
  const isReadOnly = computed(() => period.value?.status === 'closed')

  // ── Computed — filtered by view ───────────────────────────────────────────
  const filteredExpenses = computed(() => {
    if (currentView.value === 'geral') return expenses.value
    return expenses.value.filter((e) => e.responsavel === currentView.value)
  })

  // ── Computed — balance totals ─────────────────────────────────────────────
  const totalCommitted = computed(() =>
    expenses.value.reduce((sum, e) => sum + (parseFloat(e.amount) || 0), 0)
  )

  const totalPaid = computed(() =>
    expenses.value.filter((e) => e.is_paid).reduce((sum, e) => sum + (parseFloat(e.amount) || 0), 0)
  )

  const incomeAlvaro = computed(() => parseFloat(period.value?.income_alvaro) || 0)
  const incomeAlexandra = computed(() => parseFloat(period.value?.income_alexandra) || 0)
  const incomeTotal = computed(() => incomeAlvaro.value + incomeAlexandra.value)
  const carryover = computed(() => parseFloat(period.value?.carryover_balance) || 0)
  const additionalIncome = computed(() => parseFloat(period.value?.additional_income) || 0)

  // RN-03 — saldo formulas
  const freeCash = computed(() => incomeTotal.value + carryover.value + additionalIncome.value - totalCommitted.value)

  const saldoAlvaro = computed(() => {
    const alvaroExpenses = expenses.value
      .filter((e) => e.responsavel === 'alvaro')
      .reduce((sum, e) => sum + (parseFloat(e.amount) || 0), 0)
    return incomeAlvaro.value - alvaroExpenses
  })

  const saldoAlexandra = computed(() => {
    const alexandraExpenses = expenses.value
      .filter((e) => e.responsavel === 'alexandra')
      .reduce((sum, e) => sum + (parseFloat(e.amount) || 0), 0)
    return incomeAlexandra.value - alexandraExpenses
  })

  const paidCount = computed(() => expenses.value.filter((e) => e.is_paid).length)

  // ── Caixinha (Vault) ──────────────────────────────────────────────────────
  const vaultExpense = computed(() => expenses.value.find((e) => e.category === 'Caixinha') ?? null)
  const vaultMonthAmount = computed(() => parseFloat(vaultExpense.value?.amount) || 0)
  const vaultMonthPaid = computed(() => vaultExpense.value?.is_paid ?? false)

  // ── Actions ────────────────────────────────────────────────────────────────
  async function fetchCurrent() {
    loading.value = true
    error.value = null
    notFoundMonth.value = false
    try {
      const { data } = await periodsApi.getCurrent()
      period.value = data.period
      expenses.value = data.expenses
    } catch (e) {
      error.value = 'Não foi possível carregar os dados. Verifique a conexão.'
      console.error(e)
    } finally {
      loading.value = false
    }
  }

  async function fetchByMonth(year, month) {
    loading.value = true
    error.value = null
    notFoundMonth.value = false
    try {
      const { data } = await periodsApi.getByMonth(year, month)
      period.value = data.period
      expenses.value = data.expenses
    } catch (e) {
      if (e.response?.status === 404) {
        notFoundMonth.value = true
        period.value = null
        expenses.value = []
      } else {
        error.value = 'Não foi possível carregar os dados.'
      }
    } finally {
      loading.value = false
    }
  }

  async function updateIncome(field, value) {
    if (!period.value || isReadOnly.value) return
    const amount = typeof value === 'number' ? value : parseCurrency(value)
    saving.value = true
    error.value = null
    try {
      const { data } = await periodsApi.updateIncome(period.value.id, { [field]: amount })
      period.value = data
    } catch (e) {
      error.value = 'Não foi possível salvar a renda.'
      console.error(e)
      throw e
    } finally {
      saving.value = false
    }
  }

  async function updateExpenseAmount(expenseId, rawValue) {
    if (isReadOnly.value) return
    const expense = expenses.value.find((e) => e.id === expenseId)
    if (expense?.expense_type === 'rent') return
    const amount = typeof rawValue === 'number' ? rawValue : parseCurrency(rawValue)
    saving.value = true
    try {
      const { data } = await expensesApi.update(expenseId, { amount })
      _replaceExpense(data)
    } catch (e) {
      error.value = 'Não foi possível salvar o valor.'
      console.error(e)
    } finally {
      saving.value = false
    }
  }

  async function togglePaid(expenseId) {
    if (isReadOnly.value) return
    // Optimistic update for snappy UI
    const idx = expenses.value.findIndex((e) => e.id === expenseId)
    if (idx !== -1) expenses.value[idx].is_paid = !expenses.value[idx].is_paid

    try {
      const { data } = await expensesApi.togglePaid(expenseId)
      _replaceExpense(data)
    } catch {
      // revert on failure
      if (idx !== -1) expenses.value[idx].is_paid = !expenses.value[idx].is_paid
    }
  }

  async function updateRent(expenseId, components) {
    if (isReadOnly.value) return
    saving.value = true
    try {
      const { data } = await expensesApi.updateRent(expenseId, components)
      _replaceExpense(data)
    } finally {
      saving.value = false
    }
  }

  async function addExpense(payload) {
    if (!period.value || isReadOnly.value) return
    saving.value = true
    try {
      const { data } = await expensesApi.create(period.value.id, {
        display_order: expenses.value.length,
        ...payload,
      })
      expenses.value.push(data)
    } finally {
      saving.value = false
    }
  }

  async function deleteExpense(expenseId) {
    if (isReadOnly.value) return
    const removed = expenses.value.find((e) => e.id === expenseId)
    expenses.value = expenses.value.filter((e) => e.id !== expenseId)
    try {
      await expensesApi.delete(expenseId)
    } catch (e) {
      if (removed) expenses.value = [...expenses.value, removed].sort((a, b) => (a.display_order ?? 9999) - (b.display_order ?? 9999))
      throw e
    }
  }

  function removeExpenseLocally(expenseId) {
    expenses.value = expenses.value.filter((e) => e.id !== expenseId)
  }

  function restoreExpense(expense) {
    expenses.value = [...expenses.value, expense]
      .sort((a, b) => (a.display_order ?? 9999) - (b.display_order ?? 9999))
  }

  async function hardDeleteExpense(expenseId) {
    try { await expensesApi.delete(expenseId) }
    catch (e) { console.error('[delete]', e) }
  }

  async function updateExpenseFull(expenseId, payload) {
    if (isReadOnly.value) return
    saving.value = true
    error.value = null
    try {
      const { data } = await expensesApi.update(expenseId, payload)
      _replaceExpense(data)
    } catch (e) {
      error.value = 'Não foi possível salvar as alterações.'
      console.error(e)
      throw e
    } finally {
      saving.value = false
    }
  }

  async function runTurnover() {
    saving.value = true
    error.value = null
    try {
      await periodsApi.turnover()
      await fetchCurrent()
      notFoundMonth.value = false
    } catch (e) {
      error.value = e.response?.data?.detail || 'Não foi possível fechar o mês.'
      console.error(e)
      throw e
    } finally {
      saving.value = false
    }
  }

  function setView(view) {
    currentView.value = view
  }

  function updateNames(alvaro, alexandra) {
    nameAlvaro.value = alvaro || 'Álvaro'
    nameAlexandra.value = alexandra || 'Alexandra'
    localStorage.setItem('name_alvaro', nameAlvaro.value)
    localStorage.setItem('name_alexandra', nameAlexandra.value)
  }

  function _replaceExpense(updated) {
    const idx = expenses.value.findIndex((e) => e.id === updated.id)
    if (idx !== -1) expenses.value[idx] = updated
  }

  return {
    period, expenses, loading, saving, error, notFoundMonth,
    currentView, nameAlvaro, nameAlexandra,
    quickAddOpen, quickAddTemplateOpen, quickAddCategoryOpen, fabMenuOpen, balanceSummaryCollapsed, isReadOnly,
    filteredExpenses,
    totalCommitted, totalPaid, freeCash,
    incomeAlvaro, incomeAlexandra, incomeTotal, carryover, additionalIncome,
    saldoAlvaro, saldoAlexandra, paidCount,
    vaultExpense, vaultMonthAmount, vaultMonthPaid,
    fetchCurrent, fetchByMonth, updateIncome, updateExpenseAmount,
    togglePaid, updateRent, addExpense, deleteExpense,
    removeExpenseLocally, restoreExpense, hardDeleteExpense, updateExpenseFull,
    runTurnover, setView, updateNames,
  }
})

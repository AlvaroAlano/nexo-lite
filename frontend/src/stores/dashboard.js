import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { periodsApi, expensesApi } from '../services/api.js'
import { parseCurrency } from '../utils/currency.js'

export const useDashboardStore = defineStore('dashboard', () => {
  // ── 1. Estado Inicial com Hidratação Local ──────────────────────────────────
  const cachedPeriod = localStorage.getItem('nexo_cached_period')
  const cachedExpenses = localStorage.getItem('nexo_cached_expenses')

  const period = ref(cachedPeriod ? JSON.parse(cachedPeriod) : null)
  const expenses = ref(cachedExpenses ? JSON.parse(cachedExpenses) : [])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref(null)
  const notFoundMonth = ref(false)

  // Current view: 'geral' | 'alvaro' | 'alexandra'
  const currentView = ref('geral')

  // Fila Outbox e estado de rede
  const outbox = ref(JSON.parse(localStorage.getItem('nexo_outbox') || '[]'))
  const isSyncing = ref(false)
  const isOfflineMode = ref(typeof navigator !== 'undefined' ? !navigator.onLine : false)

  // Nomes dos membros reativos persistidos no localStorage
  const nameAlvaro = ref(localStorage.getItem('name_alvaro') || 'Álvaro')
  const nameAlexandra = ref(localStorage.getItem('name_alexandra') || 'Alexandra')

  // UI flags
  const quickAddOpen = ref(false)
  const quickAddTemplateOpen = ref(false)
  const quickAddCategoryOpen = ref(false)
  const fabMenuOpen = ref(false)
  const balanceSummaryCollapsed = ref(localStorage.getItem('nexo_balance_collapsed') === 'true')

  // Persistência automática de dados locais
  watch(period, (newVal) => {
    if (newVal) localStorage.setItem('nexo_cached_period', JSON.stringify(newVal))
  }, { deep: true })

  watch(expenses, (newVal) => {
    localStorage.setItem('nexo_cached_expenses', JSON.stringify(newVal))
  }, { deep: true })

  watch(outbox, (newVal) => {
    localStorage.setItem('nexo_outbox', JSON.stringify(newVal))
  }, { deep: true })

  // ── Read-only: past months have status = 'closed' ─────────────────────────
  const isReadOnly = computed(() => period.value?.status === 'closed')

  // ── Computed — filtered by view ───────────────────────────────────────────
  const filteredExpenses = computed(() => {
    if (currentView.value === 'geral') return expenses.value
    return expenses.value.filter((e) => e.responsavel === currentView.value)
  })

  // ── Computed — balance totals ─────────────────────────────────────────────
  const totalCommitted = computed(() =>
    expenses.value
      .filter((e) => !e.is_excluded)
      .reduce((sum, e) => sum + (parseFloat(e.amount) || 0), 0)
  )

  const totalPaid = computed(() =>
    expenses.value
      .filter((e) => e.is_paid && !e.is_excluded)
      .reduce((sum, e) => sum + (parseFloat(e.amount) || 0), 0)
  )

  const incomeAlvaro = computed(() => parseFloat(period.value?.income_alvaro) || 0)
  const incomeAlexandra = computed(() => parseFloat(period.value?.income_alexandra) || 0)
  const incomeTotal = computed(() => incomeAlvaro.value + incomeAlexandra.value)
  const carryover = computed(() => parseFloat(period.value?.carryover_balance) || 0)
  const additionalIncomeItems = computed(() => period.value?.additional_income_items || [])
  const additionalIncomeTotal = computed(() => {
    return additionalIncomeItems.value.reduce((sum, item) => sum + (parseFloat(item.amount) || 0), 0)
  })

  const salariosTotal = computed(() => incomeAlvaro.value + incomeAlexandra.value)
  const rendimentosTotal = computed(() => salariosTotal.value + additionalIncomeTotal.value)

  // RN-03 — saldo formulas
  const freeCash = computed(() => rendimentosTotal.value + carryover.value - totalCommitted.value)

  const saldoAlvaro = computed(() => {
    const alvaroExpenses = expenses.value
      .filter((e) => e.responsavel === 'alvaro' && !e.is_excluded)
      .reduce((sum, e) => sum + (parseFloat(e.amount) || 0), 0)
    return incomeAlvaro.value - alvaroExpenses
  })

  const saldoAlexandra = computed(() => {
    const alexandraExpenses = expenses.value
      .filter((e) => e.responsavel === 'alexandra' && !e.is_excluded)
      .reduce((sum, e) => sum + (parseFloat(e.amount) || 0), 0)
    return incomeAlexandra.value - alexandraExpenses
  })

  const paidCount = computed(() => expenses.value.filter((e) => e.is_paid && !e.is_excluded).length)

  // ── Caixinha (Vault) ──────────────────────────────────────────────────────
  const vaultExpense = computed(() => expenses.value.find((e) => e.category === 'Caixinha') ?? null)
  const vaultMonthAmount = computed(() => parseFloat(vaultExpense.value?.amount) || 0)
  const vaultMonthPaid = computed(() => vaultExpense.value?.is_paid ?? false)

  // ── Actions ────────────────────────────────────────────────────────────────
  
  // Adiciona ação na fila outbox
  function _enqueue(actionType, payload, tempId = null) {
    outbox.value.push({
      id: crypto.randomUUID(),
      action: actionType,
      payload,
      tempId,
      timestamp: Date.now()
    })
    triggerSync()
  }

  async function fetchCurrent() {
    loading.value = true
    error.value = null
    notFoundMonth.value = false
    try {
      if (isOfflineMode.value) {
        return
      }
      const { data } = await periodsApi.getCurrent()
      period.value = data.period
      expenses.value = data.expenses
    } catch (e) {
      if (_isNetworkError(e)) {
        error.value = 'Sem conexão. Exibindo dados salvos localmente.'
      } else {
        error.value = 'Não foi possível carregar os dados. Verifique a conexão.'
        console.error(e)
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchByMonth(year, month) {
    loading.value = true
    error.value = null
    notFoundMonth.value = false
    try {
      if (isOfflineMode.value) {
        if (period.value && period.value.year === year && period.value.month === month) {
          return
        }
        throw new Error('Offline and not cached')
      }
      const { data } = await periodsApi.getByMonth(year, month)
      period.value = data.period
      expenses.value = data.expenses
    } catch (e) {
      if (e.response?.status === 404) {
        notFoundMonth.value = true
        period.value = null
        expenses.value = []
      } else if (_isNetworkError(e)) {
        if (period.value && period.value.year === year && period.value.month === month) {
          error.value = 'Sem conexão. Exibindo dados salvos localmente.'
        } else {
          error.value = 'Não foi possível carregar os dados deste mês offline.'
        }
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
    
    // Otimista
    const previousVal = period.value[field]
    period.value[field] = amount
    error.value = null

    try {
      if (isOfflineMode.value) {
        throw new Error('Offline')
      }
      saving.value = true
      const { data } = await periodsApi.updateIncome(period.value.id, { [field]: amount })
      period.value = data
    } catch (e) {
      if (!_isNetworkError(e)) {
        period.value[field] = previousVal
        error.value = 'Não foi possível salvar a renda.'
        throw e
      }
      _enqueue('update_income', { periodId: period.value.id, field, amount })
    } finally {
      saving.value = false
    }
  }

  async function updateExpenseAmount(expenseId, rawValue) {
    if (isReadOnly.value) return
    const expense = expenses.value.find((e) => e.id === expenseId)
    if (expense?.expense_type === 'rent') return
    const amount = typeof rawValue === 'number' ? rawValue : parseCurrency(rawValue)

    const previousAmount = expense.amount
    expense.amount = amount // Otimista

    try {
      if (isOfflineMode.value || _isTempId(expenseId)) {
        throw new Error('Offline or Temp ID')
      }
      saving.value = true
      const { data } = await expensesApi.update(expenseId, { amount })
      _replaceExpense(data)
    } catch (e) {
      if (!_isNetworkError(e) && !_isTempId(expenseId)) {
        expense.amount = previousAmount
        throw e
      }
      _enqueue('update_expense', { expenseId, payload: { amount } })
    } finally {
      saving.value = false
    }
  }

  async function togglePaid(expenseId) {
    if (isReadOnly.value) return
    const idx = expenses.value.findIndex((e) => e.id === expenseId)
    if (idx === -1) return
    
    expenses.value[idx].is_paid = !expenses.value[idx].is_paid // Otimista

    try {
      if (isOfflineMode.value || _isTempId(expenseId)) {
        throw new Error('Offline or Temp ID')
      }
      const { data } = await expensesApi.togglePaid(expenseId)
      _replaceExpense(data)
    } catch (e) {
      if (!_isNetworkError(e) && !_isTempId(expenseId)) {
        expenses.value[idx].is_paid = !expenses.value[idx].is_paid // Reverte
        throw e
      }
      _enqueue('toggle_paid', { expenseId })
    }
  }

  async function toggleExpenseExclusion(expenseId) {
    if (isReadOnly.value) return
    const idx = expenses.value.findIndex((e) => e.id === expenseId)
    if (idx === -1) return
    
    expenses.value[idx].is_excluded = !expenses.value[idx].is_excluded // Otimista

    try {
      if (isOfflineMode.value || _isTempId(expenseId)) {
        throw new Error('Offline or Temp ID')
      }
      const { data } = await expensesApi.toggleExcluded(expenseId)
      _replaceExpense(data)
    } catch (e) {
      if (!_isNetworkError(e) && !_isTempId(expenseId)) {
        expenses.value[idx].is_excluded = !expenses.value[idx].is_excluded // Reverte
        throw e
      }
      _enqueue('toggle_excluded', { expenseId })
    }
  }

  async function updateRent(expenseId, components) {
    if (isReadOnly.value) return
    const expense = expenses.value.find((e) => e.id === expenseId)
    if (!expense) return

    const previousItems = expense.rent_items
    const previousAmount = expense.amount

    // Otimista
    expense.rent_items = components
    expense.amount = components.reduce((sum, item) => sum + (parseFloat(item.amount) || 0), 0)

    try {
      if (isOfflineMode.value || _isTempId(expenseId)) {
        throw new Error('Offline or Temp ID')
      }
      saving.value = true
      const { data } = await expensesApi.updateRent(expenseId, components)
      _replaceExpense(data)
    } catch (e) {
      if (!_isNetworkError(e) && !_isTempId(expenseId)) {
        expense.rent_items = previousItems
        expense.amount = previousAmount
        throw e
      }
      _enqueue('update_rent', { expenseId, components })
    } finally {
      saving.value = false
    }
  }

  async function addExpense(payload) {
    if (!period.value || isReadOnly.value) return
    const tempId = crypto.randomUUID()
    const tempExpense = {
      id: tempId,
      period_id: period.value.id,
      display_order: expenses.value.length,
      is_paid: payload.is_paid || false,
      is_temp: true,
      ...payload
    }
    expenses.value.push(tempExpense) // Otimista

    try {
      if (isOfflineMode.value || outbox.value.length > 0) {
        throw new Error('Offline or pending outbox queue')
      }
      saving.value = true
      const { data } = await expensesApi.create(period.value.id, {
        display_order: tempExpense.display_order,
        ...payload
      })
      _replaceTempExpense(tempId, data)
    } catch (e) {
      if (!_isNetworkError(e)) {
        expenses.value = expenses.value.filter(e => e.id !== tempId)
        throw e
      }
      _enqueue('create_expense', payload, tempId)
    } finally {
      saving.value = false
    }
  }

  async function deleteExpense(expenseId) {
    if (isReadOnly.value) return
    const removed = expenses.value.find((e) => e.id === expenseId)
    expenses.value = expenses.value.filter((e) => e.id !== expenseId) // Otimista

    try {
      if (isOfflineMode.value || _isTempId(expenseId)) {
        throw new Error('Offline or Temp ID')
      }
      await expensesApi.delete(expenseId)
    } catch (e) {
      if (!_isNetworkError(e) && !_isTempId(expenseId)) {
        if (removed) expenses.value.push(removed)
        throw e
      }
      _enqueue('delete_expense', { expenseId })
    }
  }

  // Utilizado pelo dashboard no fluxo com UNDO
  function removeExpenseLocally(expenseId) {
    expenses.value = expenses.value.filter((e) => e.id !== expenseId)
  }

  function restoreExpense(expense) {
    expenses.value = [...expenses.value, expense]
      .sort((a, b) => (a.display_order ?? 9999) - (b.display_order ?? 9999))
  }

  async function hardDeleteExpense(expenseId) {
    if (isReadOnly.value) return
    try {
      if (isOfflineMode.value || _isTempId(expenseId)) {
        throw new Error('Offline or Temp ID')
      }
      await expensesApi.delete(expenseId)
    } catch (e) {
      if (!_isNetworkError(e) && !_isTempId(expenseId)) {
        return
      }
      _enqueue('delete_expense', { expenseId })
    }
  }

  async function updateExpenseFull(expenseId, payload) {
    if (isReadOnly.value) return
    const expense = expenses.value.find((e) => e.id === expenseId)
    if (!expense) return

    const previousExpense = { ...expense }
    
    // Otimista
    Object.assign(expense, payload)

    try {
      if (isOfflineMode.value || _isTempId(expenseId)) {
        throw new Error('Offline or Temp ID')
      }
      saving.value = true
      const { data } = await expensesApi.update(expenseId, payload)
      _replaceExpense(data)
    } catch (e) {
      if (!_isNetworkError(e) && !_isTempId(expenseId)) {
        Object.assign(expense, previousExpense)
        throw e
      }
      _enqueue('update_expense_full', { expenseId, payload })
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

  // ── 3. Motor de Reconciliação (Sincronização) ──────────────────────────────
  async function triggerSync() {
    if (isSyncing.value || !outbox.value.length) return
    if (typeof navigator !== 'undefined' && !navigator.onLine) {
      isOfflineMode.value = true
      return
    }
    isOfflineMode.value = false
    isSyncing.value = true

    try {
      while (outbox.value.length > 0) {
        const action = outbox.value[0]
        const success = await _processAction(action)
        if (success) {
          outbox.value.shift()
        } else {
          break
        }
      }
    } finally {
      isSyncing.value = false
    }
  }

  async function _processAction(action) {
    try {
      const { action: type, payload, tempId } = action

      if (type === 'update_income') {
        const { periodId, field, amount } = payload
        const { data } = await periodsApi.updateIncome(periodId, { [field]: amount })
        if (period.value && period.value.id === periodId) period.value = data
      }
      else if (type === 'create_expense') {
        const { data } = await expensesApi.create(period.value.id, payload)
        _replaceTempExpense(tempId, data)
        _resolveTempIdInOutbox(tempId, data.id)
      }
      else if (type === 'update_expense') {
        const { expenseId, payload: body } = payload
        const { data } = await expensesApi.update(expenseId, body)
        _replaceExpense(data)
      }
      else if (type === 'toggle_paid') {
        const { expenseId } = payload
        const { data } = await expensesApi.togglePaid(expenseId)
        _replaceExpense(data)
      }
      else if (type === 'toggle_excluded') {
        const { expenseId } = payload
        const { data } = await expensesApi.toggleExcluded(expenseId)
        _replaceExpense(data)
      }
      else if (type === 'update_rent') {
        const { expenseId, components } = payload
        const { data } = await expensesApi.updateRent(expenseId, components)
        _replaceExpense(data)
      }
      else if (type === 'update_expense_full') {
        const { expenseId, payload: body } = payload
        const { data } = await expensesApi.update(expenseId, body)
        _replaceExpense(data)
      }
      else if (type === 'delete_expense') {
        const { expenseId } = payload
        if (!_isTempId(expenseId)) {
          await expensesApi.delete(expenseId)
        }
      }
      return true
    } catch (e) {
      console.error('[Sync Error]', e)
      return !_isNetworkError(e)
    }
  }

  function _isTempId(id) {
    return typeof id === 'string' && id.length > 30 && expenses.value.some(e => e.id === id && e.is_temp)
  }

  function _isNetworkError(error) {
    return !error.response || error.response.status >= 500 || error.code === 'ECONNABORTED'
  }

  function _replaceTempExpense(tempId, realExpense) {
    const idx = expenses.value.findIndex(e => e.id === tempId)
    if (idx !== -1) {
      expenses.value[idx] = realExpense
    }
  }

  function _replaceExpense(updated) {
    const idx = expenses.value.findIndex((e) => e.id === updated.id)
    if (idx !== -1) expenses.value[idx] = updated
  }

  function _resolveTempIdInOutbox(tempId, realId) {
    outbox.value.forEach(action => {
      if (action.payload && action.payload.expenseId === tempId) {
        action.payload.expenseId = realId
      }
      if (action.tempId === tempId) {
        action.tempId = realId
      }
    })
  }

  // Monitoramento nativo de status de rede
  if (typeof window !== 'undefined') {
    window.addEventListener('online', () => {
      isOfflineMode.value = false
      triggerSync()
    })
    window.addEventListener('offline', () => {
      isOfflineMode.value = true
    })
  }

  return {
    period, expenses, loading, saving, error, notFoundMonth,
    currentView, nameAlvaro, nameAlexandra,
    quickAddOpen, quickAddTemplateOpen, quickAddCategoryOpen, fabMenuOpen, balanceSummaryCollapsed, isReadOnly,
    filteredExpenses,
    totalCommitted, totalPaid, freeCash,
    incomeAlvaro, incomeAlexandra, incomeTotal, carryover, additionalIncomeItems, additionalIncomeTotal, salariosTotal, rendimentosTotal,
    saldoAlvaro, saldoAlexandra, paidCount,
    vaultExpense, vaultMonthAmount, vaultMonthPaid,
    outbox, isSyncing, isOfflineMode, triggerSync,
    fetchCurrent, fetchByMonth, updateIncome, updateExpenseAmount,
    togglePaid, toggleExpenseExclusion, updateRent, addExpense, deleteExpense,
    removeExpenseLocally, restoreExpense, hardDeleteExpense, updateExpenseFull,
    runTurnover, setView, updateNames,
  }
})

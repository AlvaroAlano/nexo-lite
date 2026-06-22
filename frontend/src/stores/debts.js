import { defineStore } from 'pinia'
import { ref, watch, computed } from 'vue'
import { debtsApi } from '../services/api.js'

export const useDebtsStore = defineStore('debts', () => {
  // ── 1. Estado Inicial com Hidratação Local ──────────────────────────────────
  const cachedDebts = localStorage.getItem('nexo_cached_debts')

  const debts = ref(cachedDebts ? JSON.parse(cachedDebts) : [])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref(null)

  // Fila Outbox e estado de rede
  const outbox = ref(JSON.parse(localStorage.getItem('nexo_debts_outbox') || '[]'))
  const isSyncing = ref(false)
  const isOfflineMode = ref(typeof navigator !== 'undefined' ? !navigator.onLine : false)

  // ── Modal state ────────────────────────────────────────────────────────────
  const loanModalOpen = ref(false)
  const editingLoan   = ref(null) // null = create, object = view/edit

  // Persistência automática de dados locais
  watch(debts, (newVal) => {
    localStorage.setItem('nexo_cached_debts', JSON.stringify(newVal))
  }, { deep: true })

  watch(outbox, (newVal) => {
    localStorage.setItem('nexo_debts_outbox', JSON.stringify(newVal))
  }, { deep: true })

  function openLoanModal(debt = null) {
    editingLoan.value   = debt
    loanModalOpen.value = true
  }

  function closeLoanModal() {
    loanModalOpen.value = false
    editingLoan.value   = null
  }

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

  // ── CRUD ───────────────────────────────────────────────────────────────────
  async function fetchDebts() {
    loading.value = true
    error.value = null
    try {
      if (isOfflineMode.value) {
        return
      }
      const { data } = await debtsApi.list()
      debts.value = data
    } catch (e) {
      if (_isNetworkError(e)) {
        error.value = 'Sem conexão. Exibindo dívidas salvas localmente.'
      } else {
        error.value = 'Não foi possível carregar as dívidas.'
        console.error(e)
      }
    } finally {
      loading.value = false
    }
  }

  async function createDebt(payload) {
    const tempId = crypto.randomUUID()
    const tempDebt = {
      id: tempId,
      status: 'ativo',
      is_temp: true,
      display_order: debts.value.length + 1,
      estimated_amount: payload.amount || payload.estimated_amount || 0,
      ...payload
    }
    debts.value.push(tempDebt) // Otimista

    try {
      if (isOfflineMode.value || outbox.value.length > 0) {
        throw new Error('Offline or pending outbox queue')
      }
      saving.value = true
      const { data } = await debtsApi.create({
        ...payload,
        display_order: tempDebt.display_order,
      })
      _replaceTempDebt(tempId, data)
      return data
    } catch (e) {
      if (!_isNetworkError(e)) {
        debts.value = debts.value.filter(d => d.id !== tempId)
        throw e
      }
      _enqueue('create_debt', payload, tempId)
      return tempDebt
    } finally {
      saving.value = false
    }
  }

  async function updateDebt(id, payload) {
    const idx = debts.value.findIndex((d) => d.id === id)
    if (idx === -1) return

    const previousDebt = { ...debts.value[idx] }
    
    // Otimista
    Object.assign(debts.value[idx], payload)

    try {
      if (isOfflineMode.value || _isTempId(id)) {
        throw new Error('Offline or Temp ID')
      }
      const { data } = await debtsApi.update(id, payload)
      debts.value[idx] = data
      return data
    } catch (e) {
      if (!_isNetworkError(e) && !_isTempId(id)) {
        debts.value[idx] = previousDebt
        await fetchDebts()
        throw e
      }
      _enqueue('update_debt', { id, payload })
    }
  }

  async function settleDebt(id) {
    const idx = debts.value.findIndex((d) => d.id === id)
    if (idx === -1) return

    const previousDebt = { ...debts.value[idx] }
    
    // Otimista
    debts.value[idx].status = 'quitado'
    debts.value[idx].estimated_amount = 0

    try {
      if (isOfflineMode.value || _isTempId(id)) {
        throw new Error('Offline or Temp ID')
      }
      const { data } = await debtsApi.settle(id)
      debts.value[idx] = data
      return data
    } catch (e) {
      if (!_isNetworkError(e) && !_isTempId(id)) {
        debts.value[idx] = previousDebt
        await fetchDebts()
        throw e
      }
      _enqueue('settle_debt', { id })
    }
  }

  async function deleteDebt(id) {
    const prev = [...debts.value]
    debts.value = debts.value.filter((d) => d.id !== id) // Otimista

    try {
      if (isOfflineMode.value || _isTempId(id)) {
        throw new Error('Offline or Temp ID')
      }
      await debtsApi.delete(id)
    } catch (e) {
      if (!_isNetworkError(e) && !_isTempId(id)) {
        debts.value = prev
        throw e
      }
      _enqueue('delete_debt', { id })
    }
  }

  // ── Payments ───────────────────────────────────────────────────────────────
  async function fetchPayments(debtId) {
    if (isOfflineMode.value || _isTempId(debtId)) {
      // Retorna vazio ou tenta ler de cache (YAGNI/retornar vazio offline)
      return []
    }
    const { data } = await debtsApi.listPayments(debtId)
    return data
  }

  async function addPayment(debtId, payload) {
    const idx = debts.value.findIndex((d) => d.id === debtId)
    let previousAmt = 0
    if (idx !== -1) {
      previousAmt = parseFloat(debts.value[idx].estimated_amount) || 0
      // Otimista
      const paymentVal = parseFloat(payload.amount) || 0
      debts.value[idx].estimated_amount = Math.max(0, previousAmt - paymentVal)
    }

    try {
      if (isOfflineMode.value || _isTempId(debtId)) {
        throw new Error('Offline or Temp ID')
      }
      saving.value = true
      const { data: payment } = await debtsApi.addPayment(debtId, payload)
      // Refresh
      const { data: updatedDebts } = await debtsApi.list()
      debts.value = updatedDebts
      return payment
    } catch (e) {
      if (!_isNetworkError(e) && !_isTempId(debtId)) {
        if (idx !== -1) debts.value[idx].estimated_amount = previousAmt
        throw e
      }
      _enqueue('add_payment', { debtId, payload })
      return { id: crypto.randomUUID(), debt_id: debtId, ...payload }
    } finally {
      saving.value = false
    }
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

      if (type === 'create_debt') {
        const { data } = await debtsApi.create({
          ...payload,
          display_order: debts.value.length + 1
        })
        _replaceTempDebt(tempId, data)
        _resolveTempIdInOutbox(tempId, data.id)
      }
      else if (type === 'update_debt') {
        const { id, payload: body } = payload
        const { data } = await debtsApi.update(id, body)
        _replaceDebt(data)
      }
      else if (type === 'settle_debt') {
        const { id } = payload
        const { data } = await debtsApi.settle(id)
        _replaceDebt(data)
      }
      else if (type === 'delete_debt') {
        const { id } = payload
        if (!_isTempId(id)) {
          await debtsApi.delete(id)
        }
      }
      else if (type === 'add_payment') {
        const { debtId, payload: body } = payload
        await debtsApi.addPayment(debtId, body)
        // Refresh list
        const { data } = await debtsApi.list()
        debts.value = data
      }
      return true
    } catch (e) {
      console.error('[Sync Debts Error]', e)
      return !_isNetworkError(e)
    }
  }

  function _isTempId(id) {
    return typeof id === 'string' && id.length > 30 && debts.value.some(d => d.id === id && d.is_temp)
  }

  function _isNetworkError(error) {
    return !error.response || error.response.status >= 500 || error.code === 'ECONNABORTED'
  }

  function _replaceTempDebt(tempId, realDebt) {
    const idx = debts.value.findIndex(d => d.id === tempId)
    if (idx !== -1) {
      debts.value[idx] = realDebt
    }
  }

  function _replaceDebt(updated) {
    const idx = debts.value.findIndex((d) => d.id === updated.id)
    if (idx !== -1) debts.value[idx] = updated
  }

  function _resolveTempIdInOutbox(tempId, realId) {
    outbox.value.forEach(action => {
      if (action.payload && action.payload.debtId === tempId) {
        action.payload.debtId = realId
      }
      if (action.payload && action.payload.id === tempId) {
        action.payload.id = realId
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
    debts, loading, saving, error,
    loanModalOpen, editingLoan,
    openLoanModal, closeLoanModal,
    outbox, isSyncing, isOfflineMode, triggerSync,
    fetchDebts, createDebt, updateDebt, settleDebt, deleteDebt,
    fetchPayments, addPayment,
  }
})

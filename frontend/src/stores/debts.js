import { defineStore } from 'pinia'
import { ref } from 'vue'
import { debtsApi } from '../services/api.js'

export const useDebtsStore = defineStore('debts', () => {
  const debts   = ref([])
  const loading = ref(false)
  const saving  = ref(false)
  const error   = ref(null)

  // ── Modal state ────────────────────────────────────────────────────────────
  const loanModalOpen = ref(false)
  const editingLoan   = ref(null) // null = create, object = view/edit

  function openLoanModal(debt = null) {
    editingLoan.value   = debt
    loanModalOpen.value = true
  }

  function closeLoanModal() {
    loanModalOpen.value = false
    editingLoan.value   = null
  }

  // ── CRUD ───────────────────────────────────────────────────────────────────
  async function fetchDebts() {
    loading.value = true
    error.value = null
    try {
      const { data } = await debtsApi.list()
      debts.value = data
    } catch (e) {
      error.value = 'Não foi possível carregar as dívidas.'
      console.error(e)
    } finally {
      loading.value = false
    }
  }

  async function createDebt(payload) {
    saving.value = true
    try {
      const { data } = await debtsApi.create({
        ...payload,
        display_order: debts.value.length + 1,
      })
      debts.value.push(data)
      return data
    } finally {
      saving.value = false
    }
  }

  async function updateDebt(id, payload) {
    const idx = debts.value.findIndex((d) => d.id === id)
    try {
      const { data } = await debtsApi.update(id, payload)
      if (idx !== -1) debts.value[idx] = data
      return data
    } catch {
      await fetchDebts()
    }
  }

  async function settleDebt(id) {
    try {
      const { data } = await debtsApi.settle(id)
      const idx = debts.value.findIndex((d) => d.id === id)
      if (idx !== -1) debts.value[idx] = data
      return data
    } catch {
      await fetchDebts()
    }
  }

  async function deleteDebt(id) {
    const prev = [...debts.value]
    debts.value = debts.value.filter((d) => d.id !== id)
    try {
      await debtsApi.delete(id)
    } catch {
      debts.value = prev
    }
  }

  // ── Payments ───────────────────────────────────────────────────────────────
  async function fetchPayments(debtId) {
    const { data } = await debtsApi.listPayments(debtId)
    return data
  }

  async function addPayment(debtId, payload) {
    saving.value = true
    try {
      const { data: payment } = await debtsApi.addPayment(debtId, payload)
      // Refresh the debt to get updated estimated_amount and status
      const { data: updatedDebt } = await debtsApi.list()
      debts.value = updatedDebt
      return payment
    } finally {
      saving.value = false
    }
  }

  return {
    debts, loading, saving, error,
    loanModalOpen, editingLoan,
    openLoanModal, closeLoanModal,
    fetchDebts, createDebt, updateDebt, settleDebt, deleteDebt,
    fetchPayments, addPayment,
  }
})

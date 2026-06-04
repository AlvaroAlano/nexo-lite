import { defineStore } from 'pinia'
import { ref } from 'vue'
import { debtsApi } from '../services/api.js'

export const useDebtsStore = defineStore('debts', () => {
  const debts   = ref([])
  const loading = ref(false)
  const saving  = ref(false)
  const error   = ref(null)

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

  async function createDebt(name, estimatedAmount) {
    saving.value = true
    try {
      const { data } = await debtsApi.create({
        name,
        estimated_amount: estimatedAmount,
        display_order: debts.value.length + 1,
      })
      debts.value.push(data)
    } finally {
      saving.value = false
    }
  }

  async function updateDebt(id, estimatedAmount) {
    // Optimistic update
    const idx = debts.value.findIndex((d) => d.id === id)
    if (idx !== -1) debts.value[idx] = { ...debts.value[idx], estimated_amount: estimatedAmount }
    try {
      const { data } = await debtsApi.update(id, { estimated_amount: estimatedAmount })
      if (idx !== -1) debts.value[idx] = data
    } catch {
      await fetchDebts()
    }
  }

  async function deleteDebt(id) {
    // Optimistic delete
    const prev = [...debts.value]
    debts.value = debts.value.filter((d) => d.id !== id)
    try {
      await debtsApi.delete(id)
    } catch {
      debts.value = prev
    }
  }

  return { debts, loading, saving, error, fetchDebts, createDebt, updateDebt, deleteDebt }
})

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { vaultApi } from '../services/api.js'

export const useVaultStore = defineStore('vault', () => {
  const summary = ref(null)   // VaultSummary | null
  const loading = ref(false)
  const saving  = ref(false)
  const error   = ref(null)

  async function fetchSummary() {
    loading.value = true
    error.value = null
    try {
      const { data } = await vaultApi.getSummary()
      summary.value = data
    } catch (e) {
      error.value = 'Não foi possível carregar a Caixinha.'
      console.error(e)
    } finally {
      loading.value = false
    }
  }

  async function reconcile(realBalance) {
    saving.value = true
    try {
      await vaultApi.reconcile(realBalance)
      await fetchSummary()
    } finally {
      saving.value = false
    }
  }

  return { summary, loading, saving, error, fetchSummary, reconcile }
})

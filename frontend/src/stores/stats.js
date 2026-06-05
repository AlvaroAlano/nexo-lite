import { defineStore } from 'pinia'
import { ref } from 'vue'
import { periodsApi, templatesApi } from '../services/api.js'

export const useStatsStore = defineStore('stats', () => {
  // [{ year, month, carryover_balance, total_expenses, free_cash }]
  const history   = ref([])
  // ExpenseTemplate[] — usados para projeção futura
  const templates = ref([])
  const loading   = ref(false)
  const error     = ref(null)

  async function fetchAll() {
    loading.value = true
    error.value   = null
    try {
      const [histRes, tplRes] = await Promise.all([
        periodsApi.history(12),
        templatesApi.list(),
      ])
      history.value   = histRes.data
      templates.value = tplRes.data
    } catch (e) {
      error.value = e
      console.error('[stats store]', e)
    } finally {
      loading.value = false
    }
  }

  return { history, templates, loading, error, fetchAll }
})

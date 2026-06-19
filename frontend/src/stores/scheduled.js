import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { scheduledApi } from '../services/api.js'

export const useScheduledStore = defineStore('scheduled', () => {
  const items = ref([])
  const loading = ref(false)

  async function fetch() {
    loading.value = true
    try {
      const { data } = await scheduledApi.list()
      items.value = data
    } catch (e) {
      console.error('Erro ao buscar despesas agendadas:', e)
    } finally {
      loading.value = false
    }
  }

  async function create(payload) {
    const { data } = await scheduledApi.create(payload)
    items.value.push(data)
    return data
  }

  async function remove(id) {
    const removed = items.value.find((s) => s.id === id)
    items.value = items.value.filter((s) => s.id !== id)
    try {
      await scheduledApi.delete(id)
    } catch (e) {
      console.error('Erro ao remover agendada:', e)
      if (removed) items.value = [...items.value, removed]
    }
  }

  // Agrupado por mês alvo, ordenado cronologicamente
  const byMonth = computed(() => {
    const groups = {}
    for (const s of items.value) {
      const key = `${s.target_year}-${String(s.target_month).padStart(2, '0')}`
      ;(groups[key] ??= { year: s.target_year, month: s.target_month, items: [] }).items.push(s)
    }
    return Object.values(groups).sort((a, b) => a.year - b.year || a.month - b.month)
  })

  const count = computed(() => items.value.length)

  return { items, loading, fetch, create, remove, byMonth, count }
})

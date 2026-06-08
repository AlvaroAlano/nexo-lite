import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { categoriesApi } from '../services/api.js'
import { colorByKey } from '../utils/categories.js'

export const useCategoriesStore = defineStore('categories', () => {
  const categories = ref([])
  const loading = ref(false)

  const byId = computed(() => Object.fromEntries(categories.value.map(c => [c.id, c])))

  async function fetch(force = false) {
    if (!force && categories.value.length) return
    loading.value = true
    try {
      const { data } = await categoriesApi.list()
      categories.value = data
    } finally {
      loading.value = false
    }
  }

  function getColor(categoryId) {
    const cat = byId.value[categoryId]
    return cat ? colorByKey(cat.color) : colorByKey('slate')
  }

  function getCategory(categoryId) {
    return byId.value[categoryId] || null
  }

  async function create(payload) {
    const { data } = await categoriesApi.create(payload)
    categories.value.push(data)
    return data
  }

  async function update(id, payload) {
    const { data } = await categoriesApi.update(id, payload)
    const idx = categories.value.findIndex(c => c.id === id)
    if (idx !== -1) categories.value[idx] = data
    return data
  }

  async function remove(id) {
    await categoriesApi.delete(id)
    categories.value = categories.value.filter(c => c.id !== id)
  }

  function clear() {
    categories.value = []
  }

  return { categories, loading, byId, fetch, getColor, getCategory, create, update, remove, clear }
})


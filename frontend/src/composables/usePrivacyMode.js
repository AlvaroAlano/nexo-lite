import { ref } from 'vue'
import { formatCurrency } from '../utils/currency.js'

const STORAGE_KEY = 'nexo_privacy'
const isPrivate = ref(localStorage.getItem(STORAGE_KEY) === '1')

export function usePrivacyMode() {
  function toggle() {
    isPrivate.value = !isPrivate.value
    localStorage.setItem(STORAGE_KEY, isPrivate.value ? '1' : '0')
  }

  function maskCurrency(value) {
    return isPrivate.value ? 'R$ ••••' : formatCurrency(value)
  }

  return { isPrivate, toggle, maskCurrency }
}

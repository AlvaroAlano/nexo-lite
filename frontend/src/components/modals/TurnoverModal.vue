<template>
  <BaseModal v-model="open" title="Fechar Mês" full-screen-on-mobile>
    <div v-if="store.period" class="space-y-4 font-ss01">
      <p class="text-brand-ink-mute-light dark:text-brand-ink-mute-dark text-sm leading-relaxed">
        Ao fechar <strong class="text-brand-ink-light dark:text-white font-medium">{{ currentMonthLabel }}</strong>, o sistema vai:
      </p>

      <ul class="space-y-2 text-sm text-brand-ink-light dark:text-white">
        <li class="flex items-start gap-2">
          <span class="text-emerald-500 mt-0.5 flex-shrink-0">✓</span>
          Calcular e rolar o saldo livre para o próximo mês
        </li>
        <li class="flex items-start gap-2">
          <span class="text-emerald-500 mt-0.5 flex-shrink-0">✓</span>
          Clonar todas as despesas fixas e recorrentes
        </li>
        <li class="flex items-start gap-2">
          <span class="text-emerald-500 mt-0.5 flex-shrink-0">✓</span>
          Avançar parcelas (ex: 2/5 → 3/5) e expirar as concluídas
        </li>
      </ul>

      <!-- Carryover preview -->
      <div class="bg-brand-canvas-soft-light/50 dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark/40 rounded-xl p-4 space-y-2 text-sm mt-2">
        <p class="font-medium text-brand-ink-light dark:text-white text-xs uppercase tracking-wide">Previsão de saldo rolado</p>
        <div class="flex justify-between text-brand-ink-mute-light dark:text-brand-ink-mute-dark">
          <span>Renda + Saldo anterior</span>
          <span class="font-tabular">{{ formatCurrency(totalAvailable) }}</span>
        </div>
        <div class="flex justify-between text-brand-ink-mute-light dark:text-brand-ink-mute-dark">
          <span>Comprometido</span>
          <span class="font-tabular">− {{ formatCurrency(store.totalCommitted) }}</span>
        </div>
        <div class="border-t border-brand-hairline-light dark:border-brand-hairline-dark pt-2 flex justify-between font-semibold">
          <span class="text-brand-ink-light dark:text-white">Vai para {{ nextMonthLabel }}</span>
          <span
            class="font-tabular"
            :class="carryover >= 0 ? 'text-emerald-600' : 'text-red-500'"
          >
            {{ formatCurrency(carryover) }}
          </span>
        </div>
      </div>

      <p class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark">
        Esta ação não pode ser desfeita. Certifique-se de que os valores estão corretos.
      </p>
    </div>

    <template #footer>
      <p v-if="turnoverError" class="text-xs text-red-500 text-center mb-2">{{ turnoverError }}</p>
      <div class="flex gap-3">
        <button
          @click="open = false"
          class="flex-1 py-2.5 md:py-2 px-4 rounded-full border border-brand-hairline-light dark:border-brand-hairline-dark text-brand-ink-light dark:text-white text-sm font-medium hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark/30 active:scale-[.98] transition-all"
        >
          Cancelar
        </button>
        <button
          @click="confirm"
          :disabled="store.saving"
          class="flex-1 py-2.5 md:py-2 px-4 rounded-full bg-brand-primary hover:bg-brand-primary-hover text-white text-sm font-medium active:scale-[.98] transition-all disabled:opacity-50"
        >
          {{ store.saving ? 'Fechando…' : 'Confirmar Virada' }}
        </button>
      </div>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed, ref } from 'vue'
import BaseModal from '../ui/BaseModal.vue'
import { useDashboardStore } from '../../stores/dashboard.js'
import { formatCurrency } from '../../utils/currency.js'
import { monthLabel } from '../../utils/date.js'

const props = defineProps({ modelValue: Boolean })
const emit = defineEmits(['update:modelValue'])

const store = useDashboardStore()

const open = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const currentMonthLabel = computed(() =>
  store.period ? monthLabel(store.period.year, store.period.month) : ''
)

const nextMonthLabel = computed(() => {
  if (!store.period) return ''
  let { year, month } = store.period
  month = month === 12 ? 1 : month + 1
  year = store.period.month === 12 ? year + 1 : year
  return monthLabel(year, month)
})

const totalAvailable = computed(() => {
  if (!store.period) return 0
  return store.incomeAlvaro + store.incomeAlexandra + (parseFloat(store.period.carryover_balance) || 0)
})

const carryover = computed(() =>
  Math.max(0, totalAvailable.value - store.totalCommitted)
)

const turnoverError = ref(null)

async function confirm() {
  turnoverError.value = null
  try {
    await store.runTurnover()
    open.value = false
  } catch (e) {
    turnoverError.value = e.response?.data?.detail || 'Não foi possível fechar o mês.'
  }
}
</script>

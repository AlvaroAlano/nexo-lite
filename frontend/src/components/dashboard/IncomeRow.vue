<!-- Editable income row used inside BalanceSummary -->
<template>
  <div class="flex items-center justify-between">
    <span class="text-brand-ink-mute-dark text-sm">{{ label }}</span>
    <span
      v-if="!editing"
      @click="!readonly && startEdit()"
      class="font-tabular font-medium text-white text-sm transition-colors"
      :class="!readonly ? 'cursor-pointer hover:text-brand-primary-soft' : ''"
    >
      {{ formatCurrency(value) }}
    </span>
    <CurrencyInput
      v-else
      ref="inputRef"
      :model-value="raw"
      @update:model-value="raw = $event"
      @confirm="save"
      @cancel="cancel"
      hide-prefix
      input-class="bg-transparent border-b border-brand-primary focus:border-brand-primary-soft outline-none w-32 text-right font-tabular font-medium text-white text-sm"
    />
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useDashboardStore } from '../../stores/dashboard.js'
import { formatCurrency } from '../../utils/currency.js'
import CurrencyInput from '../ui/CurrencyInput.vue'

const props = defineProps({
  label: String,
  value: Number,
  field: String,   // 'income_alvaro' | 'income_alexandra'
  readonly: Boolean,
})

const store = useDashboardStore()
const editing = ref(false)
const raw = ref(0)
const inputRef = ref(null)

function startEdit() {
  raw.value = props.value || 0
  editing.value = true
  nextTick(() => inputRef.value?.focus())
}

async function save() {
  editing.value = false
  await store.updateIncome(props.field, raw.value)
}

function cancel() {
  editing.value = false
}
</script>

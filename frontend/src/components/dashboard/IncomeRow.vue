<!-- Editable income row used inside BalanceSummary -->
<template>
  <div class="flex items-center justify-between">
    <span class="text-brand-ink-mute-dark text-sm">{{ label }}</span>
    <span
      v-if="!editing"
      @click="!readonly && !hidden && startEdit()"
      class="font-tabular font-medium text-white text-sm transition-colors select-none"
      :class="!readonly && !hidden ? 'cursor-pointer hover:text-brand-primary-soft' : ''"
    >
      <span v-if="hidden" class="tracking-widest opacity-50">••••••</span>
      <span v-else>{{ maskCurrency(value) }}</span>
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
import { usePrivacyMode } from '../../composables/usePrivacyMode.js'
import CurrencyInput from '../ui/CurrencyInput.vue'

const { maskCurrency } = usePrivacyMode()

const props = defineProps({
  label: String,
  value: Number,
  field: String,
  readonly: Boolean,
  hidden: { type: Boolean, default: false },
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

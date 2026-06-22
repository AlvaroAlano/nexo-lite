<!-- Editable income row used inside BalanceSummary -->
<template>
  <div class="flex items-center justify-between py-0.5">
    <span class="text-brand-ink-mute-dark text-sm">{{ label }}</span>
    <span
      v-if="!editing"
      @click="!readonly && !hidden && startEdit()"
      class="font-tabular font-medium text-sm transition-colors select-none"
      :class="[
        !readonly && !hidden ? 'cursor-pointer hover:text-brand-primary-soft' : '',
        valueClass || 'text-white'
      ]"
    >
      <span v-if="hidden" class="tracking-widest opacity-50">••••••</span>
      <span v-else>{{ prefix }}{{ maskCurrency(value) }}</span>
    </span>
    <div v-else class="flex items-center gap-1.5" @click.stop>
      <CurrencyInput
        ref="inputRef"
        :model-value="raw"
        @update:model-value="raw = $event"
        @confirm="save"
        @cancel="cancel"
        @blur="handleBlur"
        hide-prefix
        input-class="bg-transparent border-b border-brand-primary focus:border-brand-primary-soft outline-none w-24 text-right font-tabular font-medium text-white text-sm"
      />
      <button
        @mousedown.prevent
        @click="save"
        class="w-6 h-6 flex items-center justify-center rounded-full bg-emerald-500 hover:bg-emerald-600 text-white transition-all active:scale-95 duration-200"
        :class="{ 'animate-check-pop': animating }"
        title="Confirmar"
      >
        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
      </button>
    </div>
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
  prefix: { type: String, default: '' },
  valueClass: { type: String, default: '' },
})

const store = useDashboardStore()
const editing = ref(false)
const animating = ref(false)
const raw = ref(0)
const inputRef = ref(null)

function startEdit() {
  raw.value = props.value || 0
  editing.value = true
  nextTick(() => inputRef.value?.focus())
}

function handleBlur() {
  setTimeout(() => {
    if (editing.value && !animating.value) {
      cancel()
    }
  }, 180)
}

async function save() {
  if (animating.value) return
  animating.value = true
  
  setTimeout(async () => {
    try {
      await store.updateIncome(props.field, raw.value)
    } finally {
      editing.value = false
      animating.value = false
    }
  }, 300)
}

function cancel() {
  editing.value = false
}
</script>

<style scoped>
@keyframes check-pop-out {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.35);
    opacity: 0.8;
  }
  100% {
    transform: scale(1.6);
    opacity: 0;
  }
}
.animate-check-pop {
  animation: check-pop-out 300ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
</style>

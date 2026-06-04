<template>
  <div class="relative">
    <span
      v-if="!hidePrefix"
      class="absolute left-3 top-1/2 -translate-y-1/2 text-brand-ink-mute-light dark:text-brand-ink-mute-dark text-sm font-mono pointer-events-none select-none"
    >R$</span>
    <input
      ref="inputRef"
      v-bind="$attrs"
      type="text"
      inputmode="numeric"
      autocomplete="off"
      :value="display"
      :class="[inputClass, 'font-tabular border-0 focus:ring-0 outline-none', hidePrefix ? '' : 'pl-10']"
      @focus="onFocus"
      @input="onInput"
      @keydown.enter="$emit('confirm')"
      @keydown.escape="$emit('cancel')"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  modelValue: { type: Number, default: 0 },
  inputClass: { type: String, default: '' },
  hidePrefix: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const inputRef = ref(null)

// Store value as integer cents to avoid float drift
const cents = ref(toCents(props.modelValue))

// Focus expose helper that handles component wrapping
function focus() {
  const el = inputRef.value
  if (el) {
    el.focus()
    nextTick(() => el.setSelectionRange(el.value.length, el.value.length))
  }
}

function toCents(v) {
  return Math.round((parseFloat(v) || 0) * 100)
}

function format(c) {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(c / 100)
}

const display = computed(() => format(cents.value))

function onFocus(e) {
  nextTick(() => e.target.setSelectionRange(e.target.value.length, e.target.value.length))
}

function onInput(e) {
  const digits = e.target.value.replace(/\D/g, '')
  cents.value = parseInt(digits || '0', 10)
  emit('update:modelValue', cents.value / 100)
  // Reapply formatted value and keep cursor at end
  nextTick(() => {
    e.target.value = format(cents.value)
    e.target.setSelectionRange(e.target.value.length, e.target.value.length)
  })
}

// Sync if parent changes value externally
watch(() => props.modelValue, (v) => {
  const c = toCents(v)
  if (c !== cents.value) cents.value = c
})

defineExpose({ focus, select: () => inputRef.value?.select() })
</script>

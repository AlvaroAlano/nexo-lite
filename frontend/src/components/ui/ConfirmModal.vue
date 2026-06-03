<template>
  <BaseModal v-model="open" :title="title">
    <p class="text-sm text-brand-ink-mute-light dark:text-brand-ink-mute-dark leading-relaxed">{{ message }}</p>

    <template #footer>
      <div class="flex gap-3">
        <button
          @click="open = false"
          class="flex-1 py-2.5 md:py-2 px-4 rounded-full border border-brand-hairline-light dark:border-brand-hairline-dark text-brand-ink-light dark:text-white text-sm font-medium hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark/20 active:scale-[.98] transition-all"
        >
          {{ cancelLabel }}
        </button>
        <button
          @click="confirm"
          :class="variant === 'danger'
            ? 'bg-red-600 hover:bg-red-700 text-white'
            : 'bg-brand-primary hover:bg-brand-primary-hover text-white'"
          class="flex-1 py-2.5 md:py-2 px-4 rounded-full text-sm font-medium active:scale-[.98] transition-all"
        >
          {{ confirmLabel }}
        </button>
      </div>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed } from 'vue'
import BaseModal from './BaseModal.vue'

const props = defineProps({
  modelValue: Boolean,
  title: { type: String, default: 'Confirmar' },
  message: { type: String, default: 'Tem certeza?' },
  confirmLabel: { type: String, default: 'Confirmar' },
  cancelLabel: { type: String, default: 'Cancelar' },
  variant: { type: String, default: 'danger' }, // 'danger' | 'default'
})
const emit = defineEmits(['update:modelValue', 'confirm'])

const open = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

function confirm() {
  emit('confirm')
  open.value = false
}
</script>

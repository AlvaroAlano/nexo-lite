<template>
  <BaseModal v-model="open" :title="title">
    <p class="text-sm text-brand-ink-mute-light dark:text-brand-ink-mute-dark leading-relaxed">{{ message }}</p>
    <p v-if="errorMessage" class="text-red-500 dark:text-red-400 text-xs mt-2">{{ errorMessage }}</p>

    <template #footer>
      <div class="flex gap-3">
        <button
          @click="open = false"
          :disabled="loading"
          class="flex-1 py-2.5 md:py-2 px-4 rounded-full border border-brand-hairline-light dark:border-brand-hairline-dark text-brand-ink-light dark:text-white text-sm font-medium hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark/20 active:scale-[.98] transition-all disabled:opacity-40"
        >
          {{ cancelLabel }}
        </button>
        <button
          @click="confirm"
          :disabled="loading"
          :class="variant === 'danger'
            ? 'bg-red-600 hover:bg-red-700 text-white'
            : 'bg-brand-primary hover:bg-brand-primary-hover text-white'"
          class="flex-1 py-2.5 md:py-2 px-4 rounded-full text-sm font-medium active:scale-[.98] transition-all disabled:opacity-40"
        >
          {{ loading ? 'Aguarde…' : confirmLabel }}
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
  // Controlados pelo chamador: mantém o modal aberto e trava os botões
  // enquanto a ação assíncrona do @confirm está em andamento, e mostra o
  // erro em vez de fechar como se tivesse dado certo.
  loading: { type: Boolean, default: false },
  errorMessage: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue', 'confirm'])

const open = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

function confirm() {
  emit('confirm')
  // Não fecha mais sozinho — quem chama fecha (open = false) após o handler
  // do @confirm resolver com sucesso. Em caso de erro, o modal permanece
  // aberto mostrando `errorMessage`.
}
</script>

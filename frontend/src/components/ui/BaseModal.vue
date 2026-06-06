<template>
  <Teleport to="body">
    <Transition name="modal-backdrop">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex justify-center"
        :class="fullScreenOnMobile ? 'items-end md:items-center' : 'items-center p-4'"
        @click.self="close"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-brand-ink-light/40 dark:bg-black/70 backdrop-blur-sm"
          @click="close"
        />

        <!-- Panel -->
        <Transition :name="fullScreenOnMobile ? 'modal-sheet' : 'modal-center'">
          <div
            v-if="modelValue"
            class="relative z-10 bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark shadow-stripe-2 flex flex-col transition-colors duration-150"
            :class="fullScreenOnMobile
              ? 'w-full h-full md:h-auto md:max-w-md md:rounded-stripe-card'
              : 'w-full max-w-md rounded-stripe-card h-auto'"
          >
            <!-- Header -->
            <div class="flex items-center justify-between pl-5 pr-3 md:px-5 py-4 border-b border-brand-hairline-light dark:border-brand-hairline-dark flex-shrink-0">
              <h2 class="font-medium tracking-tight text-brand-ink-light dark:text-white text-base">{{ title }}</h2>
              <button
                @click="close"
                aria-label="Fechar"
                class="w-11 h-11 md:w-8 md:h-8 flex items-center justify-center rounded-xl
                       text-brand-ink-mute-light dark:text-brand-ink-mute-dark
                       hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark/30
                       hover:text-brand-ink-light dark:hover:text-white
                       active:scale-90 active:bg-brand-canvas-soft-light dark:active:bg-brand-canvas-soft-dark/30
                       transition-all flex-shrink-0"
              >
                <svg class="w-5 h-5 md:w-4 md:h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>

            <!-- Content -->
            <div class="flex-1 overflow-y-auto px-5 py-5 text-brand-ink-light dark:text-white text-sm">
              <slot />
            </div>

            <!-- Footer -->
            <div
              v-if="$slots.footer"
              class="px-5 pt-4 pb-5 flex-shrink-0"
              :class="fullScreenOnMobile
                ? 'border-t border-brand-hairline-light dark:border-brand-hairline-dark/40 bg-brand-canvas-soft-light/20 dark:bg-brand-canvas-soft-dark/40 md:bg-transparent md:border-t-0 md:pt-1'
                : 'pt-1'"
              :style="fullScreenOnMobile
                ? 'padding-bottom: max(1.5rem, calc(env(safe-area-inset-bottom, 0px) + 1.25rem))'
                : ''"
            >
              <slot name="footer" />
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { watch, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  title: { type: String, default: '' },
  fullScreenOnMobile: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])

function close() {
  emit('update:modelValue', false)
}

watch(() => props.modelValue, (isOpen) => {
  document.body.classList.toggle('overflow-hidden', isOpen)
}, { immediate: true })

onUnmounted(() => {
  document.body.classList.remove('overflow-hidden')
})
</script>

<style scoped>
/* ── Backdrop ───────────────────────────────────────────────── */
.modal-backdrop-enter-active { transition: opacity 280ms ease-out; }
.modal-backdrop-leave-active { transition: opacity 220ms ease-in; }
.modal-backdrop-enter-from,
.modal-backdrop-leave-to    { opacity: 0; }

/* ── Bottom sheet (mobile) — spring physics ─────────────────── */
.modal-sheet-enter-active { transition: transform 420ms cubic-bezier(0.32, 0.72, 0, 1); }
.modal-sheet-leave-active { transition: transform 280ms cubic-bezier(0.4, 0, 1, 1); }
.modal-sheet-enter-from,
.modal-sheet-leave-to     { transform: translateY(100%); }

/* Desktop override: sheet becomes centered scale+fade */
@media (min-width: 768px) {
  .modal-sheet-enter-active { transition: opacity 200ms ease-out, transform 220ms ease-out; }
  .modal-sheet-leave-active { transition: opacity 160ms ease-in,  transform 160ms ease-in; }
  .modal-sheet-enter-from,
  .modal-sheet-leave-to     { opacity: 0; transform: scale(0.96) translateY(6px); }
}

/* ── Centered modal (non-sheet) ─────────────────────────────── */
.modal-center-enter-active { transition: opacity 200ms ease-out, transform 220ms ease-out; }
.modal-center-leave-active { transition: opacity 160ms ease-in,  transform 160ms ease-in; }
.modal-center-enter-from,
.modal-center-leave-to     { opacity: 0; transform: scale(0.96) translateY(6px); }
</style>

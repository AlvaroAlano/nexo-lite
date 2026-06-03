<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-200"
      leave-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex justify-center transition-all"
        :class="fullScreenOnMobile ? 'items-end md:items-center p-0 md:p-4' : 'items-center p-4'"
        @click.self="$emit('update:modelValue', false)"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-brand-ink-light/40 dark:bg-black/70 backdrop-blur-sm" @click="$emit('update:modelValue', false)" />

        <!-- Panel: full screen on mobile, centered dialog on desktop -->
        <Transition
          :enter-active-class="fullScreenOnMobile ? 'transition-transform duration-300 ease-out md:transition-all md:duration-200' : 'transition-all duration-200 ease-out'"
          :leave-active-class="fullScreenOnMobile ? 'transition-transform duration-200 ease-in md:transition-all md:duration-150' : 'transition-all duration-150 ease-in'"
          :enter-from-class="fullScreenOnMobile ? 'translate-y-full md:translate-y-0 md:scale-95 md:opacity-0' : 'scale-95 opacity-0'"
          :leave-to-class="fullScreenOnMobile ? 'translate-y-full md:translate-y-0 md:scale-95 md:opacity-0' : 'scale-95 opacity-0'"
        >
          <div
            v-if="modelValue"
            class="relative z-10 bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark shadow-stripe-2 flex flex-col transition-colors duration-150"
            :class="fullScreenOnMobile ? 'w-full h-full md:h-auto md:max-w-md md:rounded-stripe-card' : 'w-full max-w-md rounded-stripe-card h-auto'"
          >
            <!-- Header -->
            <div class="flex items-center justify-between px-5 py-4 border-b border-brand-hairline-light dark:border-brand-hairline-dark flex-shrink-0">
              <h2 class="font-light tracking-tight text-brand-ink-light dark:text-white text-base">{{ title }}</h2>
              <button
                @click="$emit('update:modelValue', false)"
                class="w-8 h-8 flex items-center justify-center rounded-lg text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark/30 hover:text-brand-ink-light dark:hover:text-white transition-colors"
              >
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>

            <!-- Content -->
            <div class="flex-1 overflow-y-auto px-5 py-6 text-brand-ink-light dark:text-white text-sm">
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
defineEmits(['update:modelValue'])

watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    document.body.classList.add('overflow-hidden')
  } else {
    document.body.classList.remove('overflow-hidden')
  }
}, { immediate: true })

onUnmounted(() => {
  document.body.classList.remove('overflow-hidden')
})
</script>

<template>
  <div class="max-w-2xl mx-auto px-4 pt-12 pb-6 font-ss01 flex flex-col items-center justify-center min-h-[40vh]">
    <div class="w-14 h-14 rounded-2xl bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark flex items-center justify-center mb-4">
      <BarChart2 class="text-brand-ink-mute-light dark:text-brand-ink-mute-dark" :size="28" stroke-width="1.5" />
    </div>
    <p class="font-semibold text-brand-ink-light dark:text-white">Estatísticas</p>
    <p class="text-sm text-brand-ink-mute-light dark:text-brand-ink-mute-dark mt-1">Em breve</p>
  </div>
</template>

<script setup>
import { BarChart2 } from 'lucide-vue-next'
</script>

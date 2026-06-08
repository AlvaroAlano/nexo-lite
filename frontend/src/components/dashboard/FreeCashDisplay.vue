<!-- Hero "livre" display — reused in all three views -->
<template>
  <div
    class="rounded-xl p-4 text-center mt-4 transition-all duration-150"
    :class="value >= 0 ? 'bg-zinc-900 border border-zinc-800' : 'bg-red-950/20 border border-red-900/30'"
  >
    <p class="text-brand-ink-mute-dark text-[10px] font-semibold uppercase tracking-wider mb-1.5">{{ label }}</p>
    <p
      class="text-3xl md:text-4xl font-light font-tabular tracking-tight transition-colors"
      :class="value >= 0 ? 'text-brand-primary dark:text-emerald-400' : 'text-red-400'"
      style="letter-spacing: -1.2px;"
    >
      {{ maskCurrency(value) }}
    </p>
    <p v-if="value < 0" class="text-red-400 text-xs mt-1">
      Despesas excedem a renda disponível
    </p>
  </div>
</template>

<script setup>
import { usePrivacyMode } from '../../composables/usePrivacyMode.js'
const { maskCurrency } = usePrivacyMode()
defineProps({
  value: { type: Number, default: 0 },
  label: { type: String, default: 'Livre' },
})
</script>

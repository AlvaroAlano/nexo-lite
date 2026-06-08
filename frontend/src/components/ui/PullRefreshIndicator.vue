<template>
  <div
    class="flex justify-center items-center overflow-hidden transition-all duration-200 pointer-events-none md:hidden rounded-xl"
    :style="{
      height: `${pullDistance}px`,
      opacity: pullDistance > 0 ? 1 : 0,
      marginBottom: pullDistance > 0 ? '12px' : '0px'
    }"
  >
    <div class="flex items-center gap-2 py-2">
      <svg
        v-if="refreshing"
        class="w-5 h-5 text-brand-primary animate-spin"
        viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"
      >
        <path d="M21 12a9 9 0 11-6.21-8.56" />
      </svg>
      <svg
        v-else
        class="w-5 h-5 text-brand-ink-mute-light dark:text-brand-ink-mute-dark transition-transform"
        :style="{ transform: `rotate(${Math.min(pullDistance * 4, 180)}deg)` }"
        viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
        stroke-linecap="round" stroke-linejoin="round"
      >
        <line x1="12" y1="5" x2="12" y2="19" />
        <polyline points="19 12 12 19 5 12" />
      </svg>
      <span class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark font-medium">
        {{ refreshing ? 'Atualizando...' : (pullDistance >= 45 ? 'Solte para atualizar' : 'Puxe para atualizar') }}
      </span>
    </div>
  </div>
</template>

<script setup>
defineProps({ pullDistance: Number, refreshing: Boolean })
</script>

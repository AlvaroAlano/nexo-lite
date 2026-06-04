<template>
  <div class="rounded-stripe-card bg-brand-canvas-light dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark shadow-stripe-1 p-5">
    <div class="mb-4">
      <p class="text-sm font-semibold text-brand-ink-light dark:text-white leading-tight">{{ title }}</p>
      <p v-if="subtitle" class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark mt-0.5 leading-tight">{{ subtitle }}</p>
    </div>
    <slot />
  </div>
</template>

<script setup>
defineProps({ title: String, subtitle: String })
</script>

<template>
  <div class="font-ss01 space-y-3">

    <!-- Labels proporcionais às fatias -->
    <div class="flex">
      <div
        v-for="seg in segments"
        :key="seg.key"
        :style="{ flex: seg.pct }"
        class="min-w-0 px-0.5 transition-opacity duration-150"
        :class="hovered && hovered !== seg.key ? 'opacity-30' : 'opacity-100'"
      >
        <p class="text-[11px] font-semibold truncate leading-tight" :class="seg.textClass">{{ seg.label }}</p>
        <p class="text-[11px] tabular-nums text-brand-ink-mute-light dark:text-brand-ink-mute-dark leading-tight">{{ seg.pct }}%</p>
        <!-- Valor só aparece no hover/touch para não truncar em segmentos pequenos -->
        <p
          v-if="hovered === seg.key"
          class="text-[11px] tabular-nums font-mono text-brand-ink-light dark:text-white leading-tight"
        >{{ fmt(seg.amount) }}</p>
      </div>
    </div>

    <!-- Barra empilhada -->
    <div
      class="flex h-6 rounded-full overflow-hidden"
      @mouseleave="hovered = null"
      @touchstart.stop="hovered = null"
    >
      <div
        v-for="seg in segments"
        :key="seg.key"
        :style="{ flex: seg.pct, backgroundColor: seg.color }"
        class="transition-opacity duration-150 cursor-default"
        :class="hovered && hovered !== seg.key ? 'opacity-25' : 'opacity-100'"
        @mouseenter="hovered = seg.key"
        @touchstart.prevent.stop="hovered = hovered === seg.key ? null : seg.key"
      />
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  data: { type: Object, required: true },
})

const hovered = ref(null)

const CONFIG = {
  alvaro:    { color: '#6366f1', textClass: 'text-brand-primary dark:text-brand-primary-soft' },
  alexandra: { color: '#f472b6', textClass: 'text-pink-500 dark:text-pink-400' },
  conjunto:  { color: '#64748b', textClass: 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark' },
}

const total = computed(() =>
  Object.values(props.data).reduce((s, v) => s + v.amount, 0)
)

const segments = computed(() =>
  Object.entries(props.data).map(([key, val]) => ({
    key,
    label: val.label,
    amount: val.amount,
    pct: total.value > 0 ? Math.round((val.amount / total.value) * 100) : 0,
    color: CONFIG[key]?.color ?? '#94a3b8',
    textClass: CONFIG[key]?.textClass ?? 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark',
  }))
)

const fmt = (n) => n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
</script>

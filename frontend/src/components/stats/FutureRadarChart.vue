<template>
  <div class="relative font-ss01">

    <!-- SVG das barras -->
    <svg
      :viewBox="`0 0 ${W} ${H}`"
      class="w-full overflow-visible"
      :style="{ height: '160px' }"
      @mouseleave="hovered = null"
    >
      <g v-for="(bar, i) in bars" :key="i">
        <!-- Barra -->
        <rect
          :x="bar.x"
          :y="bar.y"
          :width="barW"
          :height="bar.h"
          rx="4"
          :fill="BAR_COLOR"
          :opacity="hovered !== null && hovered !== i ? 0.3 : 1"
          class="transition-opacity duration-150 cursor-default"
          @mouseenter="hovered = i"
          @touchstart.prevent="hovered = hovered === i ? null : i"
        />

        <!-- Rótulo do mês (eixo X) -->
        <text
          :x="bar.x + barW / 2"
          :y="H - 2"
          text-anchor="middle"
          class="text-[9px] fill-current"
          :class="i === 0
            ? 'text-brand-ink-light dark:text-white font-semibold'
            : 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark'"
          font-size="9"
        >{{ bar.label }}</text>
      </g>
    </svg>

    <!-- Tooltip -->
    <Transition name="fade">
      <div
        v-if="hovered !== null"
        class="absolute pointer-events-none z-10 px-2.5 py-1.5 rounded-xl bg-brand-ink-light dark:bg-brand-canvas-soft-dark border border-brand-hairline-dark/20 dark:border-brand-hairline-dark shadow-stripe-2"
        :style="tooltipStyle"
      >
        <p class="text-[11px] font-semibold text-white dark:text-white whitespace-nowrap">{{ bars[hovered]?.label }}</p>
        <p class="text-[11px] tabular-nums font-mono text-brand-primary-soft whitespace-nowrap">{{ fmt(bars[hovered]?.value) }}</p>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  data: { type: Array, required: true }, // [{ month: 'Jun', value: 8500 }, ...]
})

const BAR_COLOR = '#6366f1'
const W = 280
const H = 160
const PADDING_TOP = 12
const LABEL_H = 14    // espaço para o label do mês
const CHART_H = H - PADDING_TOP - LABEL_H
const GAP = 6

const hovered = ref(null)

const barW = computed(() => {
  const n = props.data.length
  return Math.floor((W - GAP * (n + 1)) / n)
})

const maxVal = computed(() => Math.max(...props.data.map((d) => d.value), 1))

const bars = computed(() =>
  props.data.map((d, i) => {
    const h = Math.round((d.value / maxVal.value) * CHART_H)
    const x = GAP + i * (barW.value + GAP)
    const y = PADDING_TOP + (CHART_H - h)
    return { x, y, h, label: d.month, value: d.value }
  })
)

// Posiciona o tooltip acima da barra — flip nas bordas para não vazar
const tooltipStyle = computed(() => {
  if (hovered.value === null) return {}
  const bar = bars.value[hovered.value]
  const svgPct = (bar.x + barW.value / 2) / W
  let transform = 'translateX(-50%)'
  if (svgPct < 0.2) transform = 'translateX(0)'
  if (svgPct > 0.8) transform = 'translateX(-100%)'
  return {
    bottom: `${H - bar.y + 8}px`,
    left: `${svgPct * 100}%`,
    transform,
  }
})

const fmt = (n) =>
  (n ?? 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 100ms ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>

<template>
  <div class="font-ss01">

    <!-- Empty state -->
    <div v-if="!data.length" class="flex flex-col items-center justify-center py-8 gap-2">
      <PiggyBank :size="28" class="text-brand-ink-mute-light dark:text-brand-ink-mute-dark opacity-40" />
      <p class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark text-center">
        Nenhum aporte registrado ainda.<br>Dê o check na despesa "Caixinha" para começar.
      </p>
    </div>

    <div v-else class="relative" @mouseleave="hovered = null">
      <svg
        :viewBox="`0 0 ${W} ${H + LABEL_H}`"
        class="w-full overflow-visible"
        style="height: 120px;"
        @mousemove="onMove"
        @touchmove.prevent="onTouch"
        @touchend="hovered = null"
      >
        <!-- Bars -->
        <g v-for="(b, i) in bars" :key="i">
          <rect
            :x="b.x"
            :y="b.y"
            :width="BAR_W"
            :height="b.h"
            rx="3"
            :class="hovered === i
              ? 'fill-emerald-400'
              : 'fill-emerald-500/60'"
            class="transition-colors duration-100 cursor-pointer"
            @mouseenter="hovered = i"
          />
          <!-- Month label -->
          <text
            :x="b.x + BAR_W / 2"
            :y="H + LABEL_H - 1"
            text-anchor="middle"
            font-size="9"
            class="fill-brand-ink-mute-light dark:fill-brand-ink-mute-dark"
          >{{ b.label }}</text>
        </g>
      </svg>

      <!-- Tooltip -->
      <Transition name="fade">
        <div
          v-if="hovered !== null"
          class="absolute pointer-events-none z-10 px-2.5 py-2 rounded-xl bg-brand-ink-light dark:bg-brand-canvas-soft-dark border border-brand-hairline-dark/20 dark:border-brand-hairline-dark shadow-stripe-2"
          :style="tooltipStyle"
        >
          <p class="text-[10px] font-semibold text-white mb-0.5">{{ bars[hovered]?.labelFull }}</p>
          <p class="text-[11px] tabular-nums font-mono text-emerald-400">{{ fmt(data[hovered]?.amount) }}</p>
        </div>
      </Transition>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { PiggyBank } from 'lucide-vue-next'

const props = defineProps({
  data: {
    type: Array,
    required: true,
    // [{ year, month, amount }, ...]
  },
})

const W       = 280
const H       = 96
const LABEL_H = 14
const BAR_W   = 20
const PAD_X   = 12
const PAD_TOP = 6

const MONTHS_PT = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']

const hovered = ref(null)

const maxAmount = computed(() => Math.max(...props.data.map((d) => d.amount), 1))

const step = computed(() => {
  const n = props.data.length
  return n > 1 ? (W - PAD_X * 2 - BAR_W) / (n - 1) : 0
})

const bars = computed(() =>
  props.data.map((d, i) => {
    const barH = Math.max(4, ((d.amount / maxAmount.value) * (H - PAD_TOP)))
    return {
      x: PAD_X + i * step.value,
      y: H - barH,
      h: barH,
      label: MONTHS_PT[(d.month - 1)],
      labelFull: `${MONTHS_PT[(d.month - 1)]} ${d.year}`,
    }
  })
)

const tooltipStyle = computed(() => {
  if (hovered.value === null) return {}
  const b = bars.value[hovered.value]
  const pct = ((b.x + BAR_W / 2) / W) * 100
  return {
    bottom: `${(H - b.y) + 10}px`,
    left: `${pct}%`,
    transform: pct > 65 ? 'translateX(-100%)' : 'translateX(-30%)',
  }
})

const findClosest = (clientX, rect) => {
  const svgX = ((clientX - rect.left) / rect.width) * W
  let closest = 0, minDist = Infinity
  bars.value.forEach((b, i) => {
    const d = Math.abs(b.x + BAR_W / 2 - svgX)
    if (d < minDist) { minDist = d; closest = i }
  })
  hovered.value = closest
}

const onMove  = (e) => findClosest(e.clientX, e.currentTarget.getBoundingClientRect())
const onTouch = (e) => findClosest(e.touches[0].clientX, e.currentTarget.getBoundingClientRect())

const fmt = (n) => (n ?? 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 100ms ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>

<template>
  <div class="font-ss01 space-y-3">

    <!-- Valor em destaque: Free Cash do mês mais recente -->
    <div>
      <p class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark">Saldo Livre Médio</p>
      <p class="text-2xl font-bold tabular-nums font-mono" :class="avgFreeCash >= 0 ? 'text-emerald-500' : 'text-red-500'">
        {{ fmt(avgFreeCash) }}
      </p>
    </div>

    <!-- SVG de área dupla -->
    <div class="relative" @mouseleave="hovered = null">
      <svg
        :viewBox="`0 0 ${W} ${H}`"
        class="w-full overflow-visible"
        style="height: 110px"
        @mousemove="onMove"
        @touchmove.prevent="onTouch"
        @touchend="hovered = null"
      >
        <defs>
          <linearGradient :id="gradFree" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#6366f1" stop-opacity="0.25" />
            <stop offset="100%" stop-color="#6366f1" stop-opacity="0" />
          </linearGradient>
          <linearGradient :id="gradCarry" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#10b981" stop-opacity="0.18" />
            <stop offset="100%" stop-color="#10b981" stop-opacity="0" />
          </linearGradient>
        </defs>

        <!-- Área Carryover (atrás) -->
        <path :d="carryoverAreaPath" :fill="`url(#${gradCarry})`" />
        <path :d="carryoverLinePath" fill="none" stroke="#10b981" stroke-width="1.5" stroke-linejoin="round" />

        <!-- Área Free Cash (frente) -->
        <path :d="freeCashAreaPath" :fill="`url(#${gradFree})`" />
        <path :d="freeCashLinePath" fill="none" stroke="#6366f1" stroke-width="2" stroke-linejoin="round" />

        <!-- Labels do eixo X -->
        <text
          v-for="(p, i) in points"
          :key="`lbl-${i}`"
          :x="p.x"
          :y="H + 1"
          text-anchor="middle"
          font-size="9"
          class="fill-brand-ink-mute-light dark:fill-brand-ink-mute-dark"
        >{{ p.month }}</text>

        <!-- Linha vertical de hover -->
        <line
          v-if="hovered !== null"
          :x1="points[hovered]?.x"
          :x2="points[hovered]?.x"
          y1="0"
          :y2="H - 2"
          stroke-width="1"
          stroke-dasharray="3 2"
          class="stroke-brand-hairline-light dark:stroke-brand-hairline-dark"
        />

        <!-- Pontos de hover -->
        <template v-if="hovered !== null">
          <circle :cx="points[hovered].x" :cy="points[hovered].freeCashY" r="3" fill="#6366f1" />
          <circle :cx="points[hovered].x" :cy="points[hovered].carryoverY" r="3" fill="#10b981" />
        </template>
      </svg>

      <!-- Tooltip -->
      <Transition name="fade">
        <div
          v-if="hovered !== null"
          class="absolute pointer-events-none z-10 px-2.5 py-2 rounded-xl bg-brand-ink-light dark:bg-brand-canvas-soft-dark border border-brand-hairline-dark/20 dark:border-brand-hairline-dark shadow-stripe-2 space-y-0.5"
          :style="tooltipStyle"
        >
          <p class="text-[10px] font-semibold text-white dark:text-white mb-1">{{ points[hovered]?.month }}</p>
          <div class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-brand-primary flex-shrink-0" />
            <span class="text-[10px] tabular-nums font-mono text-white">{{ fmt(data[hovered]?.freeCash) }}</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-emerald-500 flex-shrink-0" />
            <span class="text-[10px] tabular-nums font-mono text-white">{{ fmt(data[hovered]?.carryover) }}</span>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Legenda -->
    <div class="flex gap-5">
      <div class="flex items-center gap-1.5">
        <span class="w-2.5 h-0.5 rounded-full bg-brand-primary" />
        <span class="text-[11px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark">Free Cash</span>
      </div>
      <div class="flex items-center gap-1.5">
        <span class="w-2.5 h-0.5 rounded-full bg-emerald-500" />
        <span class="text-[11px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark">Carryover</span>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  data: {
    type: Array,
    required: true,
    // [{ month: 'Jan', freeCash: 2000, carryover: 500 }, ...]
  },
})

const W = 280
const H = 96   // altura útil do gráfico (sem label eixo X)
const PAD_X = 16
const PAD_TOP = 8

// IDs únicos para os gradientes (evita colisão se houver múltiplas instâncias)
const uid = Math.random().toString(36).slice(2, 7)
const gradFree  = `grad-free-${uid}`
const gradCarry = `grad-carry-${uid}`

const hovered = ref(null)

const avgFreeCash = computed(() => {
  if (!props.data.length) return 0
  return Math.round(props.data.reduce((s, d) => s + d.freeCash, 0) / props.data.length)
})

const allValues = computed(() =>
  props.data.flatMap((d) => [d.freeCash, d.carryover])
)
const minVal = computed(() => Math.min(...allValues.value, 0))
const maxVal = computed(() => Math.max(...allValues.value, 1))
const range  = computed(() => maxVal.value - minVal.value || 1)

const toY = (v) =>
  PAD_TOP + ((maxVal.value - v) / range.value) * (H - PAD_TOP)

const stepX = computed(() => {
  const n = props.data.length
  return n > 1 ? (W - PAD_X * 2) / (n - 1) : 0
})

const points = computed(() =>
  props.data.map((d, i) => ({
    x: PAD_X + i * stepX.value,
    freeCashY:  toY(d.freeCash),
    carryoverY: toY(d.carryover),
    month: d.month,
  }))
)

// Constrói path bezier suave (cardinal spline simplificado)
const smoothPath = (pts, yKey) => {
  if (!pts.length) return ''
  return pts.reduce((acc, p, i) => {
    if (i === 0) return `M ${p.x},${p[yKey]}`
    const prev = pts[i - 1]
    const cx1 = prev.x + stepX.value * 0.4
    const cx2 = p.x   - stepX.value * 0.4
    return `${acc} C ${cx1},${prev[yKey]} ${cx2},${p[yKey]} ${p.x},${p[yKey]}`
  }, '')
}

const freeCashLinePath  = computed(() => smoothPath(points.value, 'freeCashY'))
const carryoverLinePath = computed(() => smoothPath(points.value, 'carryoverY'))

const areaPath = (linePath) => {
  if (!points.value.length) return ''
  const last  = points.value[points.value.length - 1]
  const first = points.value[0]
  return `${linePath} L ${last.x},${H} L ${first.x},${H} Z`
}

const freeCashAreaPath  = computed(() => areaPath(freeCashLinePath.value))
const carryoverAreaPath = computed(() => areaPath(carryoverLinePath.value))

const findClosest = (clientX, rect) => {
  const svgX = ((clientX - rect.left) / rect.width) * W
  let closest = 0
  let minDist = Infinity
  points.value.forEach((p, i) => {
    const d = Math.abs(p.x - svgX)
    if (d < minDist) { minDist = d; closest = i }
  })
  hovered.value = closest
}

const onMove  = (e) => findClosest(e.clientX, e.currentTarget.getBoundingClientRect())
const onTouch = (e) => findClosest(e.touches[0].clientX, e.currentTarget.getBoundingClientRect())

const tooltipStyle = computed(() => {
  if (hovered.value === null) return {}
  const p = points.value[hovered.value]
  const pct = (p.x / W) * 100
  const topPx = Math.min(p.freeCashY, p.carryoverY)
  return {
    bottom: `${H - topPx + 12}px`,
    left: `${pct}%`,
    transform: pct > 60 ? 'translateX(-100%)' : 'translateX(0)',
  }
})

const fmt = (n) => (n ?? 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 100ms ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>

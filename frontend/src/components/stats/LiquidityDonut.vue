<template>
  <div class="font-ss01 flex flex-col items-center gap-4">

    <!-- SVG da rosca -->
    <div class="relative w-full max-w-[200px]">
      <svg :viewBox="`0 0 ${SIZE} ${SIZE}`" class="w-full h-auto">
        <!-- Trilha de fundo -->
        <circle
          :cx="C" :cy="C" :r="R"
          fill="none"
          stroke-width="28"
          class="stroke-brand-hairline-light dark:stroke-brand-hairline-dark"
        />

        <!-- Fatia: Fixas -->
        <circle
          :cx="C" :cy="C" :r="R"
          fill="none"
          stroke-width="28"
          :stroke="COLORS.fixed"
          :stroke-dasharray="`${fixedArc} ${CIRCUMFERENCE}`"
          stroke-dashoffset="0"
          stroke-linecap="round"
          transform="rotate(-90, 100, 100)"
          :opacity="hovered === 'variable' ? 0.3 : 1"
          class="transition-opacity duration-150 cursor-default"
          @mouseenter="hovered = 'fixed'"
          @mouseleave="hovered = null"
          @touchstart.prevent="hovered = hovered === 'fixed' ? null : 'fixed'"
        />

        <!-- Fatia: Variáveis (começa após as fixas) -->
        <circle
          :cx="C" :cy="C" :r="R"
          fill="none"
          stroke-width="28"
          :stroke="COLORS.variable"
          :stroke-dasharray="`${variableArc} ${CIRCUMFERENCE}`"
          :stroke-dashoffset="-fixedArc"
          stroke-linecap="round"
          transform="rotate(-90, 100, 100)"
          :opacity="hovered === 'fixed' ? 0.3 : 1"
          class="transition-opacity duration-150 cursor-default"
          @mouseenter="hovered = 'variable'"
          @mouseleave="hovered = null"
          @touchstart.prevent="hovered = hovered === 'variable' ? null : 'variable'"
        />

        <!-- Texto central: percentual dominante -->
        <text :x="C" :y="C - 8" text-anchor="middle" font-size="28" font-weight="700"
          class="fill-brand-ink-light dark:fill-white tabular-nums"
        >{{ dominantPct }}%</text>
        <text :x="C" :y="C + 14" text-anchor="middle" font-size="10"
          class="fill-brand-ink-mute-light dark:fill-brand-ink-mute-dark"
        >{{ dominantLabel }}</text>
      </svg>
    </div>

    <!-- Legenda -->
    <div class="flex gap-6">
      <div
        v-for="item in legend"
        :key="item.key"
        class="flex items-center gap-2 cursor-default transition-opacity duration-150"
        :class="hovered && hovered !== item.key ? 'opacity-30' : 'opacity-100'"
        @mouseenter="hovered = item.key"
        @mouseleave="hovered = null"
      >
        <span class="w-2.5 h-2.5 rounded-full flex-shrink-0" :style="{ backgroundColor: item.color }" />
        <div>
          <p class="text-xs font-medium text-brand-ink-light dark:text-white leading-tight">{{ item.label }}</p>
          <p class="text-[11px] tabular-nums font-mono text-brand-ink-mute-light dark:text-brand-ink-mute-dark">{{ fmt(item.amount) }}</p>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    required: true,
    // { fixed: number, variable: number }
  },
})

const hovered = ref(null)

const SIZE = 200
const C = SIZE / 2
const R = 72
const CIRCUMFERENCE = 2 * Math.PI * R

const COLORS = {
  fixed:    '#1e293b', // slate-800
  variable: '#cbd5e1', // slate-300
}

const total = computed(() => (props.data.fixed ?? 0) + (props.data.variable ?? 0))

const fixedPct  = computed(() => total.value ? Math.round((props.data.fixed / total.value) * 100) : 0)
const varPct    = computed(() => 100 - fixedPct.value)

const fixedArc    = computed(() => (fixedPct.value / 100) * CIRCUMFERENCE)
const variableArc = computed(() => (varPct.value / 100) * CIRCUMFERENCE)

const dominantPct   = computed(() => fixedPct.value >= varPct.value ? fixedPct.value : varPct.value)
const dominantLabel = computed(() => fixedPct.value >= varPct.value ? 'Fixo' : 'Variável')

const legend = computed(() => [
  { key: 'fixed',    label: 'Fixas + Aluguel',      amount: props.data.fixed,    color: COLORS.fixed },
  { key: 'variable', label: 'Variáveis + Parceladas', amount: props.data.variable, color: COLORS.variable },
])

const fmt = (n) => (n ?? 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
</script>

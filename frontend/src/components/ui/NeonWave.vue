<template>
  <canvas ref="canvasRef" class="block w-full h-full" aria-hidden="true" />
</template>

<script setup>
// Onda neon animada em canvas 2D — núcleo branco + bordas índigo/esmeralda
// (aberração cromática) com brilho aditivo. Sem dependências; respeita reduced-motion.
import { ref, onMounted, onBeforeUnmount } from 'vue'

const canvasRef = ref(null)
let ctx = null
let raf = null
let ro = null
let w = 0, h = 0, dpr = 1
let phase = 0

const INDIGO = '#6366f1'
const EMERALD = '#10b981'

function resize() {
  const c = canvasRef.value
  if (!c || !ctx) return
  dpr = Math.min(window.devicePixelRatio || 1, 2)
  const rect = c.getBoundingClientRect()
  w = rect.width
  h = rect.height
  c.width = Math.max(1, Math.floor(w * dpr))
  c.height = Math.max(1, Math.floor(h * dpr))
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
}

function tracePath(amp, freq, ph, yOffset) {
  ctx.beginPath()
  const mid = h / 2 + yOffset
  for (let x = 0; x <= w; x += 2) {
    const nx = x / w
    const env = Math.sin(nx * Math.PI)          // amplitude vai a zero nas bordas
    const y = mid + Math.sin(nx * freq + ph) * amp * env
    x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
  }
}

function strokeLine(color, width, alpha, blur) {
  ctx.strokeStyle = color
  ctx.lineWidth = width
  ctx.globalAlpha = alpha
  ctx.shadowBlur = blur
  ctx.shadowColor = color
  ctx.lineCap = 'round'
  ctx.stroke()
}

function draw() {
  if (!ctx) return
  ctx.clearRect(0, 0, w, h)
  ctx.globalCompositeOperation = 'lighter'

  const amp = h * 0.18 * (0.85 + 0.15 * Math.sin(phase * 0.6))
  const freq = 6.5

  // Cópias deslocadas (aberração cromática)
  tracePath(amp, freq, phase - 0.18, -2)
  strokeLine(INDIGO, 2, 0.55, 18)

  tracePath(amp, freq, phase + 0.18, 2)
  strokeLine(EMERALD, 2, 0.45, 18)

  // Núcleo branco com fade horizontal nas pontas
  const grad = ctx.createLinearGradient(0, 0, w, 0)
  grad.addColorStop(0,    'rgba(255,255,255,0)')
  grad.addColorStop(0.22, 'rgba(255,255,255,0.9)')
  grad.addColorStop(0.5,  'rgba(255,255,255,1)')
  grad.addColorStop(0.78, 'rgba(255,255,255,0.9)')
  grad.addColorStop(1,    'rgba(255,255,255,0)')
  tracePath(amp, freq, phase, 0)
  ctx.strokeStyle = grad
  ctx.lineWidth = 1.6
  ctx.globalAlpha = 1
  ctx.shadowBlur = 12
  ctx.shadowColor = 'rgba(255,255,255,0.9)'
  ctx.lineCap = 'round'
  ctx.stroke()

  ctx.globalCompositeOperation = 'source-over'
  ctx.globalAlpha = 1
  ctx.shadowBlur = 0
}

function loop() {
  phase += 0.03
  draw()
  raf = requestAnimationFrame(loop)
}

onMounted(() => {
  const c = canvasRef.value
  if (!c) return
  ctx = c.getContext('2d')
  resize()

  const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  if (reduce) {
    draw() // quadro estático
  } else {
    loop()
  }

  ro = new ResizeObserver(() => { resize(); if (reduce) draw() })
  ro.observe(c)
})

onBeforeUnmount(() => {
  if (raf) cancelAnimationFrame(raf)
  ro?.disconnect()
})
</script>

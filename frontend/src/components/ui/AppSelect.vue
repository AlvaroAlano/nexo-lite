<template>
  <div class="relative" ref="rootRef">
    <button
      ref="triggerRef"
      type="button"
      @click="toggle"
      class="w-full flex items-center justify-between gap-2 px-4 py-2.5 md:py-2 border border-brand-hairline-light dark:border-brand-hairline-dark rounded-stripe-input text-sm text-left bg-white dark:bg-brand-canvas-soft-dark text-brand-ink-light dark:text-white hover:border-slate-300 dark:hover:border-brand-hairline-dark/50 focus:outline-none focus:ring-2 focus:ring-brand-primary/20 dark:focus:ring-brand-primary/40 transition-colors"
    >
      <span class="truncate">{{ selectedLabel }}</span>
      <svg
        class="w-3.5 h-3.5 text-brand-ink-mute-light dark:text-brand-ink-mute-dark flex-shrink-0 transition-transform duration-150"
        :class="open ? 'rotate-180' : ''"
        viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
      >
        <polyline points="6 9 12 15 18 9"/>
      </svg>
    </button>

    <Teleport to="body">
      <div
        v-if="open"
        ref="dropdownRef"
        class="fixed z-[300] bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-stripe-input shadow-stripe-2 overflow-hidden"
        :style="dropdownStyle"
      >
        <div class="py-1">
          <button
            v-for="opt in options"
            :key="opt.value"
            type="button"
            @click="select(opt.value)"
            class="w-full px-4 py-2 text-left text-sm text-brand-ink-light dark:text-white hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark/50 flex items-center justify-between gap-2 transition-colors"
          >
            <span>{{ opt.label }}</span>
            <svg
              v-if="modelValue === opt.value"
              class="w-3.5 h-3.5 text-emerald-500 flex-shrink-0"
              viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
            >
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

defineOptions({ inheritAttrs: false })
const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  options: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const rootRef = ref(null)
const triggerRef = ref(null)
const dropdownRef = ref(null)
const dropdownStyle = ref({})

const selectedLabel = computed(() =>
  props.options.find(o => o.value === props.modelValue)?.label ?? ''
)

function toggle() {
  if (!open.value) {
    const rect = triggerRef.value.getBoundingClientRect()
    dropdownStyle.value = {
      top:   `${rect.bottom + 4}px`,
      left:  `${rect.left}px`,
      width: `${rect.width}px`,
    }
  }
  open.value = !open.value
}

function select(value) {
  emit('update:modelValue', value)
  open.value = false
}

function handleOutside(e) {
  const inRoot     = rootRef.value?.contains(e.target)
  const inDropdown = dropdownRef.value?.contains(e.target)
  if (!inRoot && !inDropdown) open.value = false
}
onMounted(() => document.addEventListener('click', handleOutside))
onUnmounted(() => document.removeEventListener('click', handleOutside))
</script>

<!-- Dropdown to pick a category, shows icon + colored name -->
<template>
  <div class="relative" ref="rootRef">
    <button
      ref="triggerRef"
      type="button"
      @click="toggle"
      class="w-full flex items-center gap-2 px-3 py-2.5 md:py-2 border border-brand-hairline-light dark:border-brand-hairline-dark rounded-stripe-input text-sm text-left hover:border-slate-300 dark:hover:border-brand-hairline-dark/50 focus:outline-none focus:ring-2 focus:ring-brand-primary/20 dark:focus:ring-brand-primary/40 transition-colors bg-white dark:bg-brand-canvas-soft-dark"
    >
      <template v-if="selected">
        <span
          class="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0"
          :style="{ backgroundColor: colorByKey(selected.color).light, color: colorByKey(selected.color).text }"
        >
          <component :is="getIconComponent(selected.icon)" :size="11" :stroke-width="2" />
        </span>
        <span class="flex-1 truncate text-brand-ink-light dark:text-white">{{ selected.name }}</span>
      </template>
      <span v-else class="text-brand-ink-mute-light dark:text-brand-ink-mute-dark flex-1">Categoria (opcional)</span>
      <svg class="w-3.5 h-3.5 text-brand-ink-mute-light dark:text-brand-ink-mute-dark flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
        <div class="max-h-52 overflow-y-auto py-1">
          <button
            v-if="modelValue"
            type="button"
            @click="select(null)"
            class="w-full px-3 py-2 text-left text-sm text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark/50 flex items-center gap-2"
          >
            <span class="w-5 h-5" />
            <span>Sem categoria</span>
          </button>
          <button
            v-for="cat in store.categories"
            :key="cat.id"
            type="button"
            @click="select(cat)"
            class="w-full px-3 py-2 text-left text-sm hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark/50 flex items-center gap-2 transition-colors"
            :class="modelValue === cat.id ? 'bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark/50' : ''"
          >
            <span
              class="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0"
              :style="{ backgroundColor: colorByKey(cat.color).light, color: colorByKey(cat.color).text }"
            >
              <component :is="getIconComponent(cat.icon)" :size="11" :stroke-width="2" />
            </span>
            <span class="text-brand-ink-light dark:text-white truncate">{{ cat.name }}</span>
            <svg v-if="modelValue === cat.id" class="w-3.5 h-3.5 text-emerald-500 ml-auto flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
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
import { useCategoriesStore } from '../../stores/categories.js'
import { colorByKey, getIconComponent } from '../../utils/categories.js'

const props = defineProps({ modelValue: { type: String, default: null } })
const emit = defineEmits(['update:modelValue'])

const store = useCategoriesStore()
const open = ref(false)
const rootRef = ref(null)
const triggerRef = ref(null)
const dropdownRef = ref(null)
const dropdownStyle = ref({})

const selected = computed(() => props.modelValue ? store.byId[props.modelValue] : null)

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

function select(cat) {
  emit('update:modelValue', cat?.id || null)
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

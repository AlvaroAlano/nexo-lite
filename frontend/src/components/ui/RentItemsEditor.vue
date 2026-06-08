<template>
  <div class="space-y-1 font-ss01">

    <!-- Items list -->
    <div v-if="modelValue.length" class="space-y-1 mb-2">
      <div
        v-for="(item, idx) in modelValue"
        :key="item.id"
        class="flex items-center gap-2 px-3 py-2 border border-brand-hairline-light dark:border-brand-hairline-dark/40 rounded-stripe-card bg-brand-canvas-soft-light/50 dark:bg-brand-canvas-soft-dark group"
      >
        <span class="text-[10px] font-semibold px-1.5 py-0.5 rounded-full flex-shrink-0" :class="typeBadge(item.type)">
          {{ typeLabel(item.type) }}
        </span>
        <span class="flex-1 text-sm text-brand-ink-light dark:text-white min-w-0 truncate">
          {{ item.name }}
          <span v-if="item.type === 'installment' && item.installment_current" class="text-brand-ink-mute-light dark:text-brand-ink-mute-dark ml-1 font-tabular text-[11px]">
            {{ item.installment_current }}/{{ item.installment_total }}
          </span>
        </span>
        <CurrencyInput
          :model-value="item.amount"
          @update:model-value="updateAmount(idx, $event)"
          hide-prefix
          input-class="w-24 text-right font-tabular font-medium text-sm text-brand-ink-light dark:text-white bg-transparent border-b border-transparent focus:border-brand-primary outline-none"
        />
        <button
          @click="remove(idx)"
          class="w-6 h-6 flex items-center justify-center rounded text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:text-red-500 hover:bg-red-500/10 transition-colors opacity-0 group-hover:opacity-100"
        >
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
    </div>

    <p v-else class="text-center text-brand-ink-mute-light dark:text-brand-ink-mute-dark text-sm py-3">
      Nenhum item. Adicione abaixo.
    </p>

    <!-- Add form -->
    <div v-if="!showAdd" class="pt-1">
      <button
        @click="showAdd = true"
        class="w-full py-2.5 rounded-stripe-input border border-dashed border-brand-hairline-light dark:border-brand-hairline-dark text-brand-ink-mute-light dark:text-brand-ink-mute-dark text-sm hover:border-brand-primary hover:text-brand-primary dark:hover:text-white transition-colors"
      >
        + Adicionar item
      </button>
    </div>

    <div v-else class="border border-brand-hairline-light dark:border-brand-hairline-dark rounded-stripe-input p-3 space-y-2.5 bg-white dark:bg-brand-canvas-soft-dark/50">
      <input
        ref="draftNameRef"
        v-model="draft.name"
        placeholder="Nome (ex: IPTU)"
        class="w-full px-3 py-2 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
      />
      <div class="grid grid-cols-2 gap-2">
        <AppSelect v-model="draft.type" :options="typeOpts" />
        <CurrencyInput
          v-model="draft.amount"
          input-class="w-full pr-3 py-2 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
        />
      </div>
      <div v-if="draft.type === 'installment'" class="grid grid-cols-2 gap-2">
        <input
          v-model.number="draft.installment_current"
          type="number" min="1"
          placeholder="Parcela atual (ex: 1)"
          class="px-3 py-2 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
        />
        <input
          v-model.number="draft.installment_total"
          type="number" min="1"
          placeholder="Total (ex: 8)"
          class="px-3 py-2 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
        />
      </div>
      <div class="flex gap-2">
        <button
          @click="addItem"
          :disabled="!draft.name.trim()"
          class="flex-1 py-2 rounded-full bg-brand-primary hover:bg-brand-primary-hover text-white text-sm font-medium disabled:opacity-40 active:scale-95 transition-all"
        >Adicionar</button>
        <button
          @click="cancelAdd"
          class="px-4 py-2 rounded-full border border-brand-hairline-light dark:border-brand-hairline-dark text-sm text-brand-ink-light dark:text-white hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark/30 transition-colors"
        >Cancelar</button>
      </div>
    </div>

    <!-- Total -->
    <div class="flex items-center justify-between bg-brand-canvas-soft-light/50 dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark/40 rounded-xl px-4 py-3 mt-2">
      <span class="text-sm font-semibold text-brand-ink-light dark:text-white">Total do boleto</span>
      <span class="font-tabular font-medium text-lg text-brand-ink-light dark:text-white">{{ fmt(total) }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import CurrencyInput from './CurrencyInput.vue'
import AppSelect from './AppSelect.vue'
import { usePrivacyMode } from '../../composables/usePrivacyMode.js'
const { maskCurrency: fmt } = usePrivacyMode()

const props = defineProps({ modelValue: { type: Array, default: () => [] } })
const emit  = defineEmits(['update:modelValue'])

const showAdd    = ref(false)
const draftNameRef = ref(null)

const emptyDraft = () => ({ name: '', amount: 0, type: 'fixed', installment_current: null, installment_total: null })
const draft = ref(emptyDraft())

const typeOpts = [
  { value: 'fixed',       label: 'Fixo' },
  { value: 'variable',    label: 'Variável' },
  { value: 'installment', label: 'Parcela' },
]

watch(showAdd, (v) => { if (v) nextTick(() => draftNameRef.value?.focus()) })

const total = computed(() => props.modelValue.reduce((s, i) => s + (parseFloat(i.amount) || 0), 0))

function addItem() {
  if (!draft.value.name.trim()) return
  emit('update:modelValue', [
    ...props.modelValue,
    {
      id: crypto.randomUUID(),
      name: draft.value.name.trim(),
      amount: parseFloat(draft.value.amount) || 0,
      type: draft.value.type,
      installment_current: draft.value.type === 'installment' ? (draft.value.installment_current || 1) : null,
      installment_total:   draft.value.type === 'installment' ? (draft.value.installment_total   || null) : null,
    },
  ])
  draft.value = emptyDraft()
  showAdd.value = false
}

function cancelAdd() {
  draft.value = emptyDraft()
  showAdd.value = false
}

function remove(idx) {
  const updated = [...props.modelValue]
  updated.splice(idx, 1)
  emit('update:modelValue', updated)
}

function updateAmount(idx, val) {
  const updated = props.modelValue.map((item, i) => i === idx ? { ...item, amount: val } : item)
  emit('update:modelValue', updated)
}

const TYPE_LABELS = { fixed: 'Fixo', variable: 'Variável', installment: 'Parcela' }
const TYPE_BADGES = {
  fixed:       'bg-brand-canvas-soft-light text-brand-ink-mute-light dark:bg-brand-canvas-dark dark:text-brand-ink-mute-dark',
  variable:    'bg-amber-50 text-amber-600 dark:bg-amber-950/40 dark:text-amber-300',
  installment: 'bg-blue-50 text-blue-600 dark:bg-blue-950/40 dark:text-blue-300',
}
const typeLabel = (t) => TYPE_LABELS[t] || t
const typeBadge = (t) => TYPE_BADGES[t] || TYPE_BADGES.fixed
</script>

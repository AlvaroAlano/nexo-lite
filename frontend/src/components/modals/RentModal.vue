<template>
  <BaseModal v-model="open" title="Composição do Boleto" full-screen-on-mobile>
    <div v-if="expense" class="space-y-1 font-ss01">

      <!-- Items list -->
      <div v-if="items.length" class="space-y-1 mb-3">
        <div
          v-for="(item, idx) in items"
          :key="item.id"
          class="flex items-center gap-2 px-3 py-2 border border-brand-hairline-light dark:border-brand-hairline-dark/40 rounded-stripe-card bg-brand-canvas-soft-light/50 dark:bg-brand-canvas-soft-dark group"
        >
          <!-- Type badge -->
          <span class="text-[10px] font-semibold px-1.5 py-0.5 rounded-full flex-shrink-0" :class="typeBadge(item.type)">
            {{ typeLabel(item.type) }}
          </span>

          <!-- Name -->
          <span class="flex-1 text-sm text-brand-ink-light dark:text-white min-w-0 truncate">
            {{ item.name }}
            <span v-if="item.type === 'installment' && item.installment_current" class="text-brand-ink-mute-light dark:text-brand-ink-mute-dark ml-1 font-tabular text-[11px]">
              {{ item.installment_current }}/{{ item.installment_total }}
            </span>
          </span>

          <!-- Amount (inline edit) -->
          <CurrencyInput
            :model-value="item.amount"
            @update:model-value="item.amount = $event"
            hide-prefix
            input-class="w-24 text-right font-tabular font-medium text-sm text-brand-ink-light dark:text-white bg-transparent border-b border-transparent focus:border-brand-primary outline-none"
          />

          <!-- Remove -->
          <button
            @click="removeItem(idx)"
            class="w-6 h-6 flex items-center justify-center rounded text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:text-red-500 hover:bg-red-500/10 transition-colors opacity-0 group-hover:opacity-100"
          >
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      </div>

      <p v-else class="text-center text-brand-ink-mute-light dark:text-brand-ink-mute-dark text-sm py-4">
        Nenhum item ainda. Adicione abaixo.
      </p>

      <!-- Add item form -->
      <div v-if="!showAddForm" class="pt-1">
        <button
          @click="showAddForm = true"
          class="w-full py-2.5 rounded-stripe-input border border-dashed border-brand-hairline-light dark:border-brand-hairline-dark text-brand-ink-mute-light dark:text-brand-ink-mute-dark text-sm hover:border-brand-primary hover:text-brand-primary dark:hover:text-white transition-colors"
        >
          + Adicionar item
        </button>
      </div>

      <div v-else class="border border-brand-hairline-light dark:border-brand-hairline-dark rounded-stripe-input p-3 space-y-2.5 bg-white dark:bg-brand-canvas-soft-dark/50 mt-1">
        <input
          v-model="newItem.name"
          placeholder="Nome (ex: Condomínio)"
          class="w-full px-3 py-2.5 md:py-2 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
          ref="nameInputRef"
        />
        <div class="grid grid-cols-2 gap-2">
          <AppSelect v-model="newItem.type" :options="itemTypeOpts" />
          <CurrencyInput
            v-model="newItem.amount"
            input-class="w-full pr-3 py-2.5 md:py-2 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
          />
        </div>
        <div v-if="newItem.type === 'installment'" class="grid grid-cols-2 gap-2">
          <input
            v-model.number="newItem.installment_current"
            type="number"
            min="1"
            placeholder="Parcela atual (ex: 9)"
            class="px-3 py-2.5 md:py-2 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
          />
          <input
            v-model.number="newItem.installment_total"
            type="number"
            min="1"
            placeholder="Total (ex: 12)"
            class="px-3 py-2.5 md:py-2 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
          />
        </div>
        <div class="flex gap-2">
          <button
            @click="addItem"
            :disabled="!newItem.name.trim()"
            class="flex-1 py-2 rounded-full bg-brand-primary hover:bg-brand-primary-hover text-white text-sm font-medium disabled:opacity-40 active:scale-95 transition-all"
          >
            Adicionar
          </button>
          <button
            @click="cancelAdd"
            class="px-4 py-2 rounded-full border border-brand-hairline-light dark:border-brand-hairline-dark text-sm text-brand-ink-light dark:text-white hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark/30 transition-colors"
          >
            Cancelar
          </button>
        </div>
      </div>

      <!-- Total -->
      <div class="flex items-center justify-between bg-brand-canvas-soft-light/50 dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark/40 rounded-xl px-4 py-3 mt-3">
        <span class="text-sm font-semibold text-brand-ink-light dark:text-white">Total do boleto</span>
        <span class="font-tabular font-medium text-lg text-brand-ink-light dark:text-white">{{ formatCurrency(liveTotal) }}</span>
      </div>
    </div>

    <template #footer>
      <button
        @click="save"
        :disabled="store.saving || !items.length"
        class="w-full py-2.5 md:py-2 px-4 rounded-full bg-brand-primary hover:bg-brand-primary-hover text-white font-medium text-sm active:scale-[.98] transition-all disabled:opacity-50"
      >
        {{ store.saving ? 'Salvando…' : 'Confirmar Boleto' }}
      </button>
    </template>
  </BaseModal>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import BaseModal from '../ui/BaseModal.vue'
import CurrencyInput from '../ui/CurrencyInput.vue'
import AppSelect from '../ui/AppSelect.vue'
import { useDashboardStore } from '../../stores/dashboard.js'
import { formatCurrency } from '../../utils/currency.js'

const props = defineProps({ modelValue: Boolean, expense: { type: Object, default: null } })
const emit = defineEmits(['update:modelValue'])

const store = useDashboardStore()
const open = computed({ get: () => props.modelValue, set: (v) => emit('update:modelValue', v) })

const items = ref([])
const showAddForm = ref(false)
const nameInputRef = ref(null)

const emptyItem = () => ({
  id: crypto.randomUUID(),
  name: '',
  amount: 0,
  type: 'fixed',
  installment_current: null,
  installment_total: null,
})
const newItem = ref(emptyItem())

const itemTypeOpts = [
  { value: 'fixed',       label: 'Fixo' },
  { value: 'variable',    label: 'Variável' },
  { value: 'installment', label: 'Parcela' },
]

watch(() => props.expense, (e) => {
  if (e) {
    items.value = (e.rent_items || []).map(i => ({ ...i, amount: parseFloat(i.amount) || 0 }))
  }
}, { immediate: true })

const liveTotal = computed(() =>
  items.value.reduce((sum, i) => sum + (parseFloat(i.amount) || 0), 0)
)

function addItem() {
  if (!newItem.value.name.trim()) return
  items.value.push({
    id: crypto.randomUUID(),
    name: newItem.value.name.trim(),
    amount: parseFloat(newItem.value.amount) || 0,
    type: newItem.value.type,
    installment_current: newItem.value.type === 'installment' ? newItem.value.installment_current : null,
    installment_total: newItem.value.type === 'installment' ? newItem.value.installment_total : null,
  })
  newItem.value = emptyItem()
  showAddForm.value = false
}

function cancelAdd() {
  newItem.value = emptyItem()
  showAddForm.value = false
}

function removeItem(idx) {
  items.value.splice(idx, 1)
}

async function save() {
  if (!props.expense) return
  await store.updateRent(props.expense.id, {
    rent_items: items.value.map(i => ({
      ...i,
      amount: parseFloat(i.amount) || 0,
    })),
  })
  open.value = false
}

watch(showAddForm, (v) => {
  if (v) nextTick(() => nameInputRef.value?.focus())
})

const TYPE_LABELS = { fixed: 'Fixo', variable: 'Variável', installment: 'Parcela' }
const TYPE_BADGES = {
  fixed:       'bg-brand-canvas-soft-light text-brand-ink-mute-light dark:bg-brand-canvas-dark dark:text-brand-ink-mute-dark',
  variable:    'bg-amber-50 text-amber-600 dark:bg-amber-950/40 dark:text-amber-300',
  installment: 'bg-blue-50 text-blue-600 dark:bg-blue-950/40 dark:text-blue-300',
}
const typeLabel = (t) => TYPE_LABELS[t] || t
const typeBadge = (t) => TYPE_BADGES[t] || TYPE_BADGES.fixed
</script>

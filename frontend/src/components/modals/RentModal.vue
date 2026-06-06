<template>
  <BaseModal v-model="open" title="Composição do Boleto" full-screen-on-mobile>
    <div v-if="expense" class="space-y-3 font-ss01">

      <!-- Lista de itens -->
      <div v-if="items.length" class="rounded-xl overflow-hidden border border-brand-hairline-light dark:border-brand-hairline-dark/50">
        <div v-for="(item, idx) in items" :key="item.id" class="group">
          <div class="flex items-center pl-4 pr-2 py-3 bg-white dark:bg-brand-canvas-soft-dark/60 hover:bg-brand-canvas-soft-light/60 dark:hover:bg-brand-canvas-soft-dark transition-colors">
            <!-- Info -->
            <div class="flex-1 min-w-0 pr-2">
              <p class="text-sm font-medium text-brand-ink-light dark:text-white leading-tight">{{ item.name }}</p>
              <div class="flex items-center gap-1.5 mt-1">
                <span class="text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-full flex-shrink-0" :class="typeBadge(item.type)">
                  {{ typeLabel(item.type) }}
                </span>
                <span v-if="item.type === 'installment' && item.installment_current" class="text-[11px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark font-tabular">
                  {{ item.installment_current }}/{{ item.installment_total }}
                </span>
              </div>
            </div>

            <!-- Valor (edição inline) -->
            <CurrencyInput
              :model-value="item.amount"
              @update:model-value="item.amount = $event"
              hide-prefix
              input-class="w-20 text-right font-tabular font-semibold text-sm text-brand-ink-light dark:text-white bg-transparent border-b border-transparent focus:border-brand-primary/60 outline-none"
            />

            <!-- Remover -->
            <button
              @click="removeItem(idx)"
              class="ml-1 w-8 h-8 flex items-center justify-center rounded-lg text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:text-red-500 hover:bg-red-500/10 active:scale-90 transition-all md:opacity-0 md:group-hover:opacity-100 flex-shrink-0"
              aria-label="Remover item"
            >
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <!-- Divisor entre itens -->
          <div v-if="idx < items.length - 1" class="h-px bg-brand-hairline-light dark:bg-brand-hairline-dark/40 mx-4" />
        </div>
      </div>

      <!-- Empty state -->
      <p v-else class="text-center text-brand-ink-mute-light dark:text-brand-ink-mute-dark text-sm py-6">
        Nenhum item ainda.
      </p>

      <!-- Adicionar item -->
      <div v-if="!showAddForm">
        <button
          @click="showAddForm = true"
          class="w-full py-3 rounded-xl border border-dashed border-brand-hairline-light dark:border-brand-hairline-dark text-brand-ink-mute-light dark:text-brand-ink-mute-dark text-sm hover:border-brand-primary/50 hover:text-brand-primary dark:hover:text-brand-primary-soft active:scale-[.98] transition-all"
        >
          + Adicionar item
        </button>
      </div>

      <div v-else class="rounded-xl border border-brand-hairline-light dark:border-brand-hairline-dark bg-brand-canvas-soft-light/40 dark:bg-brand-canvas-soft-dark/50 p-4 space-y-3">
        <input
          v-model="newItem.name"
          placeholder="Nome (ex: Condomínio)"
          class="w-full px-3 py-2.5 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20 transition-colors"
          ref="nameInputRef"
        />
        <div class="grid grid-cols-2 gap-2">
          <AppSelect v-model="newItem.type" :options="itemTypeOpts" />
          <CurrencyInput
            v-model="newItem.amount"
            input-class="w-full pr-3 py-2.5 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
          />
        </div>
        <div v-if="newItem.type === 'installment'" class="grid grid-cols-2 gap-2">
          <input
            v-model.number="newItem.installment_current"
            type="number"
            min="1"
            placeholder="Parcela atual"
            class="px-3 py-2.5 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
          />
          <input
            v-model.number="newItem.installment_total"
            type="number"
            min="1"
            placeholder="Total de parcelas"
            class="px-3 py-2.5 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
          />
        </div>
        <div class="flex gap-2 pt-0.5">
          <button
            @click="addItem"
            :disabled="!newItem.name.trim()"
            class="flex-1 py-2.5 rounded-full bg-brand-primary hover:bg-brand-primary-hover text-white text-sm font-medium disabled:opacity-40 active:scale-[.98] transition-all"
          >
            Adicionar
          </button>
          <button
            @click="cancelAdd"
            class="px-4 py-2.5 rounded-full border border-brand-hairline-light dark:border-brand-hairline-dark text-sm text-brand-ink-light dark:text-white hover:bg-white dark:hover:bg-brand-canvas-soft-dark/30 transition-colors"
          >
            Cancelar
          </button>
        </div>
      </div>

      <!-- Total -->
      <div class="flex items-center justify-between pt-1">
        <span class="text-sm text-brand-ink-mute-light dark:text-brand-ink-mute-dark">Total do boleto</span>
        <span class="font-tabular font-bold text-xl text-brand-ink-light dark:text-white">{{ formatCurrency(liveTotal) }}</span>
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

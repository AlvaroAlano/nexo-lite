<template>
  <div class="flex items-center gap-3 py-3.5">
    <!-- Category icon -->
    <div
      class="w-9 h-9 rounded-full flex-shrink-0 flex items-center justify-center"
      :style="{ backgroundColor: catColor.light }"
    >
      <component
        v-if="category"
        :is="getIconComponent(category.icon)"
        :size="16"
        :stroke-width="2"
        :style="{ color: catColor.text }"
      />
      <div v-else class="w-2 h-2 rounded-full bg-slate-300 dark:bg-slate-600" />
    </div>

    <!-- Name + secondary info -->
    <div class="flex-1 min-w-0">
      <div class="flex items-center gap-1.5 min-w-0">
        <span
          class="text-sm font-medium truncate"
          :class="expense.is_paid
            ? 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark line-through'
            : 'text-brand-ink-light dark:text-white'"
        >
          {{ expense.name }}
        </span>
        <span
          v-if="isInstallment"
          class="text-[10px] font-tabular text-brand-ink-mute-light dark:text-brand-ink-mute-dark flex-shrink-0"
        >
          {{ expense.installment_current }}/{{ expense.installment_total }}
        </span>
      </div>
      <div class="flex items-center gap-1 mt-0.5">
        <span v-if="category" class="text-[11px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark">{{ category.name }}</span>
        <span v-if="category" class="text-[11px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark">·</span>
        <span class="text-[11px]" :class="responsavelColor">{{ responsavelLabel }}</span>
      </div>
    </div>

    <!-- Amount + actions -->
    <div class="flex-shrink-0 flex flex-col items-end gap-2">
      <!-- Amount (tap to edit, except rent) -->
      <span
        v-if="!editing"
        @click="!isRent && startEdit()"
        class="text-sm font-tabular font-medium transition-colors"
        :class="[
          expense.is_paid
            ? 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark line-through'
            : 'text-brand-ink-light dark:text-white',
          !isRent ? 'cursor-pointer hover:text-brand-primary dark:hover:text-brand-primary-soft' : '',
        ]"
      >
        {{ formatCurrency(expense.amount) }}
      </span>
      <CurrencyInput
        v-else
        v-model="editValue"
        @confirm="saveEdit"
        @cancel="cancelEdit"
        @blur="saveEdit"
        hide-prefix
        input-class="font-tabular font-medium text-sm text-right text-brand-ink-light dark:text-white bg-transparent border-b border-brand-primary outline-none w-24"
      />

      <!-- Secondary actions -->
      <div class="flex items-center gap-2.5">
        <button
          v-if="isRent"
          @click="$emit('open-rent', expense)"
          class="text-[11px] font-medium text-brand-primary dark:text-brand-primary-soft active:opacity-60 transition-opacity"
        >
          Detalhar
        </button>

        <button
          v-if="!store.isReadOnly && expense.category !== 'Caixinha'"
          @click="$emit('edit', expense)"
          class="w-5 h-5 flex items-center justify-center rounded-md text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark/30 hover:text-brand-primary active:opacity-60 transition-all flex-shrink-0"
          title="Editar despesa"
        >
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
        </button>
        <button
          v-if="!store.isReadOnly && expense.category !== 'Caixinha'"
          @click="$emit('delete', expense)"
          class="w-5 h-5 flex items-center justify-center rounded-md text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:bg-red-500/10 hover:text-red-500 active:bg-red-500/20 transition-all flex-shrink-0"
          title="Excluir despesa"
        >
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
            <path d="M10 11v6"/>
            <path d="M14 11v6"/>
            <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
          </svg>
        </button>

        <button
          @click="store.togglePaid(expense.id)"
          class="w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all duration-200 active:scale-90 flex-shrink-0"
          :class="expense.is_paid
            ? 'bg-emerald-500 border-emerald-500'
            : 'border-brand-hairline-light dark:border-brand-hairline-dark hover:border-emerald-400 dark:hover:border-emerald-500'"
        >
          <svg v-if="expense.is_paid" class="w-2.5 h-2.5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDashboardStore } from '../../stores/dashboard.js'
import { useCategoriesStore } from '../../stores/categories.js'
import { formatCurrency } from '../../utils/currency.js'
import { colorByKey, getIconComponent } from '../../utils/categories.js'
import CurrencyInput from '../ui/CurrencyInput.vue'

const props = defineProps({
  expense: { type: Object, required: true },
})
defineEmits(['open-rent', 'delete', 'edit'])

const store = useDashboardStore()
const catStore = useCategoriesStore()

const isInstallment = computed(() => props.expense.expense_type === 'installment')
const isRent = computed(() => props.expense.expense_type === 'rent')
const category = computed(() => props.expense.category_id ? catStore.getCategory(props.expense.category_id) : null)
const catColor = computed(() => category.value ? colorByKey(category.value.color) : colorByKey('slate'))

const RESP_COLORS = {
  alvaro:    'text-blue-500 dark:text-blue-400',
  alexandra: 'text-pink-500 dark:text-pink-400',
  conjunto:  'text-brand-ink-mute-light dark:text-brand-ink-mute-dark',
}
const responsavelLabel = computed(() => {
  if (props.expense.responsavel === 'alvaro') return store.nameAlvaro
  if (props.expense.responsavel === 'alexandra') return store.nameAlexandra
  return 'Casal'
})
const responsavelColor = computed(() => RESP_COLORS[props.expense.responsavel] || RESP_COLORS.conjunto)

const editing = ref(false)
const editValue = ref(0)

function startEdit() {
  editValue.value = parseFloat(props.expense.amount) || 0
  editing.value = true
}

async function saveEdit() {
  editing.value = false
  if (editValue.value !== (parseFloat(props.expense.amount) || 0)) {
    await store.updateExpenseAmount(props.expense.id, editValue.value)
  }
}

function cancelEdit() {
  editing.value = false
}
</script>

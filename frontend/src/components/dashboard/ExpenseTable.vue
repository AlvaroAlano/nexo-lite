<template>
  <div class="bg-white dark:bg-brand-canvas-soft-dark rounded-stripe-card border border-brand-hairline-light dark:border-brand-hairline-dark overflow-hidden shadow-stripe-1 font-ss01 transition-colors duration-150">
    <table class="w-full text-sm">
      <thead>
        <tr class="border-b border-brand-hairline-light dark:border-brand-hairline-dark bg-brand-canvas-soft-light/30 dark:bg-brand-canvas-dark/25">
          <th class="text-left px-4 py-3 text-xs font-semibold text-brand-ink-mute-light dark:text-brand-ink-mute-dark uppercase tracking-wide w-[140px]">
            Categoria
          </th>
          <th class="text-left px-4 py-3 text-xs font-semibold text-brand-ink-mute-light dark:text-brand-ink-mute-dark uppercase tracking-wide">
            Despesa
          </th>
          <th class="text-right px-4 py-3 text-xs font-semibold text-brand-ink-mute-light dark:text-brand-ink-mute-dark uppercase tracking-wide w-[120px]">
            Valor
          </th>
          <th class="text-center px-3 py-3 text-xs font-semibold text-brand-ink-mute-light dark:text-brand-ink-mute-dark uppercase tracking-wide w-[90px]">
            Status
          </th>
          <th v-if="!store.isReadOnly" class="w-[50px]"></th>
        </tr>
      </thead>
      <tbody class="divide-y divide-brand-hairline-light dark:divide-brand-hairline-dark/30">
        <tr
          v-for="expense in expenses"
          :key="expense.id"
          class="group hover:bg-brand-canvas-soft-light/40 dark:hover:bg-brand-canvas-soft-dark/30 transition-colors"
          :class="expense.is_paid ? 'opacity-60' : ''"
        >
          <!-- Category -->
          <td class="px-4 py-3.5 w-[140px]">
            <div v-if="getCategory(expense.category_id)" class="flex items-center gap-2">
              <div
                class="w-6 h-6 rounded-full flex-shrink-0 flex items-center justify-center"
                :style="{ backgroundColor: catColor(expense.category_id).light }"
              >
                <component
                  :is="getIconComponent(getCategory(expense.category_id).icon)"
                  :size="12"
                  :stroke-width="2"
                  :style="{ color: catColor(expense.category_id).text }"
                />
              </div>
              <span class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark truncate max-w-[80px]">
                {{ getCategory(expense.category_id).name }}
              </span>
            </div>
            <span v-else class="text-xs text-brand-ink-mute-light/30 dark:text-brand-ink-mute-dark/30">—</span>
          </td>

          <!-- Name + badges -->
          <td class="px-4 py-3.5">
            <div class="flex items-center gap-2 flex-wrap">
              <span
                class="font-medium text-brand-ink-light dark:text-white"
                :class="expense.is_paid ? 'line-through text-brand-ink-mute-light dark:text-brand-ink-mute-dark' : ''"
              >
                {{ expense.name }}
              </span>
              <span
                v-if="expense.expense_type === 'installment'"
                class="text-[10px] font-tabular bg-brand-canvas-soft-light dark:bg-brand-canvas-dark text-brand-ink-mute-light dark:text-brand-ink-mute-dark px-1.5 py-0.5 rounded"
              >
                {{ expense.installment_current }}/{{ expense.installment_total }}
              </span>
              <span
                class="text-[10px] font-semibold px-1.5 py-0.5 rounded-full"
                :class="RESP_BADGES[expense.responsavel] || 'bg-brand-canvas-soft-light text-brand-ink-mute-light dark:bg-brand-canvas-dark dark:text-brand-ink-mute-dark'"
              >
                {{ respLabels[expense.responsavel] || 'Casal' }}
              </span>
            </div>
          </td>

          <!-- Amount -->
          <td class="px-4 py-3.5 text-right w-[120px]">
            <template v-if="expense.expense_type === 'rent'">
              <button
                @click="$emit('open-rent', expense)"
                class="font-tabular font-medium text-brand-ink-light dark:text-white hover:text-brand-primary transition-colors inline-flex items-center gap-1"
              >
                {{ formatCurrency(expense.amount) }}
                <span class="text-[10px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark">↗</span>
              </button>
            </template>
            <template v-else>
              <span
                v-if="editingId !== expense.id"
                @click="startEdit(expense)"
                class="font-tabular font-medium text-brand-ink-light dark:text-white cursor-pointer hover:text-brand-primary transition-colors"
              >
                {{ formatCurrency(expense.amount) }}
              </span>
              <CurrencyInput
                v-else
                ref="editInputRef"
                v-model="editValue"
                @confirm="saveEdit"
                @cancel="cancelEdit"
                @blur="saveEdit"
                hide-prefix
                input-class="font-tabular font-medium text-brand-ink-light dark:text-white text-right bg-white dark:bg-brand-canvas-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-stripe-input px-2 py-0.5 outline-none w-28 focus:ring-2 focus:ring-brand-primary/20"
              />
            </template>
          </td>

          <!-- Paid toggle -->
          <td class="px-3 py-3.5 text-center w-[90px]">
            <button
              @click="store.togglePaid(expense.id)"
              class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border transition-all active:scale-95"
              :class="expense.is_paid
                ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20'
                : 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark border-brand-hairline-light dark:border-brand-hairline-dark hover:border-emerald-300 hover:text-emerald-500'"
            >
              <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              {{ expense.is_paid ? 'Pago' : 'Pagar' }}
            </button>
          </td>

          <!-- Delete action -->
          <td v-if="!store.isReadOnly" class="px-2 py-3.5 text-center w-[50px]">
            <button
              @click="$emit('delete', expense)"
              class="opacity-0 group-hover:opacity-100 focus:opacity-100 w-7 h-7 flex items-center justify-center rounded-lg text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:bg-red-500/10 hover:text-red-500 active:bg-red-500/20 transition-all mx-auto"
              title="Excluir despesa"
            >
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
                <path d="M10 11v6"/>
                <path d="M14 11v6"/>
                <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
              </svg>
            </button>
          </td>
        </tr>

        <!-- Empty state row -->
        <tr v-if="!expenses.length">
          <td :colspan="store.isReadOnly ? 4 : 5" class="px-5 py-10 text-center text-brand-ink-mute-light dark:text-brand-ink-mute-dark text-sm">
            Nenhuma despesa neste mês ainda.
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, nextTick, computed } from 'vue'
import { useDashboardStore } from '../../stores/dashboard.js'
import { useCategoriesStore } from '../../stores/categories.js'
import { formatCurrency } from '../../utils/currency.js'
import { colorByKey, getIconComponent } from '../../utils/categories.js'
import CurrencyInput from '../ui/CurrencyInput.vue'

defineProps({ expenses: { type: Array, default: () => [] } })
defineEmits(['open-rent', 'delete'])

const store = useDashboardStore()
const catStore = useCategoriesStore()

const respLabels = computed(() => ({
  alvaro: store.nameAlvaro,
  alexandra: store.nameAlexandra,
  conjunto: 'Casal'
}))
const RESP_BADGES = {
  alvaro:    'bg-blue-50 text-blue-600 dark:bg-blue-950/40 dark:text-blue-300',
  alexandra: 'bg-pink-50 text-pink-600 dark:bg-pink-950/40 dark:text-pink-300',
  conjunto:  'bg-brand-canvas-soft-light text-brand-ink-mute-light dark:bg-brand-canvas-dark dark:text-brand-ink-mute-dark',
}

function getCategory(id) {
  return id ? catStore.getCategory(id) : null
}

function catColor(id) {
  const cat = getCategory(id)
  return cat ? colorByKey(cat.color) : colorByKey('slate')
}

const editingId = ref(null)
const editValue = ref(0)
const editInputRef = ref(null)

function startEdit(expense) {
  editingId.value = expense.id
  editValue.value = parseFloat(expense.amount) || 0
  nextTick(() => editInputRef.value?.$el?.querySelector('input')?.focus())
}

async function saveEdit() {
  if (editingId.value) {
    await store.updateExpenseAmount(editingId.value, editValue.value)
  }
  editingId.value = null
}

function cancelEdit() {
  editingId.value = null
}
</script>

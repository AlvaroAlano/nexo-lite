<template>
  <BaseModal v-model="open" title="Detalhes da Despesa" full-screen-on-mobile>
    <div v-if="expense" class="space-y-6 font-ss01">
      
      <!-- Top Header Area: Title & Amount -->
      <div class="text-center pb-4 border-b border-brand-hairline-light dark:border-brand-hairline-dark/40">
        <h3 class="text-xl font-semibold text-brand-ink-light dark:text-white mb-2 leading-tight">
          {{ expense.name }}
        </h3>
        
        <p class="text-3xl font-bold font-tabular text-brand-ink-light dark:text-white tracking-tight">
          {{ maskCurrency(expense.amount) }}
        </p>

        <!-- Status Badge -->
        <div class="mt-3 flex justify-center">
          <span
            class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border"
            :class="expense.is_paid
              ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20'
              : 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20'"
          >
            <span class="w-1.5 h-1.5 rounded-full" :class="expense.is_paid ? 'bg-emerald-500' : 'bg-amber-500'" />
            {{ expense.is_paid ? 'Pago' : 'Pendente de Pagamento' }}
          </span>
        </div>
      </div>

      <!-- Properties Grid -->
      <div class="grid grid-cols-2 gap-4">
        <!-- Categoria -->
        <div class="bg-brand-canvas-soft-light/40 dark:bg-brand-canvas-soft-dark/30 border border-brand-hairline-light dark:border-brand-hairline-dark/50 rounded-xl p-3.5 flex flex-col justify-between min-h-[80px]">
          <span class="text-[10px] font-semibold text-brand-ink-mute-light dark:text-brand-ink-mute-dark uppercase tracking-wider mb-1">Categoria</span>
          <div v-if="category" class="flex items-center gap-2">
            <span
              class="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0"
              :style="{ backgroundColor: catColor.light, color: catColor.text }"
            >
              <component :is="getIconComponent(category.icon)" :size="12" :stroke-width="2.5" />
            </span>
            <span class="text-sm font-semibold text-brand-ink-light dark:text-white truncate">{{ category.name }}</span>
          </div>
          <span v-else class="text-sm font-medium text-brand-ink-mute-light/50">—</span>
        </div>

        <!-- Responsável -->
        <div class="bg-brand-canvas-soft-light/40 dark:bg-brand-canvas-soft-dark/30 border border-brand-hairline-light dark:border-brand-hairline-dark/50 rounded-xl p-3.5 flex flex-col justify-between min-h-[80px]">
          <span class="text-[10px] font-semibold text-brand-ink-mute-light dark:text-brand-ink-mute-dark uppercase tracking-wider mb-1">Responsável</span>
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full" :class="responsavelDot" />
            <span class="text-sm font-semibold text-brand-ink-light dark:text-white truncate">{{ responsavelLabel }}</span>
          </div>
        </div>
      </div>

      <!-- Info Details List -->
      <div class="bg-brand-canvas-soft-light/20 dark:bg-brand-canvas-soft-dark/15 rounded-xl border border-brand-hairline-light dark:border-brand-hairline-dark/30 divide-y divide-brand-hairline-light dark:divide-brand-hairline-dark/30">
        <!-- Tipo de Despesa -->
        <div class="flex justify-between items-center px-4 py-3.5 text-sm">
          <span class="text-brand-ink-mute-light dark:text-brand-ink-mute-dark font-medium">Tipo de despesa</span>
          <span class="font-semibold text-brand-ink-light dark:text-white">{{ typeLabel }}</span>
        </div>

        <!-- Parcelas (se aplicável) -->
        <div v-if="expense.expense_type === 'installment'" class="flex justify-between items-center px-4 py-3.5 text-sm">
          <span class="text-brand-ink-mute-light dark:text-brand-ink-mute-dark font-medium">Progresso de parcelas</span>
          <span class="font-semibold text-brand-ink-light dark:text-white font-tabular">
            Parcela {{ expense.installment_current }} de {{ expense.installment_total }}
          </span>
        </div>
      </div>

      <!-- Composição do Aluguel (para despesas do tipo rent) -->
      <div v-if="expense.expense_type === 'rent'" class="space-y-3">
        <h4 class="text-xs font-bold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark">
          Itens do Aluguel
        </h4>
        <div v-if="expense.rent_items && expense.rent_items.length" class="rounded-xl overflow-hidden border border-brand-hairline-light dark:border-brand-hairline-dark/50 bg-white dark:bg-brand-canvas-soft-dark/40">
          <template v-for="(item, idx) in expense.rent_items" :key="item.id">
            <div class="px-4 py-3 text-sm flex items-center justify-between">
              <div>
                <p class="font-semibold text-brand-ink-light dark:text-white">{{ item.name }}</p>
                <div class="flex items-center gap-1.5 mt-0.5">
                  <span class="text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-full flex-shrink-0" :class="itemTypeBadge(item.type)">
                    {{ itemTypeLabel(item.type) }}
                  </span>
                  <span v-if="item.type === 'installment' && item.installment_current" class="text-[10px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark font-tabular">
                    {{ item.installment_current }}/{{ item.installment_total }}
                  </span>
                </div>
              </div>
              <span class="font-tabular font-semibold text-brand-ink-light dark:text-white">{{ maskCurrency(item.amount) }}</span>
            </div>
            <div v-if="idx < expense.rent_items.length - 1" class="h-px bg-brand-hairline-light dark:bg-brand-hairline-dark/30 mx-4" />
          </template>
        </div>
        <p v-else class="text-sm text-brand-ink-mute-light dark:text-brand-ink-mute-dark text-center py-4 bg-brand-canvas-soft-light/20 dark:bg-brand-canvas-soft-dark/10 rounded-xl">
          Nenhum sub-item cadastrado neste aluguel.
        </p>
      </div>

    </div>

    <!-- Footer Actions -->
    <template #footer>
      <div v-if="expense" class="space-y-2.5">
        <!-- Primary action: toggle status or edit details for rent -->
        <div class="flex gap-2">
          <!-- Toggle Paid -->
          <button
            @click="togglePaid"
            class="flex-1 py-3 px-4 rounded-full border text-sm font-semibold transition-all active:scale-[.98]"
            :class="expense.is_paid
              ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20 hover:bg-amber-500/15'
              : 'bg-emerald-500 text-white border-transparent hover:bg-emerald-600'"
          >
            {{ expense.is_paid ? 'Marcar como Pendente' : 'Marcar como Pago' }}
          </button>

          <!-- Edit Basic Details -->
          <button
            v-if="!store.isReadOnly && expense.category !== 'Caixinha'"
            @click="editExpense"
            class="px-5 py-3 rounded-full border border-brand-hairline-light dark:border-brand-hairline-dark text-sm font-semibold text-brand-ink-light dark:text-white hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark/30 active:scale-[.98] transition-colors"
          >
            Editar
          </button>
        </div>

        <div class="flex gap-2">
          <!-- Rent subitems details manager -->
          <button
            v-if="!store.isReadOnly && expense.expense_type === 'rent'"
            @click="openRentEditor"
            class="flex-1 py-3 px-4 rounded-full bg-brand-primary text-white text-sm font-semibold hover:bg-brand-primary-hover active:scale-[.98] transition-all"
          >
            Preencher Boleto (Itens)
          </button>

          <!-- Delete Expense -->
          <button
            v-if="!store.isReadOnly && expense.category !== 'Caixinha'"
            @click="deleteExpense"
            class="py-3 rounded-full border border-red-200 dark:border-red-950 text-red-500 hover:bg-red-500/10 dark:hover:bg-red-950/20 text-sm font-semibold active:scale-[.98] transition-all"
            :class="expense.expense_type === 'rent' ? 'px-5' : 'flex-1'"
          >
            Excluir despesa
          </button>
        </div>
      </div>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed } from 'vue'
import BaseModal from '../ui/BaseModal.vue'
import { useDashboardStore } from '../../stores/dashboard.js'
import { useCategoriesStore } from '../../stores/categories.js'
import { usePrivacyMode } from '../../composables/usePrivacyMode.js'
import { colorByKey, getIconComponent } from '../../utils/categories.js'

const { maskCurrency } = usePrivacyMode()
const props = defineProps({
  modelValue: Boolean,
  expense: { type: Object, default: null }
})
const emit = defineEmits(['update:modelValue', 'edit', 'open-rent', 'delete'])

const store = useDashboardStore()
const catStore = useCategoriesStore()

const open = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})

const category = computed(() =>
  props.expense?.category_id ? catStore.getCategory(props.expense.category_id) : null
)

const catColor = computed(() =>
  category.value ? colorByKey(category.value.color) : colorByKey('slate')
)

const responsavelLabel = computed(() => {
  if (!props.expense) return ''
  if (props.expense.responsavel === 'alvaro') return store.nameAlvaro
  if (props.expense.responsavel === 'alexandra') return store.nameAlexandra
  return 'Casal (Conjunto)'
})

const responsavelDot = computed(() => {
  if (!props.expense) return 'bg-slate-300'
  if (props.expense.responsavel === 'alvaro') return 'bg-blue-500'
  if (props.expense.responsavel === 'alexandra') return 'bg-pink-500'
  return 'bg-slate-400 dark:bg-slate-500'
})

const typeLabel = computed(() => {
  if (!props.expense) return ''
  const types = {
    fixed: 'Recorrência Fixa',
    variable: 'Variável Mensal',
    rent: 'Aluguel Variável',
    installment: 'Parcelamento'
  }
  return types[props.expense.expense_type] || props.expense.expense_type
})

const itemTypeLabel = (t) => {
  const labels = { fixed: 'Fixo', variable: 'Variável', installment: 'Parcela' }
  return labels[t] || t
}

const itemTypeBadge = (t) => {
  const badges = {
    fixed: 'bg-brand-canvas-soft-light text-brand-ink-mute-light dark:bg-brand-canvas-dark dark:text-brand-ink-mute-dark',
    variable: 'bg-amber-50 text-amber-600 dark:bg-amber-950/40 dark:text-amber-300',
    installment: 'bg-blue-50 text-blue-600 dark:bg-blue-950/40 dark:text-blue-300',
  }
  return badges[t] || badges.fixed
}

function togglePaid() {
  if (!props.expense) return
  store.togglePaid(props.expense.id)
}

function editExpense() {
  emit('edit', props.expense)
  open.value = false
}

function openRentEditor() {
  emit('open-rent', props.expense)
  open.value = false
}

function deleteExpense() {
  emit('delete', props.expense)
  open.value = false
}
</script>

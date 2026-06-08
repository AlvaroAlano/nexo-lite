<template>
  <div
    @click="$emit('click-detail', expense)"
    class="flex items-center gap-3 py-3.5 cursor-pointer hover:bg-brand-canvas-soft-light/10 dark:hover:bg-brand-canvas-soft-dark/10 transition-colors rounded-xl px-2 -mx-2"
  >
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

    <!-- Amount + actions: tudo numa única linha horizontal -->
    <div class="flex-shrink-0 flex items-center gap-2">
      <!-- Valor (ou input de edição) -->
      <div class="flex flex-col items-end" @click.stop>
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
        <button
          v-if="isRent"
          @click="$emit('open-rent', expense)"
          class="text-[11px] font-medium text-brand-primary dark:text-brand-primary-soft active:opacity-60 transition-opacity leading-none mt-0.5"
        >
          Detalhar
        </button>
      </div>

      <!-- Opções (3 pontinhos) -->
      <div v-if="!store.isReadOnly && expense.category !== 'Caixinha'" class="relative" @click.stop>
        <button
          @click.stop="toggleMenu"
          class="w-7 h-7 flex items-center justify-center rounded-lg text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark/30 hover:text-brand-primary active:opacity-60 transition-all flex-shrink-0"
          title="Opções"
        >
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/>
          </svg>
        </button>
        <Transition name="dropdown">
          <div v-if="menuOpen" class="absolute right-0 top-8 z-30 min-w-[140px] rounded-xl bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark shadow-stripe-2 py-1 overflow-hidden">
            <button
              @click.stop="onDetail"
              class="w-full flex items-center gap-2 px-3.5 py-2 text-left text-xs text-brand-ink-light dark:text-white hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-dark transition-colors"
            >
              Ver detalhes
            </button>
            <button
              @click.stop="onEdit"
              class="w-full flex items-center gap-2 px-3.5 py-2 text-left text-xs text-brand-ink-light dark:text-white hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-dark transition-colors"
            >
              Editar
            </button>
            <div class="h-px bg-brand-hairline-light dark:bg-brand-hairline-dark/40" />
            <button
              @click.stop="onDelete"
              class="w-full flex items-center gap-2 px-3.5 py-2 text-left text-xs text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors"
            >
              Excluir
            </button>
          </div>
        </Transition>
      </div>

      <!-- Toggle pago -->
      <button
        @click.stop="store.togglePaid(expense.id)"
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
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useDashboardStore } from '../../stores/dashboard.js'
import { useCategoriesStore } from '../../stores/categories.js'
import { formatCurrency } from '../../utils/currency.js'
import { colorByKey, getIconComponent } from '../../utils/categories.js'
import CurrencyInput from '../ui/CurrencyInput.vue'

const props = defineProps({
  expense: { type: Object, required: true },
})
const emit = defineEmits(['open-rent', 'delete', 'edit', 'click-detail'])

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
const menuOpen = ref(false)

function toggleMenu() {
  menuOpen.value = !menuOpen.value
  if (menuOpen.value) {
    setTimeout(() => {
      document.addEventListener('click', closeMenu)
    }, 0)
  }
}

function closeMenu() {
  menuOpen.value = false
  document.removeEventListener('click', closeMenu)
}

onUnmounted(() => {
  document.removeEventListener('click', closeMenu)
})

function onDetail() {
  closeMenu()
  emit('click-detail', props.expense)
}

function onEdit() {
  closeMenu()
  emit('edit', props.expense)
}

function onDelete() {
  closeMenu()
  emit('delete', props.expense)
}

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

<style scoped>
.dropdown-enter-active { animation: dropdown-pop 0.14s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
.dropdown-leave-active { animation: dropdown-pop 0.1s ease-in reverse forwards; }
@keyframes dropdown-pop {
  from { opacity: 0; transform: scale(0.88) translateY(-6px); }
  to   { opacity: 1; transform: scale(1)    translateY(0); }
}
</style>

<template>
  <div class="bg-white dark:bg-brand-canvas-soft-dark rounded-stripe-card border border-brand-hairline-light dark:border-brand-hairline-dark overflow-hidden shadow-stripe-1 font-ss01 transition-colors duration-150">
    <table class="w-full text-sm">
      <thead>
        <tr class="border-b border-brand-hairline-light dark:border-brand-hairline-dark bg-brand-canvas-soft-light/30 dark:bg-brand-canvas-dark/25">
          <th class="text-left px-4 py-3 text-xs font-semibold text-brand-ink-mute-light dark:text-brand-ink-mute-dark uppercase tracking-wide">
            Despesa
          </th>
          <th class="text-left px-4 py-3 text-xs font-semibold text-brand-ink-mute-light dark:text-brand-ink-mute-dark uppercase tracking-wide w-[140px]">
            Categoria
          </th>
          <th class="text-right px-4 py-3 text-xs font-semibold text-brand-ink-mute-light dark:text-brand-ink-mute-dark uppercase tracking-wide w-[120px]">
            Valor
          </th>
          <th class="text-center px-3 py-3 text-xs font-semibold text-brand-ink-mute-light dark:text-brand-ink-mute-dark uppercase tracking-wide w-[90px]">
            Status
          </th>
          <th v-if="!store.isReadOnly" class="w-[80px]"></th>
        </tr>
      </thead>
      <tbody class="divide-y divide-brand-hairline-light dark:divide-brand-hairline-dark/30">
        <tr
          v-for="expense in expenses"
          :key="expense.id"
          @click="$emit('click-detail', expense)"
          class="group hover:bg-brand-canvas-soft-light/45 dark:hover:bg-brand-canvas-soft-dark/30 transition-colors cursor-pointer"
          :class="expense.is_paid ? 'opacity-60' : ''"
        >
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

          <!-- Amount -->
          <td class="px-4 py-3.5 text-right w-[120px]" @click.stop>
            <template v-if="expense.expense_type === 'rent'">
              <button
                @click.stop="$emit('open-rent', expense)"
                class="font-tabular font-medium text-brand-ink-light dark:text-white hover:text-brand-primary transition-colors inline-flex items-center gap-1"
              >
                {{ maskCurrency(expense.amount) }}
                <span class="text-[10px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark">↗</span>
              </button>
            </template>
            <template v-else>
              <span
                v-if="editingId !== expense.id"
                @click.stop="startEdit(expense)"
                class="font-tabular font-medium text-brand-ink-light dark:text-white cursor-pointer hover:text-brand-primary transition-colors"
              >
                {{ maskCurrency(expense.amount) }}
              </span>
              <div v-else class="inline-flex items-center gap-1.5" @click.stop>
                <CurrencyInput
                  ref="editInputRef"
                  v-model="editValue"
                  @confirm="saveEdit"
                  @cancel="cancelEdit"
                  @blur="handleBlur"
                  hide-prefix
                  input-class="font-tabular font-medium text-brand-ink-light dark:text-white text-right bg-white dark:bg-brand-canvas-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-stripe-input px-2 py-0.5 outline-none w-24 focus:ring-2 focus:ring-brand-primary/20"
                />
                <button
                  @mousedown.prevent
                  @click="saveEdit"
                  class="w-6 h-6 flex items-center justify-center rounded-full bg-emerald-500 hover:bg-emerald-600 text-white transition-all active:scale-95 duration-200 flex-shrink-0"
                  :class="{ 'animate-check-pop': animating }"
                  title="Confirmar"
                >
                  <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                </button>
              </div>
            </template>
          </td>

          <!-- Paid toggle -->
          <td class="px-3 py-3.5 text-center w-[90px]" @click.stop>
            <button
              @click.stop="store.togglePaid(expense.id)"
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

          <!-- Actions: 3-dot dropdown menu -->
          <td v-if="!store.isReadOnly" class="px-2 py-3.5 w-[80px]" @click.stop>
            <div v-if="expense.category !== 'Caixinha'" class="opacity-0 group-hover:opacity-100 focus-within:opacity-100 flex items-center justify-center relative transition-all">
              <button
                @click.stop="toggleMenu(expense.id)"
                class="w-7 h-7 flex items-center justify-center rounded-lg text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark/30 hover:text-brand-primary active:opacity-60 transition-all"
                title="Opções"
              >
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/>
                </svg>
              </button>
              <Transition name="dropdown">
                <div v-if="activeMenuId === expense.id" class="absolute right-0 top-8 z-30 min-w-[150px] rounded-xl bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark shadow-stripe-2 py-1 overflow-hidden">
                  <button
                    @click.stop="onDetail(expense)"
                    class="w-full flex items-center gap-2.5 px-3.5 py-2.5 text-left text-sm text-brand-ink-light dark:text-white hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-dark transition-colors"
                  >
                    <svg class="w-3.5 h-3.5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
                    </svg>
                    Ver detalhes
                  </button>
                  <button
                    @click.stop="onEdit(expense)"
                    class="w-full flex items-center gap-2.5 px-3.5 py-2.5 text-left text-sm text-brand-ink-light dark:text-white hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-dark transition-colors"
                  >
                    <svg class="w-3.5 h-3.5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                    </svg>
                    Editar
                  </button>
                  <div class="h-px bg-brand-hairline-light dark:bg-brand-hairline-dark/40" />
                  <button
                    @click.stop="onDelete(expense)"
                    class="w-full flex items-center gap-2.5 px-3.5 py-2.5 text-left text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors"
                  >
                    <svg class="w-3.5 h-3.5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/>
                    </svg>
                    Excluir
                  </button>
                </div>
              </Transition>
            </div>
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
import { ref, nextTick, computed, onMounted, onUnmounted } from 'vue'
import { useDashboardStore } from '../../stores/dashboard.js'
import { useCategoriesStore } from '../../stores/categories.js'
import { usePrivacyMode } from '../../composables/usePrivacyMode.js'
import { colorByKey, getIconComponent } from '../../utils/categories.js'
import CurrencyInput from '../ui/CurrencyInput.vue'
import { CLOSE_MENUS_EVENT, broadcastMenuOpen } from '../../utils/menuBus.js'

const props = defineProps({ expenses: { type: Array, default: () => [] } })
const { maskCurrency } = usePrivacyMode()
const emit = defineEmits(['open-rent', 'delete', 'edit', 'click-detail'])

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
const activeMenuId = ref(null)

function toggleMenu(id) {
  if (activeMenuId.value === id) {
    closeMenu()
  } else {
    broadcastMenuOpen()
    activeMenuId.value = id
    setTimeout(() => document.addEventListener('click', closeMenu), 0)
  }
}

function closeMenu() {
  activeMenuId.value = null
  document.removeEventListener('click', closeMenu)
}

onMounted(() => document.addEventListener(CLOSE_MENUS_EVENT, closeMenu))
onUnmounted(() => {
  document.removeEventListener(CLOSE_MENUS_EVENT, closeMenu)
  document.removeEventListener('click', closeMenu)
})

function onDetail(expense) {
  closeMenu()
  emit('click-detail', expense)
}

function onEdit(expense) {
  closeMenu()
  emit('edit', expense)
}

function onDelete(expense) {
  closeMenu()
  emit('delete', expense)
}

const animating = ref(false)

function startEdit(expense) {
  editingId.value = expense.id
  editValue.value = parseFloat(expense.amount) || 0
  nextTick(() => editInputRef.value?.$el?.querySelector('input')?.focus())
}

function handleBlur() {
  setTimeout(() => {
    if (editingId.value && !animating.value) {
      cancelEdit()
    }
  }, 180)
}

async function saveEdit() {
  if (animating.value) return
  if (!editingId.value) return
  
  const currentExpense = props.expenses.find(e => e.id === editingId.value)
  if (currentExpense && editValue.value === (parseFloat(currentExpense.amount) || 0)) {
    editingId.value = null
    return
  }
  
  animating.value = true
  setTimeout(async () => {
    try {
      await store.updateExpenseAmount(editingId.value, editValue.value)
    } finally {
      editingId.value = null
      animating.value = false
    }
  }, 300)
}

function cancelEdit() {
  editingId.value = null
}
</script>

<style scoped>
.dropdown-enter-active { animation: dropdown-pop 0.14s var(--ease-out-quint) forwards; }
.dropdown-leave-active { animation: dropdown-pop 0.1s ease-in reverse forwards; }
@keyframes dropdown-pop {
  from { opacity: 0; transform: scale(0.88) translateY(-6px); }
  to   { opacity: 1; transform: scale(1)    translateY(0); }
}

@keyframes check-pop-out {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.35);
    opacity: 0.8;
  }
  100% {
    transform: scale(1.6);
    opacity: 0;
  }
}
.animate-check-pop {
  animation: check-pop-out 300ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
</style>

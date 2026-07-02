<template>
  <div
    @click="$emit('click-detail', expense)"
    class="flex items-center gap-3 py-3.5 cursor-pointer hover:bg-brand-canvas-soft-light/10 dark:hover:bg-brand-canvas-soft-dark/10 transition-colors rounded-xl px-2 -mx-2"
    :class="{ 'opacity-50': expense.is_excluded }"
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
      <!-- tem categoria mas ainda não carregou → skeleton (não 'quebrado') -->
      <div v-else-if="expense.category_id" class="w-4 h-4 rounded-full bg-slate-200 dark:bg-slate-700 animate-pulse" />
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
        <EyeOff
          v-if="expense.is_excluded"
          class="w-3 h-3 flex-shrink-0 text-brand-ink-mute-light dark:text-brand-ink-mute-dark"
        />
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
          {{ maskCurrency(expense.amount) }}
        </span>
        <div v-else class="flex items-center gap-1.5" @click.stop>
          <CurrencyInput
            v-model="editValue"
            @confirm="saveEdit"
            @cancel="cancelEdit"
            @blur="handleBlur"
            hide-prefix
            input-class="font-tabular font-medium text-sm text-right text-brand-ink-light dark:text-white bg-transparent border-b border-brand-primary outline-none w-20"
          />
          <button
            @mousedown.prevent
            @click="saveEdit"
            class="w-6 h-6 flex items-center justify-center rounded-full bg-emerald-500 hover:bg-emerald-600 text-white transition-all active:scale-95 duration-200 flex-shrink-0"
            :class="{ 'animate-check-pop': animating }"
            title="Confirmar"
          >
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </button>
        </div>
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
          <div v-if="menuOpen" class="absolute right-0 top-8 z-30 min-w-[150px] rounded-xl bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark shadow-stripe-2 py-1 overflow-hidden">
            <button
              @click.stop="onDetail"
              class="w-full flex items-center gap-2.5 px-3.5 py-2.5 text-left text-sm text-brand-ink-light dark:text-white hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-dark transition-colors"
            >
              <svg class="w-3.5 h-3.5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
              </svg>
              Ver detalhes
            </button>
            <button
              @click.stop="onEdit"
              class="w-full flex items-center gap-2.5 px-3.5 py-2.5 text-left text-sm text-brand-ink-light dark:text-white hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-dark transition-colors"
            >
              <svg class="w-3.5 h-3.5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
              Editar
            </button>
            <button
              @click.stop="onToggleExclusion"
              class="w-full flex items-center gap-2.5 px-3.5 py-2.5 text-left text-sm text-brand-ink-light dark:text-white hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-dark transition-colors"
            >
              <component :is="expense.is_excluded ? Eye : EyeOff" class="w-3.5 h-3.5 flex-shrink-0" />
              {{ expense.is_excluded ? 'Incluir no cálculo' : 'Excluir do cálculo' }}
            </button>
            <div class="h-px bg-brand-hairline-light dark:bg-brand-hairline-dark/40" />
            <button
              @click.stop="onDelete"
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

      <!-- Toggle pago -->
      <button
        @click.stop="store.togglePaid(expense.id).catch(() => {})"
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useDashboardStore } from '../../stores/dashboard.js'
import { useCategoriesStore } from '../../stores/categories.js'
import { usePrivacyMode } from '../../composables/usePrivacyMode.js'
import { colorByKey, getIconComponent } from '../../utils/categories.js'
const { maskCurrency } = usePrivacyMode()
import CurrencyInput from '../ui/CurrencyInput.vue'
import { CLOSE_MENUS_EVENT, broadcastMenuOpen } from '../../utils/menuBus.js'
import { Eye, EyeOff } from 'lucide-vue-next'

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
  if (menuOpen.value) {
    closeMenu()
  } else {
    broadcastMenuOpen()
    menuOpen.value = true
    setTimeout(() => document.addEventListener('click', closeMenu), 0)
  }
}

function closeMenu() {
  menuOpen.value = false
  document.removeEventListener('click', closeMenu)
}

onMounted(() => document.addEventListener(CLOSE_MENUS_EVENT, closeMenu))
onUnmounted(() => {
  document.removeEventListener(CLOSE_MENUS_EVENT, closeMenu)
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

function onToggleExclusion() {
  closeMenu()
  store.toggleExpenseExclusion(props.expense.id).catch(() => {})
}

const animating = ref(false)

function startEdit() {
  editValue.value = parseFloat(props.expense.amount) || 0
  editing.value = true
}

function handleBlur() {
  setTimeout(() => {
    if (editing.value && !animating.value) {
      cancelEdit()
    }
  }, 180)
}

async function saveEdit() {
  if (animating.value) return
  if (editValue.value === (parseFloat(props.expense.amount) || 0)) {
    editing.value = false
    return
  }
  animating.value = true
  
  setTimeout(async () => {
    try {
      await store.updateExpenseAmount(props.expense.id, editValue.value)
    } catch {
      // otimista já reverteu o valor na store
    } finally {
      editing.value = false
      animating.value = false
    }
  }, 300)
}

function cancelEdit() {
  editing.value = false
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

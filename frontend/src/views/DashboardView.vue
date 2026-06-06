<template>
  <div class="max-w-5xl mx-auto px-4 pt-5 pb-6 font-ss01">

    <!-- Loading -->
    <div v-if="store.loading" class="flex flex-col items-center justify-center py-20 gap-3">
      <div class="w-6 h-6 rounded-full border-2 border-brand-hairline-light dark:border-brand-hairline-dark border-t-brand-primary animate-spin" />
      <p class="text-brand-ink-mute-light dark:text-brand-ink-mute-dark text-sm">Carregando…</p>
    </div>

    <!-- Future month: not yet created -->
    <div
      v-else-if="store.notFoundMonth"
      class="flex flex-col items-center justify-center py-20 gap-4 text-center"
    >
      <div class="w-12 h-12 rounded-stripe-card bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark flex items-center justify-center">
        <svg class="w-6 h-6 text-brand-ink-mute-light dark:text-brand-ink-mute-dark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
          <line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
          <line x1="3" y1="10" x2="21" y2="10"/>
        </svg>
      </div>
      <div>
        <p class="font-medium text-brand-ink-light dark:text-white">Mês ainda não criado</p>
        <p class="text-sm text-brand-ink-mute-light dark:text-brand-ink-mute-dark mt-1 max-w-xs">
          Clique em "Fechar mês atual" para avançar e criar este período.
        </p>
      </div>
      <button
        @click="showTurnover = true"
        class="flex items-center gap-2 px-5 py-2.5 rounded-full bg-brand-primary text-white text-sm font-medium hover:bg-brand-primary-hover active:scale-95 transition-all"
      >
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M17 1l4 4-4 4"/><path d="M3 11V9a4 4 0 014-4h14"/>
          <path d="M7 23l-4-4 4-4"/><path d="M21 13v2a4 4 0 01-4 4H3"/>
        </svg>
        Fechar mês atual e criar próximo
      </button>
    </div>

    <!-- Error -->
    <div v-else-if="store.error" class="bg-red-500/10 border border-red-500/20 rounded-stripe-card p-5 text-center dark:bg-red-950/20 dark:border-red-900/30">
      <p class="text-red-600 dark:text-red-400 text-sm font-medium">{{ store.error }}</p>
      <button @click="store.fetchCurrent()" class="mt-3 text-xs text-red-600 dark:text-red-400 underline">Tentar novamente</button>
    </div>

    <template v-else-if="store.period">
      <!-- ═══ Desktop: 2-column grid | Mobile: stacked ═══ -->
      <div class="md:grid md:grid-cols-[300px_1fr] md:gap-8 md:items-start">

        <!-- ── LEFT: Balance summary (sticky sidebar on desktop) ── -->
        <div class="md:sticky md:top-[60px] md:self-start">
          <BalanceSummary />

          <!-- Add expense — desktop sidebar -->
          <div v-if="!store.isReadOnly" class="hidden md:block">
            <Transition name="btn-bounce">
              <div v-if="!showAddForm">
                <button
                  @click="showAddForm = true"
                  class="w-full py-2.5 rounded-stripe-input border border-dashed border-brand-hairline-light dark:border-brand-hairline-dark text-brand-ink-mute-light dark:text-brand-ink-mute-dark text-sm font-medium hover:border-brand-primary hover:text-brand-primary dark:hover:text-white transition-colors"
                >
                  + Nova despesa
                </button>
              </div>
            </Transition>

            <Transition name="form-slide">
            <form v-if="showAddForm" @submit.prevent="quickAdd" class="bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-stripe-card p-4 space-y-3">
              <div class="flex items-center justify-between mb-1">
                <span class="text-sm font-semibold text-brand-ink-light dark:text-white">Nova despesa</span>
                <button type="button" @click="showAddForm = false" class="text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:text-brand-ink-light dark:hover:text-white">
                  <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              </div>
              <input
                v-model="addForm.name"
                placeholder="Nome da despesa"
                required
                class="w-full px-3 py-2 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
              />
              <div class="grid grid-cols-2 gap-2">
                <CategoryPicker v-model="addForm.category_id" />
                <AppSelect v-model="addForm.responsavel" :options="responsavelOpts" />
              </div>
              <CurrencyInput
                v-model="addForm.amount"
                input-class="w-full pr-3 py-2 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input font-tabular text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
              />
              <button
                type="submit"
                :disabled="!addForm.name.trim() || store.saving"
                class="w-full py-2 rounded-full bg-brand-primary text-white text-sm font-medium hover:bg-brand-primary-hover disabled:opacity-40 active:scale-[.98] transition-all"
              >
                {{ store.saving ? 'Adicionando…' : 'Adicionar' }}
              </button>
            </form>
            </Transition>
          </div>
        </div>

        <!-- ── RIGHT: Expense list + turnover ── -->
        <div>
          <!-- Mobile: compact rows -->
          <div class="divide-y divide-brand-hairline-light/60 dark:divide-brand-hairline-dark/50 md:hidden">
            <ExpenseCard
              v-for="expense in store.filteredExpenses"
              :key="expense.id"
              :expense="expense"
              @open-rent="openRent"
              @delete="deleteWithUndo"
            />
            <p v-if="!store.filteredExpenses.length" class="text-center py-10 text-brand-ink-mute-light dark:text-brand-ink-mute-dark text-sm">
              Nenhuma despesa neste mês ainda.
            </p>
          </div>

          <!-- Desktop: table with category column -->
          <ExpenseTable
            class="hidden md:block"
            :expenses="store.filteredExpenses"
            @open-rent="openRent"
            @delete="deleteWithUndo"
          />


          <!-- Turnover -->
          <div v-if="!store.isReadOnly" class="mt-8 pt-6 border-t border-brand-hairline-light dark:border-brand-hairline-dark">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-semibold text-brand-ink-light dark:text-white">Virada de Mês</p>
                <p class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark mt-0.5">Fecha o mês atual e abre o próximo</p>
              </div>
              <button
                @click="showTurnover = true"
                class="flex items-center gap-2 px-4 py-2 rounded-full border border-brand-hairline-light dark:border-brand-hairline-dark text-sm font-medium text-brand-ink-light dark:text-white hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark/30 active:scale-95 transition-all"
              >
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17 1l4 4-4 4"/><path d="M3 11V9a4 4 0 014-4h14"/>
                  <path d="M7 23l-4-4 4-4"/><path d="M21 13v2a4 4 0 01-4 4H3"/>
                </svg>
                Fechar mês
              </button>
            </div>
          </div>
        </div>

      </div>
    </template>

    <!-- Modals -->
    <RentModal v-model="showRent" :expense="rentExpense" />
    <TurnoverModal v-model="showTurnover" />
    <!-- Undo toast — aparece 5s após deletar uma despesa -->
    <Teleport to="body">
      <Transition name="toast-slide">
        <div
          v-if="undoState"
          :key="undoKey"
          class="fixed bottom-24 md:bottom-8 left-0 right-0 z-[200] flex justify-center px-4 pointer-events-none"
        >
          <div class="pointer-events-auto w-full max-w-sm rounded-xl bg-[#18181b] border border-white/10 shadow-2xl overflow-hidden">
            <div class="flex items-center justify-between gap-4 px-4 py-3">
              <span class="text-sm text-white truncate">"{{ undoState.expense.name }}" removida</span>
              <button
                @click="cancelUndo"
                class="text-sm font-semibold text-brand-primary-soft shrink-0 hover:text-white transition-colors"
              >Desfazer</button>
            </div>
            <div class="h-0.5 bg-white/10">
              <div class="h-full bg-brand-primary toast-progress" />
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <BaseModal v-model="showExpenseModal" title="Nova Despesa" :full-screen-on-mobile="true">
      <div class="space-y-3">
        <input
          v-model="addForm.name"
          placeholder="Nome da despesa"
          class="w-full px-4 py-3 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
        />
        <div class="grid grid-cols-2 gap-2">
          <CategoryPicker v-model="addForm.category_id" />
          <AppSelect v-model="addForm.responsavel" :options="responsavelOpts" />
        </div>
        <CurrencyInput
          v-model="addForm.amount"
          input-class="w-full pr-4 py-3 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input font-tabular text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
        />
        <label class="flex items-center gap-3 py-1 cursor-pointer select-none">
          <button
            type="button"
            @click="addForm.is_paid = !addForm.is_paid"
            class="w-5 h-5 rounded border flex items-center justify-center transition-colors flex-shrink-0"
            :class="addForm.is_paid ? 'bg-brand-primary border-brand-primary' : 'border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark'"
          >
            <svg v-if="addForm.is_paid" class="w-3 h-3 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </button>
          <span class="text-sm text-brand-ink-light dark:text-white">Já paguei</span>
        </label>
      </div>
      <template #footer>
        <button
          @click="quickAdd"
          :disabled="!addForm.name.trim() || store.saving"
          class="w-full py-3 rounded-full bg-brand-primary text-white text-sm font-medium hover:bg-brand-primary-hover disabled:opacity-40 active:scale-[.98] transition-all"
        >
          {{ store.saving ? 'Adicionando…' : 'Adicionar despesa' }}
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, reactive, computed } from 'vue'
import { useDashboardStore } from '../stores/dashboard.js'
import BalanceSummary from '../components/dashboard/BalanceSummary.vue'
import ExpenseCard from '../components/dashboard/ExpenseCard.vue'
import ExpenseTable from '../components/dashboard/ExpenseTable.vue'
import RentModal from '../components/modals/RentModal.vue'
import TurnoverModal from '../components/modals/TurnoverModal.vue'
import BaseModal from '../components/ui/BaseModal.vue'
import CategoryPicker from '../components/ui/CategoryPicker.vue'
import CurrencyInput from '../components/ui/CurrencyInput.vue'
import AppSelect from '../components/ui/AppSelect.vue'

const store = useDashboardStore()

const showRent = ref(false)
const rentExpense = ref(null)
const showTurnover = ref(false)
const showAddForm = ref(false)
const showExpenseModal = ref(false)

const addForm = reactive({ name: '', category_id: null, responsavel: 'conjunto', amount: 0, is_paid: false })

const undoState = ref(null)  // { expense, timerId }
const undoKey = ref(0)

function deleteWithUndo(expense) {
  if (store.isReadOnly) return
  if (undoState.value) {
    clearTimeout(undoState.value.timerId)
    store.hardDeleteExpense(undoState.value.expense.id)
  }
  store.removeExpenseLocally(expense.id)
  const timerId = setTimeout(() => {
    store.hardDeleteExpense(expense.id)
    undoState.value = null
  }, 5000)
  undoKey.value++
  undoState.value = { expense, timerId }
}

function cancelUndo() {
  if (!undoState.value) return
  clearTimeout(undoState.value.timerId)
  store.restoreExpense(undoState.value.expense)
  undoState.value = null
}

const responsavelOpts = computed(() => [
  { value: 'conjunto', label: 'Casal' },
  { value: 'alvaro',   label: store.nameAlvaro },
  { value: 'alexandra', label: store.nameAlexandra },
])

function resetAddForm() {
  addForm.name = ''
  addForm.category_id = null
  addForm.amount = 0
  addForm.responsavel = 'conjunto'
  addForm.is_paid = false
}

// FAB / header "+" → opens modal
watch(
  () => store.quickAddOpen,
  (val) => {
    if (val && !store.isReadOnly && store.period) {
      showExpenseModal.value = true
      store.quickAddOpen = false
    }
  }
)

watch(showExpenseModal, (val) => {
  if (!val) {
    resetAddForm()
  }
})

onMounted(async () => {
  await store.fetchCurrent()
  if (store.quickAddOpen && !store.isReadOnly && store.period) {
    showExpenseModal.value = true
    store.quickAddOpen = false
  }
})

function openRent(expense) {
  rentExpense.value = expense
  showRent.value = true
}

async function quickAdd() {
  await store.addExpense({
    name: addForm.name.trim(),
    category_id: addForm.category_id,
    expense_type: 'variable',
    responsavel: addForm.responsavel,
    amount: addForm.amount,
    is_paid: addForm.is_paid,
  })
  showAddForm.value = false
  showExpenseModal.value = false
}
</script>

<style scoped>
/* Button: shrinks out fast, pops back in with spring overshoot */
.btn-bounce-leave-active {
  animation: btn-shrink 0.18s ease-in forwards;
}
.btn-bounce-enter-active {
  animation: btn-pop 0.42s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

@keyframes btn-shrink {
  from { opacity: 1; transform: scale(1); }
  to   { opacity: 0; transform: scale(0.55); }
}

@keyframes btn-pop {
  0%   { opacity: 0; transform: scale(0.55); }
  60%  { opacity: 1; transform: scale(1.07); }
  80%  { transform: scale(0.97); }
  100% { opacity: 1; transform: scale(1); }
}

/* Form: slides down softly */
.form-slide-enter-active {
  animation: form-in 0.24s ease-out forwards;
}
.form-slide-leave-active {
  animation: form-in 0.16s ease-in reverse forwards;
}

@keyframes form-in {
  from { opacity: 0; transform: translateY(-8px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

/* Undo toast */
.toast-slide-enter-active { animation: toast-in  0.3s cubic-bezier(0.34, 1.56, 0.64, 1) forwards; }
.toast-slide-leave-active { animation: toast-out 0.2s ease-in forwards; }

@keyframes toast-in  { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes toast-out { from { opacity: 1; transform: translateY(0);    } to { opacity: 0; transform: translateY(20px); } }

.toast-progress {
  animation: toast-shrink 5s linear forwards;
}
@keyframes toast-shrink {
  from { width: 100%; }
  to   { width: 0%; }
}
</style>

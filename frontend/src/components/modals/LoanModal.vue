<template>
  <BaseModal v-model="open" :title="modalTitle" full-screen-on-mobile>

    <!-- ── CREATE / EDIT FORM ─────────────────────────────────────────────── -->
    <div v-if="isEditing" class="space-y-4 font-ss01">

      <!-- Direction picker -->
      <div class="grid grid-cols-2 gap-2">
        <button
          type="button"
          @click="form.direction = 'me_deve'"
          class="flex flex-col items-center gap-1.5 py-4 px-3 rounded-xl border-2 transition-all duration-150 active:scale-95"
          :class="form.direction === 'me_deve'
            ? 'border-emerald-500 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
            : 'border-brand-hairline-light dark:border-brand-hairline-dark text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:border-emerald-300 dark:hover:border-emerald-800'"
        >
          <ArrowDownLeft :size="22" stroke-width="2" />
          <span class="text-sm font-semibold">Me devem</span>
          <span class="text-[10px] opacity-70 text-center leading-tight">Alguém te deve dinheiro</span>
        </button>
        <button
          type="button"
          @click="form.direction = 'eu_devo'"
          class="flex flex-col items-center gap-1.5 py-4 px-3 rounded-xl border-2 transition-all duration-150 active:scale-95"
          :class="form.direction === 'eu_devo'
            ? 'border-red-400 bg-red-500/10 text-red-600 dark:text-red-400'
            : 'border-brand-hairline-light dark:border-brand-hairline-dark text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:border-red-300 dark:hover:border-red-900'"
        >
          <ArrowUpRight :size="22" stroke-width="2" />
          <span class="text-sm font-semibold">Eu devo</span>
          <span class="text-[10px] opacity-70 text-center leading-tight">Você deve a alguém</span>
        </button>
      </div>

      <!-- Name -->
      <div>
        <label class="text-[10px] font-semibold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark block mb-1.5">
          {{ form.direction === 'me_deve' ? 'Quem te deve?' : 'Pra quem você deve?' }}
        </label>
        <input
          v-model="form.name"
          :placeholder="form.direction === 'me_deve' ? 'Ex: Irmão João, Amigo Pedro...' : 'Ex: Banco Caixa, Maria...'"
          class="w-full bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-xl px-4 py-3 text-sm text-brand-ink-light dark:text-white placeholder:text-brand-ink-mute-light dark:placeholder:text-brand-ink-mute-dark focus:outline-none focus:ring-2 focus:ring-brand-primary/30 transition-all"
        />
      </div>

      <!-- Amount -->
      <div>
        <label class="text-[10px] font-semibold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark block mb-1.5">
          Valor
        </label>
        <CurrencyInput
          v-model="form.amount"
          input-class="w-full text-left text-base py-3 px-4 bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-xl text-brand-ink-light dark:text-white"
        />
      </div>

      <!-- Juros (só faz sentido em dívidas que eu devo) -->
      <div v-if="form.direction === 'eu_devo'">
        <label class="text-[10px] font-semibold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark block mb-1.5">
          Juros ao mês
        </label>
        <div class="relative">
          <input
            v-model.number="form.interest_rate"
            type="number"
            inputmode="decimal"
            min="0"
            step="0.1"
            placeholder="0"
            class="w-full bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-xl pl-4 pr-12 py-3 text-sm text-brand-ink-light dark:text-white placeholder:text-brand-ink-mute-light dark:placeholder:text-brand-ink-mute-dark focus:outline-none focus:ring-2 focus:ring-brand-primary/30 transition-all font-tabular"
          />
          <span class="absolute right-4 top-1/2 -translate-y-1/2 text-sm text-brand-ink-mute-light dark:text-brand-ink-mute-dark pointer-events-none">% a.m.</span>
        </div>
        <p class="text-[10px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark mt-1.5">
          Deixe 0 se não houver juros. Isso alimenta o Plano de Quitação (Avalanche).
        </p>
      </div>

      <!-- Dates -->
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="text-[10px] font-semibold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark block mb-1.5">
            Data
          </label>
          <input
            type="date"
            v-model="form.loan_date"
            class="w-full bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-xl px-3 py-3 text-sm text-brand-ink-light dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-primary/30 transition-all"
          />
        </div>
        <div>
          <label class="text-[10px] font-semibold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark block mb-1.5">
            Prazo previsto
          </label>
          <input
            type="date"
            v-model="form.due_date"
            class="w-full bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-xl px-3 py-3 text-sm text-brand-ink-light dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-primary/30 transition-all"
          />
        </div>
      </div>
    </div>

    <!-- ── VIEW / DETAIL MODE ─────────────────────────────────────────────── -->
    <div v-else-if="editingLoan" class="space-y-5 font-ss01">

      <!-- Direction badge + Amount header -->
      <div class="text-center pb-4 border-b border-brand-hairline-light dark:border-brand-hairline-dark/40">
        <div class="flex justify-center mb-3">
          <span
            class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border"
            :class="editingLoan.direction === 'me_deve'
              ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20'
              : 'bg-red-500/10 text-red-600 dark:text-red-400 border-red-400/20'"
          >
            <component :is="editingLoan.direction === 'me_deve' ? ArrowDownLeft : ArrowUpRight" :size="12" />
            {{ editingLoan.direction === 'me_deve' ? 'Me devem' : 'Eu devo' }}
          </span>
        </div>

        <h3 class="text-xl font-semibold text-brand-ink-light dark:text-white mb-1 leading-tight">
          {{ editingLoan.name }}
        </h3>

        <p class="text-3xl font-bold font-tabular text-brand-ink-light dark:text-white tracking-tight">
          {{ fmt(editingLoan.estimated_amount) }}
        </p>
        <p v-if="hasPartialPayment" class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark mt-1">
          Original: <span class="font-tabular">{{ fmt(editingLoan.original_amount) }}</span>
        </p>
        <p v-if="editingLoan.direction === 'eu_devo' && parseFloat(editingLoan.interest_rate) > 0" class="text-xs text-amber-600 dark:text-amber-400 mt-1">
          Juros de <span class="font-tabular font-semibold">{{ fmtRate(editingLoan.interest_rate) }}% a.m.</span>
        </p>

        <!-- Status badge -->
        <div class="mt-3 flex justify-center">
          <span
            class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border"
            :class="editingLoan.status === 'quitado'
              ? 'bg-slate-500/10 text-slate-500 dark:text-slate-400 border-slate-500/20'
              : isOverdue
                ? 'bg-red-500/10 text-red-500 dark:text-red-400 border-red-500/20'
                : 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20'"
          >
            <span class="w-1.5 h-1.5 rounded-full" :class="editingLoan.status === 'quitado' ? 'bg-slate-400' : isOverdue ? 'bg-red-500' : 'bg-amber-500'" />
            {{ editingLoan.status === 'quitado' ? 'Quitado' : isOverdue ? 'Em atraso' : 'Em aberto' }}
          </span>
        </div>
      </div>

      <!-- Info grid -->
      <div class="grid grid-cols-2 gap-3">
        <div
          v-if="editingLoan.loan_date"
          class="bg-brand-canvas-soft-light/40 dark:bg-brand-canvas-soft-dark/30 border border-brand-hairline-light dark:border-brand-hairline-dark/50 rounded-xl p-3 flex flex-col gap-1 min-h-[70px] justify-between"
        >
          <span class="text-[10px] font-semibold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark">Data</span>
          <span class="text-sm font-semibold text-brand-ink-light dark:text-white">{{ fmtDate(editingLoan.loan_date) }}</span>
        </div>
        <div
          v-if="editingLoan.due_date"
          class="bg-brand-canvas-soft-light/40 dark:bg-brand-canvas-soft-dark/30 border rounded-xl p-3 flex flex-col gap-1 min-h-[70px] justify-between"
          :class="isOverdue
            ? 'border-red-400/40 bg-red-500/5 dark:bg-red-500/10'
            : 'border-brand-hairline-light dark:border-brand-hairline-dark/50'"
        >
          <span class="text-[10px] font-semibold uppercase tracking-wider" :class="isOverdue ? 'text-red-500' : 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark'">Prazo</span>
          <span class="text-sm font-semibold" :class="isOverdue ? 'text-red-500 dark:text-red-400' : 'text-brand-ink-light dark:text-white'">
            {{ fmtDate(editingLoan.due_date) }}
          </span>
        </div>
      </div>

      <!-- Payment progress bar (if partial payments) -->
      <div v-if="hasPartialPayment" class="space-y-1.5">
        <div class="flex items-center justify-between text-xs">
          <span class="text-brand-ink-mute-light dark:text-brand-ink-mute-dark">Progresso</span>
          <span class="font-tabular font-medium text-brand-ink-light dark:text-white">{{ progressPct }}%</span>
        </div>
        <div class="h-2 w-full bg-slate-100 dark:bg-zinc-800 rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-700"
            :class="editingLoan.direction === 'me_deve' ? 'bg-emerald-500' : 'bg-brand-primary'"
            :style="{ width: progressPct + '%' }"
          />
        </div>
        <p class="text-[11px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark">
          Pago: <span class="font-tabular">{{ fmt(paidAmount) }}</span> de <span class="font-tabular">{{ fmt(editingLoan.original_amount) }}</span>
        </p>
      </div>

      <!-- Registrar pagamento (inline form) -->
      <Transition name="form-slide">
        <div
          v-if="showPaymentForm && editingLoan.status === 'ativo'"
          class="p-3.5 rounded-xl border border-brand-primary/30 bg-brand-primary/5 dark:bg-brand-primary/10 space-y-3"
        >
          <p class="text-xs font-semibold text-brand-primary dark:text-brand-primary-soft uppercase tracking-wider">Registrar Pagamento</p>
          <div class="flex gap-2 items-center">
            <CurrencyInput
              v-model="paymentForm.amount"
              input-class="flex-1 text-sm py-2.5 px-3 bg-white dark:bg-brand-canvas-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-xl text-brand-ink-light dark:text-white"
            />
            <button
              @click="submitPayment"
              :disabled="!paymentForm.amount || store.saving"
              class="flex-shrink-0 p-2.5 rounded-xl bg-brand-primary text-white disabled:opacity-40 hover:bg-brand-primary-hover transition-colors"
            >
              <Check :size="16" />
            </button>
            <button
              @click="showPaymentForm = false"
              class="flex-shrink-0 p-2.5 rounded-xl text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark transition-colors"
            >
              <X :size="16" />
            </button>
          </div>
          <input
            v-model="paymentForm.notes"
            placeholder="Observação (opcional)"
            class="w-full bg-white dark:bg-brand-canvas-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-xl px-3 py-2 text-sm text-brand-ink-light dark:text-white placeholder:text-brand-ink-mute-light dark:placeholder:text-brand-ink-mute-dark focus:outline-none"
          />
        </div>
      </Transition>

      <!-- Payment history -->
      <div v-if="payments.length || loadingPayments" class="space-y-2">
        <h4 class="text-[10px] font-bold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark flex items-center gap-1.5">
          <History :size="11" />
          Histórico de pagamentos
        </h4>
        <div v-if="loadingPayments" class="flex justify-center py-3">
          <div class="w-4 h-4 rounded-full border-2 border-brand-hairline-light dark:border-brand-hairline-dark border-t-brand-primary animate-spin" />
        </div>
        <div v-else class="rounded-xl border border-brand-hairline-light dark:border-brand-hairline-dark/50 overflow-hidden bg-white dark:bg-brand-canvas-soft-dark/40">
          <div v-for="(pmt, idx) in payments" :key="pmt.id">
            <div class="px-4 py-3 flex items-start justify-between gap-3">
              <div class="flex-1 min-w-0">
                <p v-if="pmt.notes" class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark truncate">{{ pmt.notes }}</p>
                <p class="text-[10px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark mt-0.5">
                  {{ fmtDatetime(pmt.paid_at) }}
                </p>
              </div>
              <span class="font-tabular text-sm font-semibold text-emerald-600 dark:text-emerald-400 flex-shrink-0">
                - {{ fmt(pmt.amount) }}
              </span>
            </div>
            <div v-if="idx < payments.length - 1" class="h-px bg-brand-hairline-light dark:bg-brand-hairline-dark/30 mx-4" />
          </div>
        </div>
      </div>
    </div>

    <!-- ── FOOTER ──────────────────────────────────────────────────────────── -->
    <template #footer>
      <p v-if="actionError" class="text-red-500 dark:text-red-400 text-xs mb-2">{{ actionError }}</p>
      <!-- Create/edit footer -->
      <div v-if="isEditing" class="flex gap-2">
        <button
          @click="cancelEdit"
          class="flex-1 py-3 px-4 rounded-full border border-brand-hairline-light dark:border-brand-hairline-dark text-sm font-semibold text-brand-ink-light dark:text-white hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark transition-colors active:scale-[.98]"
        >
          Cancelar
        </button>
        <button
          @click="save"
          :disabled="!form.name.trim() || !form.amount || store.saving"
          class="flex-1 py-3 px-4 rounded-full bg-brand-primary text-white text-sm font-semibold hover:bg-brand-primary-hover transition-all active:scale-[.98] disabled:opacity-40"
        >
          {{ editingLoan ? 'Salvar alterações' : 'Registrar' }}
        </button>
      </div>

      <!-- View footer -->
      <div v-else-if="editingLoan" class="space-y-2.5">
        <button
          v-if="editingLoan.status === 'ativo'"
          @click="showPaymentForm = !showPaymentForm"
          class="w-full py-3 px-4 rounded-full bg-brand-primary text-white text-sm font-semibold hover:bg-brand-primary-hover transition-all active:scale-[.98]"
        >
          {{ showPaymentForm ? 'Cancelar pagamento' : 'Registrar pagamento' }}
        </button>
        <div class="flex gap-2">
          <button
            @click="startEdit"
            class="flex-1 py-3 px-4 rounded-full border border-brand-hairline-light dark:border-brand-hairline-dark text-sm font-semibold text-brand-ink-light dark:text-white hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark transition-colors active:scale-[.98]"
          >
            Editar
          </button>
          <button
            v-if="editingLoan.status === 'ativo'"
            @click="confirmSettle"
            class="flex-1 py-3 px-4 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-sm font-semibold hover:bg-emerald-500/20 transition-colors active:scale-[.98]"
          >
            Quitar
          </button>
          <button
            v-else
            @click="confirmReopen"
            class="flex-1 py-3 px-4 rounded-full border border-amber-400/30 bg-amber-500/10 text-amber-600 dark:text-amber-400 text-sm font-semibold hover:bg-amber-500/20 transition-colors active:scale-[.98]"
          >
            Reabrir
          </button>
        </div>
        <button
          @click="confirmDelete"
          class="w-full py-3 px-4 rounded-full border border-red-200 dark:border-red-950 text-red-500 hover:bg-red-500/10 text-sm font-semibold transition-all active:scale-[.98]"
        >
          Excluir
        </button>
      </div>
    </template>

  </BaseModal>

  <!-- Confirm modals -->
  <ConfirmModal
    v-model="showSettleConfirm"
    title="Quitar empréstimo"
    :message="`Marcar '${editingLoan?.name}' como quitado?`"
    confirm-label="Quitar"
    :loading="settling"
    :error-message="settleError"
    @confirm="doSettle"
  />
  <ConfirmModal
    v-model="showDeleteConfirm"
    title="Excluir empréstimo"
    :message="`Excluir '${editingLoan?.name}'? Isso não pode ser desfeito.`"
    confirm-label="Excluir"
    variant="danger"
    :loading="deletingLoan"
    :error-message="deleteLoanError"
    @confirm="doDelete"
  />
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ArrowDownLeft, ArrowUpRight, Check, X, History } from 'lucide-vue-next'
import BaseModal from '../ui/BaseModal.vue'
import CurrencyInput from '../ui/CurrencyInput.vue'
import ConfirmModal from '../ui/ConfirmModal.vue'
import { useDebtsStore } from '../../stores/debts.js'

const store = useDebtsStore()

const open = computed({
  get: () => store.loanModalOpen,
  set: (v) => { if (!v) store.closeLoanModal() },
})

const editingLoan = computed(() => store.editingLoan)

// ── Mode ───────────────────────────────────────────────────────────────────────
const isEditing = ref(false)

const modalTitle = computed(() => {
  if (isEditing.value && !editingLoan.value) return 'Novo Empréstimo'
  if (isEditing.value && editingLoan.value) return 'Editar'
  return 'Empréstimo'
})

watch(open, (v) => {
  if (v) {
    isEditing.value = !editingLoan.value // create mode if no loan selected
    if (!editingLoan.value) resetForm()
    else loadPayments()
  } else {
    isEditing.value = false
    showPaymentForm.value = false
    payments.value = []
    paymentForm.value = { amount: 0, notes: '' }
  }
})

// ── Form ───────────────────────────────────────────────────────────────────────
const form = ref({
  direction: 'me_deve',
  name: '',
  amount: 0,
  interest_rate: 0,
  loan_date: todayStr(),
  due_date: '',
})

function resetForm() {
  form.value = {
    direction: 'me_deve',
    name: '',
    amount: 0,
    interest_rate: 0,
    loan_date: todayStr(),
    due_date: '',
  }
}

function startEdit() {
  if (editingLoan.value) {
    form.value = {
      direction: editingLoan.value.direction,
      name: editingLoan.value.name,
      amount: parseFloat(editingLoan.value.estimated_amount),
      interest_rate: parseFloat(editingLoan.value.interest_rate) || 0,
      loan_date: editingLoan.value.loan_date || todayStr(),
      due_date: editingLoan.value.due_date || '',
    }
  }
  isEditing.value = true
}

function cancelEdit() {
  if (editingLoan.value) {
    isEditing.value = false
  } else {
    store.closeLoanModal()
  }
}

const actionError = ref('')

async function save() {
  if (!form.value.name.trim() || !form.value.amount) return
  actionError.value = ''
  const payload = {
    name: form.value.name.trim(),
    direction: form.value.direction,
    estimated_amount: form.value.amount,
    interest_rate: form.value.direction === 'eu_devo' ? (parseFloat(form.value.interest_rate) || 0) : 0,
    loan_date: form.value.loan_date || null,
    due_date: form.value.due_date || null,
  }
  try {
    if (editingLoan.value) {
      await store.updateDebt(editingLoan.value.id, payload)
      // refresh the editingLoan ref in the store
      const updated = store.debts.find((d) => d.id === editingLoan.value.id)
      if (updated) store.editingLoan = updated
      isEditing.value = false
    } else {
      await store.createDebt(payload)
      store.closeLoanModal()
    }
  } catch {
    actionError.value = 'Não foi possível salvar. Tente novamente.'
  }
}

// ── Payments ───────────────────────────────────────────────────────────────────
const payments = ref([])
const loadingPayments = ref(false)
const showPaymentForm = ref(false)
const paymentForm = ref({ amount: 0, notes: '' })

async function loadPayments() {
  if (!editingLoan.value) return
  loadingPayments.value = true
  try {
    payments.value = await store.fetchPayments(editingLoan.value.id)
  } finally {
    loadingPayments.value = false
  }
}

async function submitPayment() {
  if (!paymentForm.value.amount || !editingLoan.value) return
  actionError.value = ''
  try {
    const pmt = await store.addPayment(editingLoan.value.id, {
      amount: paymentForm.value.amount,
      notes: paymentForm.value.notes || null,
    })
    payments.value.unshift(pmt)
    paymentForm.value = { amount: 0, notes: '' }
    showPaymentForm.value = false
    // update the local editingLoan reference
    const updated = store.debts.find((d) => d.id === editingLoan.value.id)
    if (updated) store.editingLoan = updated
  } catch {
    actionError.value = 'Não foi possível registrar o pagamento. Tente novamente.'
  }
}

// ── Settle / Delete ────────────────────────────────────────────────────────────
const showSettleConfirm = ref(false)
const showDeleteConfirm = ref(false)
const settling = ref(false)
const deletingLoan = ref(false)
const settleError = ref('')
const deleteLoanError = ref('')

function confirmSettle() { settleError.value = ''; showSettleConfirm.value = true }
function confirmDelete() { deleteLoanError.value = ''; showDeleteConfirm.value = true }

async function doSettle() {
  if (!editingLoan.value) return
  settling.value = true
  settleError.value = ''
  try {
    await store.settleDebt(editingLoan.value.id)
    const updated = store.debts.find((d) => d.id === editingLoan.value.id)
    if (updated) store.editingLoan = updated
    showSettleConfirm.value = false
  } catch {
    settleError.value = 'Não foi possível quitar. Tente novamente.'
  } finally {
    settling.value = false
  }
}

async function confirmReopen() {
  if (!editingLoan.value) return
  actionError.value = ''
  try {
    await store.updateDebt(editingLoan.value.id, { status: 'ativo' })
    const updated = store.debts.find((d) => d.id === editingLoan.value.id)
    if (updated) store.editingLoan = updated
  } catch {
    actionError.value = 'Não foi possível reabrir. Tente novamente.'
  }
}

async function doDelete() {
  if (!editingLoan.value) return
  deletingLoan.value = true
  deleteLoanError.value = ''
  try {
    await store.deleteDebt(editingLoan.value.id)
    showDeleteConfirm.value = false
    store.closeLoanModal()
  } catch {
    deleteLoanError.value = 'Não foi possível excluir. Tente novamente.'
  } finally {
    deletingLoan.value = false
  }
}

// ── Computed helpers ───────────────────────────────────────────────────────────
const hasPartialPayment = computed(() => {
  if (!editingLoan.value?.original_amount) return false
  return parseFloat(editingLoan.value.original_amount) > parseFloat(editingLoan.value.estimated_amount)
})

const paidAmount = computed(() => {
  if (!editingLoan.value) return 0
  return parseFloat(editingLoan.value.original_amount || 0) - parseFloat(editingLoan.value.estimated_amount || 0)
})

const progressPct = computed(() => {
  if (!editingLoan.value?.original_amount) return 0
  const orig = parseFloat(editingLoan.value.original_amount)
  if (!orig) return 0
  return Math.min(100, Math.round((paidAmount.value / orig) * 100))
})

const isOverdue = computed(() => {
  if (!editingLoan.value?.due_date || editingLoan.value.status === 'quitado') return false
  return new Date(editingLoan.value.due_date) < new Date()
})

// ── Utils ──────────────────────────────────────────────────────────────────────
function todayStr() {
  return new Date().toISOString().slice(0, 10)
}

const fmt = (n) =>
  (parseFloat(n) || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })

const fmtRate = (r) =>
  (parseFloat(r) || 0).toLocaleString('pt-BR', { maximumFractionDigits: 2 })

function fmtDate(d) {
  if (!d) return ''
  return new Date(d + 'T12:00:00').toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })
}

function fmtDatetime(d) {
  if (!d) return ''
  return new Date(d).toLocaleString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.form-slide-enter-active { animation: form-in 0.2s ease-out forwards; }
.form-slide-leave-active { animation: form-in 0.15s ease-in reverse forwards; }
@keyframes form-in {
  from { opacity: 0; transform: translateY(-6px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>

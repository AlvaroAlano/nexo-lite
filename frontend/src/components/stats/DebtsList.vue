<template>
  <div class="font-ss01 space-y-4">

    <!-- Loading -->
    <div v-if="store.loading" class="flex justify-center py-8">
      <div class="w-5 h-5 rounded-full border-2 border-brand-hairline-light dark:border-brand-hairline-dark border-t-brand-primary animate-spin" />
    </div>

    <template v-else>
      <!-- Cabeçalho: referência caixinha + total dívidas -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full px-2.5 py-1">
          <PiggyBank :size="11" class="text-emerald-500 flex-shrink-0" />
          <span class="text-[11px] font-medium text-emerald-600 dark:text-emerald-400">
            Caixinha: {{ fmt(vaultBalance) }}
          </span>
        </div>
        <span class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark">
          Total: <span class="font-tabular font-medium text-brand-ink-light dark:text-white">{{ fmt(totalDebt) }}</span>
        </span>
      </div>

      <!-- Empty state -->
      <div v-if="!store.debts.length" class="flex flex-col items-center gap-2 py-6 text-center">
        <Wallet :size="28" class="text-brand-ink-mute-light dark:text-brand-ink-mute-dark opacity-40" />
        <p class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark">
          Nenhuma dívida cadastrada.<br>Use "+ Nova dívida" para começar.
        </p>
      </div>

      <template v-else>
        <!-- ══ FOCO: dívida mais próxima de quitar ══════════════════════════════ -->
        <div
          class="rounded-xl p-3.5 border transition-colors"
          :class="focusedCovered
            ? 'border-emerald-500/30 bg-emerald-500/5 dark:bg-emerald-500/10'
            : 'border-brand-primary/20 dark:border-brand-primary/30 bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark/60'"
        >
          <!-- Badge + actions -->
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-1.5">
              <span
                class="flex items-center gap-1 text-[10px] font-semibold rounded-full px-2 py-0.5 border"
                :class="focusedCovered
                  ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400'
                  : 'bg-brand-primary/10 border-brand-primary/20 text-brand-primary dark:text-brand-primary-soft'"
              >
                <Target :size="9" />
                {{ focusedCovered ? 'Pronto para quitar' : 'Foco' }}
              </span>
              <span
                class="text-[9px] font-semibold rounded-full px-1.5 py-0.5 border"
                :class="focusedDebt.direction === 'me_deve'
                  ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400'
                  : 'bg-red-500/10 border-red-400/20 text-red-500 dark:text-red-400'"
              >
                {{ focusedDebt.direction === 'me_deve' ? 'Me deve' : 'Eu devo' }}
              </span>
            </div>

            <div class="flex items-center gap-1.5">
              <!-- Valor editável -->
              <template v-if="editing !== focusedDebt.id">
                <button
                  @click="startEdit(focusedDebt)"
                  class="text-sm font-tabular font-medium text-brand-ink-light dark:text-white hover:text-brand-primary dark:hover:text-brand-primary transition-colors"
                  title="Clique para atualizar"
                >
                  {{ fmt(focusedDebt.estimated_amount) }}
                </button>
              </template>
              <template v-else>
                <CurrencyInput
                  ref="editInputRef"
                  v-model="editAmount"
                  hide-prefix
                  @confirm="saveEdit(focusedDebt)"
                  @cancel="cancelEdit"
                  @blur="saveEdit(focusedDebt)"
                  input-class="w-24 text-right text-sm py-0.5 px-1 bg-white dark:bg-brand-canvas-dark border border-brand-primary/40 rounded-lg font-tabular font-medium text-brand-ink-light dark:text-white"
                />
              </template>

              <!-- Desktop: lixeira direta -->
              <button
                @click="confirmDelete(focusedDebt)"
                class="hidden md:flex text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:text-red-500 dark:hover:text-red-400 transition-colors"
              >
                <Trash2 :size="13" />
              </button>
              <!-- Mobile: three dots -->
              <div class="md:hidden relative">
                <button
                  @click.stop="toggleMenu(focusedDebt.id)"
                  class="w-6 h-6 flex items-center justify-center rounded-md text-brand-ink-mute-light dark:text-brand-ink-mute-dark active:bg-black/5 dark:active:bg-white/10 transition-colors"
                >
                  <MoreVertical :size="15" />
                </button>
                <Transition name="dropdown">
                  <div
                    v-if="openMenuId === focusedDebt.id"
                    class="absolute right-0 top-7 z-30 min-w-[150px] rounded-xl bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark shadow-stripe-2 py-1 overflow-hidden"
                  >
                    <button
                      @click.stop="confirmDelete(focusedDebt); openMenuId = null"
                      class="w-full flex items-center gap-2.5 px-3.5 py-2.5 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors"
                    >
                      <Trash2 :size="14" class="flex-shrink-0" />
                      Excluir
                    </button>
                  </div>
                </Transition>
              </div>
            </div>
          </div>

          <!-- Nome + clique para detalhe -->
          <button
            @click="debtsStore.openLoanModal(focusedDebt)"
            class="text-left w-full mb-2"
          >
            <p class="text-base font-semibold text-brand-ink-light dark:text-white truncate hover:text-brand-primary dark:hover:text-brand-primary-soft transition-colors">
              {{ focusedDebt.name }}
            </p>
            <p v-if="focusedDebt.due_date" class="text-[10px] mt-0.5" :class="isOverdue(focusedDebt) ? 'text-red-500 dark:text-red-400' : 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark'">
              Prazo: {{ fmtDate(focusedDebt.due_date) }}{{ isOverdue(focusedDebt) ? ' · Em atraso' : '' }}
            </p>
          </button>

          <!-- Barra de progresso -->
          <div class="h-2 w-full bg-slate-100 dark:bg-zinc-800 rounded-full overflow-hidden mb-1.5">
            <div
              class="h-full rounded-full transition-all duration-700"
              :class="focusedCovered ? 'bg-emerald-500' : 'bg-brand-primary/70'"
              :style="{ width: Math.min(coveragePct(focusedDebt), 100) + '%' }"
            />
          </div>

          <!-- Mensagem contextual -->
          <div class="flex items-center justify-between">
            <p class="text-[11px]" :class="focusedCovered ? 'text-emerald-500 font-medium' : 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark'">
              <template v-if="focusedCovered">
                Caixinha cobre essa dívida! Hora de quitar.
              </template>
              <template v-else>
                Faltam <span class="font-tabular">{{ fmt(focusedDebt.estimated_amount - vaultBalance) }}</span> para cobrir
              </template>
            </p>
            <span class="text-[10px] font-tabular text-brand-ink-mute-light dark:text-brand-ink-mute-dark">
              {{ coveragePct(focusedDebt) }}%
            </span>
          </div>
        </div>

        <!-- ══ Demais dívidas (compacto, sem mensagem) ═══════════════════════════ -->
        <div v-if="otherDebts.length" class="space-y-2.5">
          <div
            v-for="debt in otherDebts"
            :key="debt.id"
            class="group"
          >
            <div class="flex items-center gap-2 mb-1">
              <button @click="debtsStore.openLoanModal(debt)" class="flex items-center gap-1.5 flex-1 min-w-0 text-left">
                <span class="text-sm text-brand-ink-light dark:text-white truncate hover:text-brand-primary dark:hover:text-brand-primary-soft transition-colors">{{ debt.name }}</span>
                <span
                  class="text-[8px] font-semibold rounded-full px-1.5 py-0.5 border flex-shrink-0"
                  :class="debt.direction === 'me_deve'
                    ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400'
                    : 'bg-red-500/10 border-red-400/20 text-red-500 dark:text-red-400'"
                >
                  {{ debt.direction === 'me_deve' ? 'Me deve' : 'Eu devo' }}
                </span>
              </button>
              <span class="text-[10px] font-tabular text-brand-ink-mute-light dark:text-brand-ink-mute-dark flex-shrink-0 w-8 text-right">
                {{ coveragePct(debt) }}%
              </span>
              <div class="flex-shrink-0 w-24 text-right">
                <template v-if="editing !== debt.id">
                  <button
                    @click="startEdit(debt)"
                    class="text-sm font-tabular text-brand-ink-light dark:text-white hover:text-brand-primary dark:hover:text-brand-primary transition-colors"
                  >{{ fmt(debt.estimated_amount) }}</button>
                </template>
                <template v-else>
                  <CurrencyInput
                    ref="editInputRef"
                    v-model="editAmount"
                    hide-prefix
                    @confirm="saveEdit(debt)"
                    @cancel="cancelEdit"
                    @blur="saveEdit(debt)"
                    input-class="w-full text-right text-sm py-0.5 px-1 bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark border border-brand-primary/40 rounded-lg"
                  />
                </template>
              </div>
              <!-- Desktop: hover icons -->
              <button
                @click="setFocus(debt)"
                class="hidden md:flex flex-shrink-0 opacity-0 group-hover:opacity-100 focus:opacity-100 transition-opacity text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:text-brand-primary dark:hover:text-brand-primary"
                title="Definir como foco"
              >
                <Target :size="13" />
              </button>
              <button
                @click="confirmDelete(debt)"
                class="hidden md:flex flex-shrink-0 opacity-0 group-hover:opacity-100 focus:opacity-100 transition-opacity text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:text-red-500 dark:hover:text-red-400"
              >
                <Trash2 :size="13" />
              </button>
              <!-- Mobile: three dots -->
              <div class="md:hidden flex-shrink-0 relative">
                <button
                  @click.stop="toggleMenu(debt.id)"
                  class="w-6 h-6 flex items-center justify-center rounded-md text-brand-ink-mute-light dark:text-brand-ink-mute-dark active:bg-black/5 dark:active:bg-white/10 transition-colors"
                >
                  <MoreVertical :size="15" />
                </button>
                <Transition name="dropdown">
                  <div
                    v-if="openMenuId === debt.id"
                    class="absolute right-0 bottom-7 z-30 min-w-[150px] rounded-xl bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark shadow-stripe-2 py-1 overflow-hidden"
                  >
                    <button
                      @click.stop="setFocus(debt); openMenuId = null"
                      class="w-full flex items-center gap-2.5 px-3.5 py-2.5 text-sm text-brand-primary hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-dark transition-colors"
                    >
                      <Target :size="14" class="flex-shrink-0" />
                      Definir foco
                    </button>
                    <div class="h-px bg-brand-hairline-light dark:bg-brand-hairline-dark" />
                    <button
                      @click.stop="confirmDelete(debt); openMenuId = null"
                      class="w-full flex items-center gap-2.5 px-3.5 py-2.5 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors"
                    >
                      <Trash2 :size="14" class="flex-shrink-0" />
                      Excluir
                    </button>
                  </div>
                </Transition>
              </div>
            </div>
            <div class="h-1.5 w-full bg-slate-100 dark:bg-zinc-800 rounded-full overflow-hidden">
              <div
                class="h-full bg-emerald-500/50 rounded-full transition-all duration-700"
                :style="{ width: Math.min(coveragePct(debt), 100) + '%' }"
              />
            </div>
          </div>
        </div>

        <!-- Resumo geral -->
        <div class="pt-3 border-t border-brand-hairline-light dark:border-brand-hairline-dark flex items-center justify-between">
          <span class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark">Cobertura geral</span>
          <div class="flex items-center gap-2">
            <div class="w-20 h-1.5 bg-slate-100 dark:bg-zinc-800 rounded-full overflow-hidden">
              <div
                class="h-full bg-emerald-500/70 rounded-full transition-all duration-700"
                :style="{ width: Math.min(overallCoverage, 100) + '%' }"
              />
            </div>
            <span class="text-xs font-tabular font-medium text-brand-ink-light dark:text-white">
              {{ overallCoverage.toFixed(1) }}%
            </span>
          </div>
        </div>
      </template>

      <!-- Adicionar novo empréstimo -->
      <button
        @click="debtsStore.openLoanModal()"
        class="w-full mt-1 py-2 rounded-xl border border-dashed border-brand-hairline-light dark:border-brand-hairline-dark text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:border-brand-primary hover:text-brand-primary dark:hover:text-white transition-colors"
      >
        + Novo empréstimo
      </button>
    </template>

    <!-- Backdrop fecha menus mobile -->
    <div v-if="openMenuId" class="fixed inset-0 z-20" @click="openMenuId = null" />

    <!-- Modal confirmar exclusão -->
    <ConfirmModal
      v-model="showConfirm"
      title="Remover dívida"
      :message="`Remover '${deleteTarget?.name}' da lista?`"
      confirm-label="Remover"
      @confirm="doDelete"
    />

  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { PiggyBank, Trash2, Check, X, Wallet, Target, MoreVertical } from 'lucide-vue-next'
import { useDebtsStore } from '../../stores/debts.js'
import { useVaultStore } from '../../stores/vault.js'
import CurrencyInput from '../ui/CurrencyInput.vue'
import ConfirmModal from '../ui/ConfirmModal.vue'
import { CLOSE_MENUS_EVENT, broadcastMenuOpen } from '../../utils/menuBus.js'

const store = useDebtsStore()
const debtsStore = store
const vault = useVaultStore()

onMounted(() => store.fetchDebts())

// ── Vault balance ─────────────────────────────────────────────────────────────
const vaultBalance = computed(() => {
  const s = vault.summary
  if (!s) return 0
  const real = s.last_real_balance != null ? parseFloat(s.last_real_balance) : null
  return real ?? parseFloat(s.total_deposited) ?? 0
})

// ── Menu mobile ──────────────────────────────────────────────────────────────
const openMenuId = ref(null)
function toggleMenu(id) {
  if (openMenuId.value === id) {
    openMenuId.value = null
  } else {
    broadcastMenuOpen()
    openMenuId.value = id
  }
}
function closeDebtsMenu() { openMenuId.value = null }
onMounted(() => document.addEventListener(CLOSE_MENUS_EVENT, closeDebtsMenu))
onUnmounted(() => document.removeEventListener(CLOSE_MENUS_EVENT, closeDebtsMenu))

// ── Foco manual — persiste no localStorage ────────────────────────────────────
const FOCUS_KEY = 'nexo_focused_debt_id'
const focusedDebtId = ref(localStorage.getItem(FOCUS_KEY) || null)

function setFocus(debt) {
  focusedDebtId.value = String(debt.id)
  localStorage.setItem(FOCUS_KEY, String(debt.id))
}

const focusedDebt = computed(() => {
  if (focusedDebtId.value) {
    const found = store.debts.find((d) => String(d.id) === focusedDebtId.value)
    if (found) return found
  }
  // fallback: menor dívida se nenhuma selecionada ou selecionada foi deletada
  return [...store.debts].sort((a, b) => parseFloat(a.estimated_amount) - parseFloat(b.estimated_amount))[0] ?? null
})
const otherDebts = computed(() =>
  store.debts
    .filter((d) => d.id !== focusedDebt.value?.id)
    .sort((a, b) => parseFloat(a.estimated_amount) - parseFloat(b.estimated_amount))
)
const focusedCovered = computed(() =>
  focusedDebt.value ? coveragePct(focusedDebt.value) >= 100 : false
)

// ── Totais ────────────────────────────────────────────────────────────────────
const totalDebt = computed(() =>
  store.debts.reduce((s, d) => s + parseFloat(d.estimated_amount), 0)
)
const overallCoverage = computed(() =>
  totalDebt.value > 0 ? (vaultBalance.value / totalDebt.value) * 100 : 0
)

const coveragePct = (debt) => {
  const amt = parseFloat(debt.estimated_amount)
  if (!amt) return 0
  return parseFloat(((vaultBalance.value / amt) * 100).toFixed(1))
}

// ── Edição inline ─────────────────────────────────────────────────────────────
const editing      = ref(null)
const editAmount   = ref(0)
const editInputRef = ref(null)

function startEdit(debt) {
  editing.value    = debt.id
  editAmount.value = parseFloat(debt.estimated_amount)
  nextTick(() => editInputRef.value?.focus())
}

async function saveEdit(debt) {
  if (editing.value !== debt.id) return
  editing.value = null
  await store.updateDebt(debt.id, editAmount.value)
}

function cancelEdit() {
  editing.value = null
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function isOverdue(debt) {
  if (!debt.due_date || debt.status === 'quitado') return false
  return new Date(debt.due_date) < new Date()
}

function fmtDate(d) {
  if (!d) return ''
  return new Date(d + 'T12:00:00').toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })
}

// ── Exclusão ──────────────────────────────────────────────────────────────────
const showConfirm  = ref(false)
const deleteTarget = ref(null)

function confirmDelete(debt) {
  deleteTarget.value = debt
  showConfirm.value  = true
}

async function doDelete() {
  await store.deleteDebt(deleteTarget.value?.id)
  deleteTarget.value = null
}

// ── Formatação ────────────────────────────────────────────────────────────────
const fmt = (n) =>
  (n ?? 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
</script>

<style scoped>
.form-slide-enter-active { animation: form-in 0.2s ease-out forwards; }
.form-slide-leave-active { animation: form-in 0.15s ease-in reverse forwards; }

@keyframes form-in {
  from { opacity: 0; transform: translateY(-6px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Dropdown menu */
.dropdown-enter-active {
  animation: dropdown-pop 0.14s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.dropdown-leave-active {
  animation: dropdown-pop 0.1s ease-in reverse forwards;
}

@keyframes dropdown-pop {
  from { opacity: 0; transform: scale(0.88) translateY(6px); }
  to   { opacity: 1; transform: scale(1)    translateY(0);   }
}
</style>

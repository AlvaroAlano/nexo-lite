<template>
  <div class="max-w-4xl mx-auto px-4 pt-5 pb-6 font-ss01">
    <div class="mb-6">
      <h1 class="text-xl font-light tracking-tight text-brand-ink-light dark:text-white">Recorrências</h1>
      <p class="text-sm text-brand-ink-mute-light dark:text-brand-ink-mute-dark mt-1">
        Despesas clonadas automaticamente em cada virada de mês.
      </p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="w-5 h-5 rounded-full border-2 border-brand-hairline-light dark:border-brand-hairline-dark border-t-brand-primary animate-spin" />
    </div>

    <template v-else>
      <ConfirmModal
        v-model="showConfirmDelete"
        title="Remover recorrência"
        :message="`Remover '${deleteTarget?.name}' das recorrências? As próximas viradas não vão mais clonar esta despesa.`"
        confirm-label="Remover"
        @confirm="doDelete"
      />

      <div class="md:grid md:grid-cols-[340px_1fr] md:gap-8 md:items-start">
        <!-- Left: form (desktop only) -->
        <div class="hidden md:block bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-stripe-card p-5 shadow-stripe-1">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-medium text-brand-ink-light dark:text-white text-sm">
              {{ editTarget ? 'Editar Recorrência' : 'Nova Recorrência' }}
            </h3>
            <button v-if="editTarget" @click="cancelEdit" class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:text-brand-ink-light dark:hover:text-white transition-colors">Cancelar</button>
          </div>
          <div class="space-y-3">
            <input
              v-model="form.name"
              placeholder="Nome (ex: Conta de Luz)"
              class="w-full px-4 py-2.5 md:py-2 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20 transition-colors"
            />
            <CategoryPicker v-model="form.category_id" />
            <AppSelect v-model="form.responsavel" :options="responsavelOpts" />
            <AppSelect v-model="form.expense_type" :options="expenseTypeOpts" />
            <div>
              <label class="block text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-1">
                {{ form.expense_type === 'installment' ? 'Valor da parcela' : 'Valor mensal (base)' }}
              </label>
              <CurrencyInput
                v-model="form.base_amount"
                input-class="w-full pr-4 py-2.5 md:py-2 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20 transition-colors"
              />
            </div>

            <!-- Installment fields -->
            <template v-if="form.expense_type === 'installment'">
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-1">Parcelas já pagas</label>
                  <input
                    v-model.number="form.installment_paid"
                    type="number"
                    min="0"
                    :max="form.installment_total || 999"
                    placeholder="0"
                    class="w-full px-4 py-2.5 md:py-2 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20 transition-colors"
                  />
                </div>
                <div>
                  <label class="block text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-1">Total de parcelas</label>
                  <input
                    v-model.number="form.installment_total"
                    type="number"
                    min="1"
                    placeholder="Ex: 10"
                    class="w-full px-4 py-2.5 md:py-2 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20 transition-colors"
                  />
                </div>
              </div>

              <!-- Installment summary card -->
              <div v-if="installmentSummary" class="bg-brand-canvas-soft-light dark:bg-brand-canvas-dark/40 border border-brand-hairline-light dark:border-brand-hairline-dark/60 rounded-xl p-3 text-xs space-y-1 text-brand-ink-mute-light dark:text-brand-ink-mute-dark">
                <p class="font-medium text-brand-ink-light dark:text-white">Resumo do Parcelamento:</p>
                <p>{{ installmentSummary.totalText }}</p>
                <p>{{ installmentSummary.paidText }}</p>
                <p>{{ installmentSummary.remainingText }}</p>
              </div>

              <p v-if="installmentError" class="text-red-500 text-xs">{{ installmentError }}</p>
            </template>

            <!-- Add to current month — hidden when editing -->
            <label v-if="dashboardStore.period && !editTarget" @click="form.addToCurrentMonth = !form.addToCurrentMonth" class="flex items-center gap-3 py-2 cursor-pointer select-none">
              <div
                class="w-5 h-5 rounded border flex items-center justify-center transition-colors flex-shrink-0 pointer-events-none"
                :class="form.addToCurrentMonth ? 'bg-brand-primary border-brand-primary' : 'border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark'"
              >
                <svg v-if="form.addToCurrentMonth" class="w-3 h-3 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </div>
              <span class="text-sm text-brand-ink-light dark:text-white font-medium">Adicionar ao mês atual</span>
            </label>

            <button
              @click="addTemplate"
              :disabled="!form.name.trim() || saving || !!installmentError"
              class="w-full py-2.5 md:py-2 rounded-full bg-brand-primary text-white text-sm font-medium hover:bg-brand-primary-hover disabled:opacity-40 active:scale-[.98] transition-all"
            >
              {{ saving ? 'Salvando…' : (editTarget ? 'Salvar' : 'Adicionar') }}
            </button>
          </div>
        </div>

        <!-- Right: list -->
        <div class="space-y-2">
          <div
            v-for="tmpl in templates"
            :key="tmpl.id"
            class="bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-stripe-card px-4 py-3 flex items-center gap-3 shadow-stripe-1 transition-all duration-150"
            :class="!tmpl.is_active ? 'opacity-40' : ''"
          >
            <!-- Info -->
            <div class="flex-1 min-w-0 space-y-1">
              <p class="font-medium text-brand-ink-light dark:text-white text-sm truncate">{{ tmpl.name }}</p>
              <div class="flex items-center gap-1.5 flex-wrap">
                <span class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark">{{ tmpl.category }}</span>
                <span
                  class="text-[9px] font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded-full flex-shrink-0"
                  :class="typeBadge(tmpl.expense_type)"
                >
                  {{ typeLabel(tmpl.expense_type) }}
                </span>
              </div>
            </div>

            <!-- Amount + installment -->
            <div class="text-right flex-shrink-0">
              <p class="font-tabular font-medium text-brand-ink-light dark:text-white text-sm">
                {{ formatCurrency(tmpl.base_amount) }}
              </p>
              <template v-if="tmpl.expense_type === 'installment'">
                <p class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark font-tabular">
                  {{ tmpl.installment_paid }}/{{ tmpl.installment_total }} pagas
                </p>
                <p class="text-[10px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark/60 font-tabular mt-0.5">
                  Total: {{ formatCurrency(tmpl.base_amount * tmpl.installment_total) }}
                </p>
              </template>
            </div>

            <!-- Actions -->
            <div class="flex gap-1 flex-shrink-0">
              <button
                @click="startEdit(tmpl)"
                class="w-8 h-8 flex items-center justify-center rounded-lg text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark/30 hover:text-brand-ink-light dark:hover:text-white transition-colors"
                title="Editar"
              >
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
              </button>
              <button
                @click="toggleActive(tmpl)"
                class="w-8 h-8 flex items-center justify-center rounded-lg text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark/30 hover:text-brand-ink-light dark:hover:text-white transition-colors"
                :title="tmpl.is_active ? 'Desativar' : 'Ativar'"
              >
                <svg v-if="tmpl.is_active" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94"/>
                  <path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
                <svg v-else class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </button>
              <button
                @click="confirmDelete(tmpl)"
                class="w-8 h-8 flex items-center justify-center rounded-lg text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:bg-red-500/10 hover:text-red-500 transition-colors"
              >
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>
                  <path d="M10 11v6"/><path d="M14 11v6"/>
                  <path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/>
                </svg>
              </button>
            </div>
          </div>

          <div v-if="!templates.length" class="text-center py-12 text-brand-ink-mute-light dark:text-brand-ink-mute-dark text-sm">
            Nenhuma recorrência configurada ainda.
          </div>
        </div>
      </div>

      <!-- Mobile: Nova Recorrência sheet -->
      <BaseModal
        v-model="dashboardStore.quickAddTemplateOpen"
        :title="editTarget ? 'Editar Recorrência' : 'Nova Recorrência'"
        :full-screen-on-mobile="true"
      >
        <div class="space-y-3">
          <input
            v-model="form.name"
            placeholder="Nome (ex: Conta de Luz)"
            class="w-full px-4 py-3 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20 transition-colors"
          />
          <CategoryPicker v-model="form.category_id" />
          <AppSelect v-model="form.responsavel" :options="responsavelOpts" />
          <AppSelect v-model="form.expense_type" :options="expenseTypeOpts" />
          <div>
            <label class="block text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-1">
              {{ form.expense_type === 'installment' ? 'Valor da parcela' : 'Valor mensal (base)' }}
            </label>
            <CurrencyInput
              v-model="form.base_amount"
              input-class="w-full pr-4 py-3 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20 transition-colors"
            />
          </div>
          <template v-if="form.expense_type === 'installment'">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-1">Parcelas já pagas</label>
                <input v-model.number="form.installment_paid" type="number" min="0" :max="form.installment_total || 999" placeholder="0"
                  class="w-full px-4 py-3 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20 transition-colors" />
              </div>
              <div>
                <label class="block text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-1">Total de parcelas</label>
                <input v-model.number="form.installment_total" type="number" min="1" placeholder="Ex: 10"
                  class="w-full px-4 py-3 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20 transition-colors" />
              </div>
            </div>

            <!-- Installment summary card -->
            <div v-if="installmentSummary" class="bg-brand-canvas-soft-light dark:bg-brand-canvas-dark/40 border border-brand-hairline-light dark:border-brand-hairline-dark/60 rounded-xl p-3 text-xs space-y-1 text-brand-ink-mute-light dark:text-brand-ink-mute-dark">
              <p class="font-medium text-brand-ink-light dark:text-white">Resumo do Parcelamento:</p>
              <p>{{ installmentSummary.paidText }}</p>
              <p>{{ installmentSummary.remainingText }}</p>
            </div>

            <p v-if="installmentError" class="text-red-500 text-xs">{{ installmentError }}</p>
          </template>
          <label v-if="dashboardStore.period && !editTarget" @click="form.addToCurrentMonth = !form.addToCurrentMonth" class="flex items-center gap-3 py-2 cursor-pointer select-none">
            <div
              class="w-5 h-5 rounded border flex items-center justify-center transition-colors flex-shrink-0 pointer-events-none"
              :class="form.addToCurrentMonth ? 'bg-brand-primary border-brand-primary' : 'border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark'"
            >
              <svg v-if="form.addToCurrentMonth" class="w-3 h-3 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            </div>
            <span class="text-sm text-brand-ink-light dark:text-white font-medium">Adicionar ao mês atual</span>
          </label>
        </div>
        <template #footer>
          <button
            @click="addTemplateAndClose"
            :disabled="!form.name.trim() || saving || !!installmentError"
            class="w-full py-3 rounded-full bg-brand-primary text-white text-sm font-medium hover:bg-brand-primary-hover disabled:opacity-40 active:scale-[.98] transition-all"
          >
            {{ saving ? 'Salvando…' : (editTarget ? 'Salvar alterações' : 'Adicionar recorrência') }}
          </button>
        </template>
      </BaseModal>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { templatesApi } from '../services/api.js'
import { formatCurrency } from '../utils/currency.js'
import CategoryPicker from '../components/ui/CategoryPicker.vue'
import CurrencyInput from '../components/ui/CurrencyInput.vue'
import AppSelect from '../components/ui/AppSelect.vue'
import ConfirmModal from '../components/ui/ConfirmModal.vue'
import BaseModal from '../components/ui/BaseModal.vue'
import { useDashboardStore } from '../stores/dashboard.js'

const dashboardStore = useDashboardStore()
const templates = ref([])

const responsavelOpts = computed(() => [
  { value: 'conjunto',  label: 'Casal (Conjunto)' },
  { value: 'alvaro',    label: dashboardStore.nameAlvaro },
  { value: 'alexandra', label: dashboardStore.nameAlexandra },
])
const expenseTypeOpts = [
  { value: 'fixed',       label: 'Fixa' },
  { value: 'variable',    label: 'Variável' },
  { value: 'installment', label: 'Parcelada' },
  { value: 'rent',        label: 'Aluguel' },
]
const loading = ref(false)
const saving = ref(false)
const editTarget = ref(null)

watch(() => dashboardStore.quickAddTemplateOpen, (val) => {
  if (!val) {
    form.value = emptyForm()
    editTarget.value = null
  }
})

const emptyForm = () => ({
  name: '',
  category_id: null,
  expense_type: 'fixed',
  responsavel: 'conjunto',
  base_amount: 0,
  installment_paid: 0,
  installment_total: null,
  addToCurrentMonth: false,
})

const form = ref(emptyForm())

const installmentError = computed(() => {
  if (form.value.expense_type !== 'installment') return ''
  const paid = form.value.installment_paid ?? 0
  const total = form.value.installment_total ?? 0
  if (total < 1) return 'Informe o total de parcelas.'
  if (paid > total) return `Parcelas pagas (${paid}) não podem exceder o total (${total}).`
  return ''
})

const installmentSummary = computed(() => {
  if (form.value.expense_type !== 'installment') return null
  const totalAmount = form.value.base_amount || 0
  const totalInstallments = form.value.installment_total || 0
  const paidInstallments = form.value.installment_paid || 0

  if (totalInstallments <= 0) return null

  const valuePerInstallment = totalAmount
  const remainingInstallments = Math.max(0, totalInstallments - paidInstallments)
  const amountPaid = paidInstallments * valuePerInstallment
  const amountRemaining = remainingInstallments * valuePerInstallment
  const totalValue = totalInstallments * valuePerInstallment

  return {
    valuePerInstallment,
    remainingInstallments,
    amountPaid,
    amountRemaining,
    totalText: `Total da compra: ${formatCurrency(totalValue)} (${totalInstallments}× de ${formatCurrency(valuePerInstallment)})`,
    paidText: paidInstallments > 0
      ? `Você já pagou ${paidInstallments} parcela(s) de ${formatCurrency(valuePerInstallment)} (${formatCurrency(amountPaid)} pago).`
      : 'Nenhuma parcela paga ainda.',
    remainingText: remainingInstallments > 0
      ? `Falta(m) ${remainingInstallments} parcela(s) de ${formatCurrency(valuePerInstallment)} (${formatCurrency(amountRemaining)} restante).`
      : 'Parcelamento totalmente quitado!'
  }
})

onMounted(fetchTemplates)

async function fetchTemplates() {
  loading.value = true
  try {
    const { data } = await templatesApi.list()
    templates.value = data
  } finally {
    loading.value = false
  }
}

function startEdit(tmpl) {
  form.value = {
    name: tmpl.name,
    category_id: tmpl.category_id,
    expense_type: tmpl.expense_type,
    responsavel: tmpl.responsavel,
    base_amount: tmpl.base_amount,
    installment_paid: tmpl.installment_paid ?? 0,
    installment_total: tmpl.installment_total ?? null,
    addToCurrentMonth: false,
  }
  editTarget.value = tmpl
  if (window.innerWidth < 768) {
    dashboardStore.quickAddTemplateOpen = true
  }
}

function cancelEdit() {
  editTarget.value = null
  form.value = emptyForm()
}

async function updateTemplate() {
  if (!editTarget.value || installmentError.value) return
  saving.value = true
  try {
    const isInstallment = form.value.expense_type === 'installment'
    const payload = {
      name: form.value.name.trim(),
      category_id: form.value.category_id,
      expense_type: form.value.expense_type,
      responsavel: form.value.responsavel,
      base_amount: form.value.base_amount,
      installment_total: isInstallment ? (form.value.installment_total ?? null) : null,
      installment_paid: isInstallment ? (form.value.installment_paid ?? 0) : 0,
    }
    const { data } = await templatesApi.update(editTarget.value.id, payload)
    const idx = templates.value.findIndex(t => t.id === editTarget.value.id)
    if (idx !== -1) templates.value[idx] = data
    editTarget.value = null
    form.value = emptyForm()
  } finally {
    saving.value = false
  }
}

async function addTemplate() {
  if (editTarget.value) { await updateTemplate(); return }
  if (installmentError.value) return
  saving.value = true
  try {
    const isInstallment = form.value.expense_type === 'installment'
    const payload = {
      name: form.value.name.trim(),
      category_id: form.value.category_id,
      expense_type: form.value.expense_type,
      responsavel: form.value.responsavel,
      base_amount: form.value.base_amount,
      installment_total: isInstallment ? (form.value.installment_total || null) : null,
    }
    const { data: tmpl } = await templatesApi.create(payload)

    // Update paid counter on the template after creation
    if (isInstallment && form.value.installment_paid > 0) {
      await templatesApi.update(tmpl.id, { installment_paid: form.value.installment_paid })
      tmpl.installment_paid = form.value.installment_paid
    }

    templates.value.push(tmpl)

    // Optionally add to current open month
    if (form.value.addToCurrentMonth && dashboardStore.period?.id) {
      const current = form.value.installment_paid + 1
      await dashboardStore.addExpense({
        name: tmpl.name,
        category_id: tmpl.category_id,
        expense_type: tmpl.expense_type,
        responsavel: tmpl.responsavel,
        amount: tmpl.base_amount,
        ...(isInstallment && {
          installment_current: current,
          installment_total: tmpl.installment_total,
        }),
      })
    }

    form.value = emptyForm()
  } finally {
    saving.value = false
  }
}

async function addTemplateAndClose() {
  await addTemplate()
  dashboardStore.quickAddTemplateOpen = false
}

async function toggleActive(tmpl) {
  const { data } = await templatesApi.update(tmpl.id, { is_active: !tmpl.is_active })
  const idx = templates.value.findIndex((t) => t.id === tmpl.id)
  if (idx !== -1) templates.value[idx] = data
}

const showConfirmDelete = ref(false)
const deleteTarget = ref(null)

function confirmDelete(tmpl) {
  deleteTarget.value = tmpl
  showConfirmDelete.value = true
}

async function doDelete() {
  if (!deleteTarget.value) return
  await templatesApi.delete(deleteTarget.value.id)
  templates.value = templates.value.filter((t) => t.id !== deleteTarget.value.id)
  deleteTarget.value = null
  showConfirmDelete.value = false
}

function typeLabel(t) {
  return { fixed: 'Fixa', variable: 'Variável', installment: 'Parcela', rent: 'Aluguel' }[t] || t
}

function typeBadge(t) {
  return {
    fixed: 'bg-brand-canvas-soft-light text-brand-ink-mute-light dark:bg-brand-canvas-dark dark:text-brand-ink-mute-dark',
    variable: 'bg-amber-50 text-amber-600 dark:bg-amber-950/40 dark:text-amber-300',
    installment: 'bg-blue-50 text-blue-600 dark:bg-blue-950/40 dark:text-blue-300',
    rent: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
  }[t] || 'bg-brand-canvas-soft-light text-brand-ink-mute-light dark:bg-brand-canvas-dark dark:text-brand-ink-mute-dark'
}
</script>

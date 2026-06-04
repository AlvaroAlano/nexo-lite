<template>
  <div class="font-ss01">

    <!-- Loading -->
    <div v-if="vault.loading" class="flex justify-center py-8">
      <div class="w-5 h-5 rounded-full border-2 border-brand-hairline-light dark:border-brand-hairline-dark border-t-brand-primary animate-spin" />
    </div>

    <template v-else>
      <!-- 3 indicadores -->
      <div class="grid grid-cols-3 gap-3 mb-5">
        <div>
          <p class="text-[10px] font-semibold text-brand-ink-mute-light dark:text-brand-ink-mute-dark uppercase tracking-wider mb-1">Aportado</p>
          <p class="text-lg font-semibold font-tabular text-brand-ink-light dark:text-white leading-tight">
            {{ fmt(vault.summary?.total_deposited) }}
          </p>
        </div>
        <div>
          <p class="text-[10px] font-semibold text-brand-ink-mute-light dark:text-brand-ink-mute-dark uppercase tracking-wider mb-1">Rendimento</p>
          <p
            class="text-lg font-semibold font-tabular leading-tight"
            :class="yieldValue === null
              ? 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark'
              : yieldValue >= 0 ? 'text-emerald-500' : 'text-red-500'"
          >
            {{ yieldValue === null ? '—' : fmt(yieldValue) }}
          </p>
        </div>
        <div>
          <p class="text-[10px] font-semibold text-brand-ink-mute-light dark:text-brand-ink-mute-dark uppercase tracking-wider mb-1">Saldo Real</p>
          <p
            class="text-lg font-semibold font-tabular leading-tight"
            :class="vault.summary?.last_real_balance != null
              ? 'text-brand-ink-light dark:text-white'
              : 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark'"
          >
            {{ vault.summary?.last_real_balance != null ? fmt(vault.summary.last_real_balance) : '—' }}
          </p>
          <p v-if="vault.summary?.last_reconciled_at" class="text-[10px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark mt-0.5">
            {{ fmtDate(vault.summary.last_reconciled_at) }}
          </p>
        </div>
      </div>

      <!-- Gráfico -->
      <VaultBarChart :data="chartHistory" />

      <!-- Botão reconciliação -->
      <div class="mt-4 flex justify-end">
        <button
          @click="showModal = true"
          class="flex items-center gap-1.5 text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:text-brand-ink-light dark:hover:text-white border border-brand-hairline-light dark:border-brand-hairline-dark rounded-full px-3 py-1.5 transition-colors"
        >
          <RefreshCw :size="11" />
          Atualizar saldo real
        </button>
      </div>
    </template>

    <!-- Modal reconciliação -->
    <BaseModal v-model="showModal" title="Saldo Real da Caixinha">
      <div class="space-y-4">
        <p class="text-sm text-brand-ink-mute-light dark:text-brand-ink-mute-dark">
          Abra o app do banco e informe o saldo atual da sua conta de reserva.
        </p>
        <CurrencyInput
          v-model="inputBalance"
          input-class="w-full pr-4 py-3 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input font-tabular text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
        />
      </div>
      <template #footer>
        <button
          @click="save"
          :disabled="!inputBalance || vault.saving"
          class="w-full py-3 rounded-full bg-brand-primary text-white text-sm font-medium hover:bg-brand-primary-hover disabled:opacity-40 active:scale-[.98] transition-all"
        >
          {{ vault.saving ? 'Salvando…' : 'Salvar' }}
        </button>
      </template>
    </BaseModal>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RefreshCw } from 'lucide-vue-next'
import { useVaultStore } from '../../stores/vault.js'
import VaultBarChart from './VaultBarChart.vue'
import BaseModal from '../ui/BaseModal.vue'
import CurrencyInput from '../ui/CurrencyInput.vue'

const vault = useVaultStore()

const showModal    = ref(false)
const inputBalance = ref(0)

onMounted(() => vault.fetchSummary())

const yieldValue = computed(() => {
  const s = vault.summary
  if (!s || s.calculated_yield == null) return null
  return parseFloat(s.calculated_yield)
})

// Últimos 12 meses
const chartHistory = computed(() => (vault.summary?.history ?? []).slice(-12))

async function save() {
  await vault.reconcile(inputBalance.value)
  showModal.value = false
  inputBalance.value = 0
}

const fmt = (n) => (n == null ? '—' : parseFloat(n).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }))

const fmtDate = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' })
}
</script>

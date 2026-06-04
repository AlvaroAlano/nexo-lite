<template>
  <div class="max-w-5xl mx-auto px-4 pt-5 pb-6 font-ss01">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-5 items-start">

      <!-- 1: Radar de Comprometimento -->
      <StatCard title="Radar de Comprometimento" subtitle="Custo total previsto nos próximos 6 meses">
        <FutureRadarChart :data="futureMonthsData" />
      </StatCard>

      <!-- 2: Evolução do Saldo Livre -->
      <StatCard title="Evolução do Saldo Livre" subtitle="Free Cash e Carryover — últimos 6 meses">
        <FreeCashChart :data="freeCashData" />
      </StatCard>

      <!-- 3: Termômetro de Liquidez -->
      <StatCard title="Termômetro de Liquidez" subtitle="Proporção do orçamento comprometida em fixos">
        <LiquidityDonut :data="liquidityData" />
      </StatCard>

      <!-- 4: Cabo de Guerra -->
      <StatCard title="Cabo de Guerra" subtitle="Distribuição de carga financeira entre os membros">
        <WarBar :data="warData" />
      </StatCard>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import StatCard from '../components/stats/StatCard.vue'
import WarBar from '../components/stats/WarBar.vue'
import FutureRadarChart from '../components/stats/FutureRadarChart.vue'
import LiquidityDonut from '../components/stats/LiquidityDonut.vue'
import FreeCashChart from '../components/stats/FreeCashChart.vue'

// ── Mocks ─────────────────────────────────────────────────────────────────
// TODO: substituir por dados reais do endpoint GET /summary e GET /templates

const warData = ref({
  alvaro:    { label: 'Álvaro',    amount: 3200 },
  alexandra: { label: 'Alexandra', amount: 1800 },
  conjunto:  { label: 'Conjunto',  amount: 2400 },
})

// Proporção fixas vs variáveis do mês atual
const liquidityData = ref({
  fixed:    5500, // aluguel + fixas recorrentes
  variable: 3000, // variáveis + parceladas
})

// Últimos 6 meses: Free Cash e Carryover acumulado
// TODO: substituir por GET /periods (endpoint ainda não implementado no backend)
const freeCashData = ref([
  { month: 'Jan', freeCash: 1800, carryover: 200  },
  { month: 'Fev', freeCash: 2200, carryover: 400  },
  { month: 'Mar', freeCash: 1500, carryover: 600  },
  { month: 'Abr', freeCash: 2800, carryover: 500  },
  { month: 'Mai', freeCash: 2400, carryover: 900  },
  { month: 'Jun', freeCash: 3100, carryover: 1200 },
])

// Próximos 6 meses: mês atual mais alto, decrescendo conforme parcelas expiram
const futureMonthsData = ref([
  { month: 'Jun', value: 8500 },
  { month: 'Jul', value: 8100 },
  { month: 'Ago', value: 7600 },
  { month: 'Set', value: 7200 },
  { month: 'Out', value: 6800 },
  { month: 'Nov', value: 6400 },
])
</script>

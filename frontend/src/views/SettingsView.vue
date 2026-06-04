<template>
  <div class="max-w-4xl mx-auto px-4 pt-5 pb-6 font-ss01">
    <div class="mb-6">
      <h1 class="text-xl font-light tracking-tight text-brand-ink-light dark:text-white">Ajustes</h1>
      <p class="text-sm text-brand-ink-mute-light dark:text-brand-ink-mute-dark mt-1">Gerencie os membros, rendas e categorias do sistema.</p>
    </div>

    <!-- Members & Salaries Section -->
    <div class="bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-stripe-card p-5 shadow-stripe-1 mb-6 transition-colors duration-150">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-medium text-brand-ink-light dark:text-white text-sm">
          Membros e Rendas (Mês Atual)
        </h3>
        <button
          @click="saveMembersAndSalaries"
          :disabled="isSavingMembers"
          class="flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-brand-primary hover:bg-brand-primary-hover text-white text-xs font-semibold active:scale-95 transition-all disabled:opacity-40"
        >
          {{ isSavingMembers ? 'Salvando…' : 'Salvar' }}
        </button>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Membro 1 -->
        <div class="space-y-2">
          <label class="text-xs font-semibold text-brand-ink-mute-light dark:text-brand-ink-mute-dark uppercase tracking-wide">Membro 1</label>
          <div class="flex flex-col sm:flex-row gap-2">
            <input
              v-model="nameAlvaro"
              @keydown.enter="saveMembersAndSalaries"
              placeholder="Nome"
              class="w-full sm:flex-1 px-4 py-2 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20 transition-colors"
            />
            <div class="w-full sm:w-36 flex items-center justify-between px-3 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark rounded-stripe-input">
              <span class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark mr-1">R$</span>
              <CurrencyInput
                v-model="salaryAlvaro"
                @confirm="saveMembersAndSalaries"
                :disabled="dashboardStore.isReadOnly"
                hide-prefix
                input-class="bg-transparent text-right border-0 focus:ring-0 outline-none font-tabular font-medium text-brand-ink-light dark:text-white text-sm w-full"
              />
            </div>
          </div>
        </div>

        <!-- Membro 2 -->
        <div class="space-y-2">
          <label class="text-xs font-semibold text-brand-ink-mute-light dark:text-brand-ink-mute-dark uppercase tracking-wide">Membro 2</label>
          <div class="flex flex-col sm:flex-row gap-2">
            <input
              v-model="nameAlexandra"
              @keydown.enter="saveMembersAndSalaries"
              placeholder="Nome"
              class="w-full sm:flex-1 px-4 py-2 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20 transition-colors"
            />
            <div class="w-full sm:w-36 flex items-center justify-between px-3 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark rounded-stripe-input">
              <span class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark mr-1">R$</span>
              <CurrencyInput
                v-model="salaryAlexandra"
                @confirm="saveMembersAndSalaries"
                :disabled="dashboardStore.isReadOnly"
                hide-prefix
                input-class="bg-transparent text-right border-0 focus:ring-0 outline-none font-tabular font-medium text-brand-ink-light dark:text-white text-sm w-full"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Categories Section Header -->
    <div class="mb-4 flex items-center justify-between">
      <h3 class="font-medium text-brand-ink-light dark:text-white text-sm">Categorias</h3>
      <button
        @click="openAddCategory"
        class="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-brand-primary/[0.08] dark:bg-brand-primary/[0.18] hover:bg-brand-primary/[0.15] text-brand-primary dark:text-brand-primary-soft text-xs font-semibold active:scale-95 transition-all"
      >
        <Plus :size="12" stroke-width="2.5" />
        Categoria
      </button>
    </div>

    <ConfirmModal
      v-model="showConfirmDelete"
      title="Excluir categoria"
      :message="`Excluir '${deleteTarget?.name}'? As despesas vinculadas vão perder a categoria.`"
      confirm-label="Excluir"
      @confirm="doRemove"
    />

    <div class="md:grid md:grid-cols-[340px_1fr] md:gap-8 md:items-start">
      <!-- Left: form -->
      <div class="hidden md:block bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-stripe-card p-5 shadow-stripe-1 transition-colors duration-150">
        <h3 class="font-medium text-brand-ink-light dark:text-white text-sm mb-4">
          {{ editing ? 'Editar Categoria' : 'Nova Categoria' }}
        </h3>

        <div class="space-y-4">
          <!-- Name -->
          <input
            v-model="form.name"
            placeholder="Nome (ex: Alimentação)"
            class="w-full px-4 py-2.5 md:py-2 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20 transition-colors"
          />

          <!-- Icon picker -->
          <div>
            <p class="text-xs font-semibold text-brand-ink-mute-light dark:text-brand-ink-mute-dark uppercase tracking-wide mb-2">Ícone</p>
            <div class="flex flex-wrap gap-1.5">
              <button
                v-for="ico in CATEGORY_ICONS"
                :key="ico.key"
                type="button"
                @click="form.icon = ico.key"
                :title="ico.label"
                class="w-9 h-9 rounded-stripe-input flex items-center justify-center transition-all"
                :class="form.icon === ico.key
                  ? 'bg-brand-primary text-white shadow-stripe-1'
                  : 'bg-brand-canvas-soft-light dark:bg-brand-canvas-dark text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:bg-brand-canvas-soft-light/70 dark:hover:bg-brand-canvas-dark/80'"
              >
                <component :is="ico.component" :size="16" :stroke-width="1.5" />
              </button>
            </div>
          </div>

          <!-- Color picker -->
          <div>
            <p class="text-xs font-semibold text-brand-ink-mute-light dark:text-brand-ink-mute-dark uppercase tracking-wide mb-2">Cor</p>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="c in COLORS"
                :key="c.key"
                type="button"
                @click="form.color = c.key"
                class="w-8 h-8 rounded-full transition-all flex items-center justify-center ring-offset-white dark:ring-offset-brand-canvas-dark"
                :style="{ backgroundColor: c.bg }"
                :class="form.color === c.key ? 'ring-2 ring-brand-primary dark:ring-white scale-110' : 'hover:scale-105'"
              >
                <svg v-if="form.color === c.key" class="w-3 h-3 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Preview -->
          <div class="flex items-center gap-3 p-3 rounded-stripe-input" :style="{ backgroundColor: colorByKey(form.color).light }">
            <component
              :is="getIconComponent(form.icon)"
              :size="22" :stroke-width="1.5"
              :style="{ color: colorByKey(form.color).text }"
            />
            <span class="font-semibold text-sm" :style="{ color: colorByKey(form.color).text }">
              {{ form.name || 'Pré-visualização' }}
            </span>
          </div>

          <!-- Actions -->
          <div class="flex gap-2">
            <button
              @click="save"
              :disabled="!form.name.trim() || saving"
              class="flex-1 py-2.5 md:py-2 px-4 rounded-full bg-brand-primary hover:bg-brand-primary-hover text-white text-sm font-medium disabled:opacity-40 active:scale-[.98] transition-all"
            >
              {{ saving ? 'Salvando…' : editing ? 'Salvar Alterações' : 'Criar Categoria' }}
            </button>
            <button
              v-if="editing"
              @click="cancelEdit"
              class="px-4 py-2.5 md:py-2 rounded-full border border-brand-hairline-light dark:border-brand-hairline-dark text-sm text-brand-ink-light dark:text-white hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark/30 transition-colors"
            >
              Cancelar
            </button>
          </div>
        </div>
      </div>

      <!-- Right: list -->
      <div class="space-y-2">
        <div
          v-for="cat in store.categories"
          :key="cat.id"
          class="bg-white dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-stripe-card px-4 py-2.5 flex items-center gap-3 shadow-stripe-1 transition-colors duration-150"
        >
          <!-- Icon + color swatch -->
          <div
            class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
            :style="{ backgroundColor: colorByKey(cat.color).light, color: colorByKey(cat.color).text }"
          >
            <component :is="getIconComponent(cat.icon)" :size="18" :stroke-width="1.5" />
          </div>

          <span class="flex-1 font-medium text-brand-ink-light dark:text-white text-sm">{{ cat.name }}</span>

          <!-- Color dot -->
          <div class="w-3 h-3 rounded-full flex-shrink-0" :style="{ backgroundColor: colorByKey(cat.color).bg }" />

          <!-- Edit button -->
          <button
            @click="startEdit(cat)"
            class="w-8 h-8 flex items-center justify-center rounded-lg text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark/30 hover:text-brand-ink-light dark:hover:text-white transition-colors"
          >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
          </button>

          <!-- Delete -->
          <button
            @click="remove(cat)"
            class="w-8 h-8 flex items-center justify-center rounded-lg text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:bg-red-500/10 hover:text-red-500 transition-colors"
          >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>
              <path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/>
            </svg>
          </button>
        </div>

        <p v-if="!store.categories.length" class="text-center py-8 text-brand-ink-mute-light dark:text-brand-ink-mute-dark text-sm">
          Nenhuma categoria ainda.
        </p>
      </div>
    </div>

    <!-- Mobile: Nova Categoria sheet -->
    <BaseModal
      v-model="dashboardStore.quickAddCategoryOpen"
      title="Nova Categoria"
      :full-screen-on-mobile="true"
    >
      <div class="space-y-4">
        <input
          ref="categoryNameInput"
          v-model="form.name"
          placeholder="Nome (ex: Alimentação)"
          class="w-full px-4 py-3 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20 transition-colors"
        />
        <div>
          <p class="text-xs font-semibold text-brand-ink-mute-light dark:text-brand-ink-mute-dark uppercase tracking-wide mb-2">Ícone</p>
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="ico in CATEGORY_ICONS"
              :key="ico.key"
              type="button"
              @click="form.icon = ico.key"
              :title="ico.label"
              class="w-9 h-9 rounded-stripe-input flex items-center justify-center transition-all"
              :class="form.icon === ico.key
                ? 'bg-brand-primary text-white shadow-stripe-1'
                : 'bg-brand-canvas-soft-light dark:bg-brand-canvas-dark text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:bg-brand-canvas-soft-light/70 dark:hover:bg-brand-canvas-dark/80'"
            >
              <component :is="ico.component" :size="16" :stroke-width="1.5" />
            </button>
          </div>
        </div>
        <div>
          <p class="text-xs font-semibold text-brand-ink-mute-light dark:text-brand-ink-mute-dark uppercase tracking-wide mb-2">Cor</p>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="c in COLORS"
              :key="c.key"
              type="button"
              @click="form.color = c.key"
              class="w-8 h-8 rounded-full transition-all flex items-center justify-center ring-offset-white dark:ring-offset-brand-canvas-dark"
              :style="{ backgroundColor: c.bg }"
              :class="form.color === c.key ? 'ring-2 ring-brand-primary dark:ring-white scale-110' : 'hover:scale-105'"
            >
              <svg v-if="form.color === c.key" class="w-3 h-3 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            </button>
          </div>
        </div>
        <div class="flex items-center gap-3 p-3 rounded-stripe-input" :style="{ backgroundColor: colorByKey(form.color).light }">
          <component :is="getIconComponent(form.icon)" :size="22" :stroke-width="1.5" :style="{ color: colorByKey(form.color).text }" />
          <span class="font-semibold text-sm" :style="{ color: colorByKey(form.color).text }">{{ form.name || 'Pré-visualização' }}</span>
        </div>
      </div>
      <template #footer>
        <button
          @click="saveModal"
          :disabled="!form.name.trim() || saving"
          class="w-full py-3 rounded-full bg-brand-primary hover:bg-brand-primary-hover text-white text-sm font-medium disabled:opacity-40 active:scale-[.98] transition-all"
        >
          {{ saving ? 'Salvando…' : 'Criar categoria' }}
        </button>
      </template>
    </BaseModal>
  </div>
</template>
<script setup>
import { ref, reactive, watch, nextTick } from 'vue'
import { Plus } from 'lucide-vue-next'
import { useCategoriesStore } from '../stores/categories.js'
import { useDashboardStore } from '../stores/dashboard.js'
import { COLORS, CATEGORY_ICONS, colorByKey, getIconComponent } from '../utils/categories.js'
import ConfirmModal from '../components/ui/ConfirmModal.vue'
import BaseModal from '../components/ui/BaseModal.vue'
import CurrencyInput from '../components/ui/CurrencyInput.vue'

const store = useCategoriesStore()
const dashboardStore = useDashboardStore()
const saving = ref(false)
const editing = ref(null)
const categoryNameInput = ref(null)

function openAddCategory() {
  if (window.innerWidth < 768) {
    dashboardStore.quickAddCategoryOpen = true
  } else {
    const el = document.querySelector('input[placeholder="Nome (ex: Alimentação)"]')
    if (el) {
      el.focus()
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }
}

// Member names local state
const nameAlvaro = ref('')
const nameAlexandra = ref('')
const isSavingMembers = ref(false)

watch(() => dashboardStore.nameAlvaro, (val) => {
  nameAlvaro.value = val
}, { immediate: true })

watch(() => dashboardStore.nameAlexandra, (val) => {
  nameAlexandra.value = val
}, { immediate: true })

// Salaries local state synced with dashboardStore
const salaryAlvaro = ref(0)
const salaryAlexandra = ref(0)

watch(() => dashboardStore.incomeAlvaro, (val) => {
  salaryAlvaro.value = val
}, { immediate: true })

watch(() => dashboardStore.incomeAlexandra, (val) => {
  salaryAlexandra.value = val
}, { immediate: true })

async function saveMembersAndSalaries() {
  isSavingMembers.value = true
  try {
    // Salva os nomes localmente na store/localStorage
    dashboardStore.updateNames(nameAlvaro.value, nameAlexandra.value)

    // Atualiza as rendas no banco de dados para o período atual (se não for somente leitura)
    if (!dashboardStore.isReadOnly) {
      await Promise.all([
        dashboardStore.updateIncome('income_alvaro', salaryAlvaro.value),
        dashboardStore.updateIncome('income_alexandra', salaryAlexandra.value)
      ])
    }
  } catch (err) {
    console.error('Erro ao salvar membros e rendas:', err)
  } finally {
    isSavingMembers.value = false
  }
}

watch(() => dashboardStore.quickAddCategoryOpen, async (val) => {
  if (val) {
    editing.value = null
    form.name = ''
    form.icon = 'Package'
    form.color = 'slate'
    await nextTick()
    categoryNameInput.value?.focus()
  }
})

const form = reactive({ name: '', icon: 'Package', color: 'slate' })

function startEdit(cat) {
  editing.value = cat
  form.name = cat.name
  form.icon = cat.icon
  form.color = cat.color
}

function cancelEdit() {
  editing.value = null
  form.name = ''
  form.icon = 'Package'
  form.color = 'slate'
}

async function save() {
  if (!form.name.trim()) return
  saving.value = true
  try {
    if (editing.value) {
      await store.update(editing.value.id, { name: form.name, icon: form.icon, color: form.color })
      cancelEdit()
    } else {
      await store.create({ name: form.name, icon: form.icon, color: form.color, display_order: store.categories.length })
      form.name = ''
      form.icon = 'Package'
      form.color = 'slate'
    }
  } finally {
    saving.value = false
  }
}

async function saveModal() {
  await save()
  dashboardStore.quickAddCategoryOpen = false
}

const showConfirmDelete = ref(false)
const deleteTarget = ref(null)

function remove(cat) {
  deleteTarget.value = cat
  showConfirmDelete.value = true
}

async function doRemove() {
  if (!deleteTarget.value) return
  await store.remove(deleteTarget.value.id)
  deleteTarget.value = null
  showConfirmDelete.value = false
}
</script>

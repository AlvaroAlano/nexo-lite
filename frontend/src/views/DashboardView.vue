<template>
  <div
    class="max-w-5xl mx-auto px-4 pt-5 pb-6 font-ss01 relative"
    @touchstart="handleTouchStart"
    @touchmove="handleTouchMove"
    @touchend="handleTouchEnd"
  >
    <PullRefreshIndicator :pull-distance="pullDistance" :refreshing="refreshing" />

    <!-- Loading -->
    <div v-if="store.loading && !refreshing" class="flex flex-col items-center justify-center py-20 gap-3">
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

          <!-- Add expense / loan — desktop sidebar -->
          <div v-if="!store.isReadOnly" class="hidden md:block space-y-2">
            <Transition name="btn-bounce">
              <div v-if="!showAddForm" class="space-y-2">
                <button
                  @click="showAddForm = true"
                  class="w-full py-2.5 rounded-stripe-input border border-dashed border-brand-hairline-light dark:border-brand-hairline-dark text-brand-ink-mute-light dark:text-brand-ink-mute-dark text-sm font-medium hover:border-brand-primary hover:text-brand-primary dark:hover:text-white transition-colors"
                >
                  + Nova despesa
                </button>
                <button
                  @click="debtsStore.openLoanModal()"
                  class="w-full py-2.5 rounded-stripe-input border border-dashed border-brand-hairline-light dark:border-brand-hairline-dark text-brand-ink-mute-light dark:text-brand-ink-mute-dark text-sm font-medium hover:border-emerald-500 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors"
                >
                  + Registrar empréstimo
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
              <div>
                <label class="text-[11px] font-semibold uppercase tracking-wide text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-1 block">
                  Categoria <span class="font-normal normal-case opacity-70">· opcional</span>
                </label>
                <CategoryPicker v-model="addForm.category_id" />
              </div>
              <div>
                <label class="text-[11px] font-semibold uppercase tracking-wide text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-1 block">
                  Quem pagou?
                </label>
                <AppSelect v-model="addForm.responsavel" :options="responsavelOpts" />
              </div>
              <CurrencyInput
                v-model="addForm.amount"
                input-class="w-full pr-3 py-2 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input font-tabular text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
              />
              <button
                type="submit"
                :disabled="!addForm.name.trim() || submitting || store.saving"
                class="w-full py-2 rounded-full bg-brand-primary text-white text-sm font-medium hover:bg-brand-primary-hover disabled:opacity-40 active:scale-[.98] transition-all"
              >
                {{ (submitting || store.saving) ? 'Adicionando…' : 'Adicionar' }}
              </button>
            </form>
            </Transition>
          </div>
        </div>

        <!-- ── RIGHT: Expense list + turnover ── -->
        <div>
          <!-- Search bar -->
          <div class="relative mb-3">
            <svg class="absolute left-3.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-brand-ink-mute-light dark:text-brand-ink-mute-dark pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input
              v-model="searchQuery"
              placeholder="Buscar despesa..."
              class="w-full pl-9 pr-9 py-2.5 text-sm bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-xl text-brand-ink-light dark:text-white placeholder:text-brand-ink-mute-light dark:placeholder:text-brand-ink-mute-dark focus:outline-none focus:ring-2 focus:ring-brand-primary/20 transition-all"
            />
            <button
              v-if="searchQuery"
              @click="searchQuery = ''"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:text-brand-ink-light dark:hover:text-white transition-colors"
            >
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <!-- Mobile: compact rows -->
          <TransitionGroup
            tag="div"
            name="exp"
            class="relative divide-y divide-brand-hairline-light/60 dark:divide-brand-hairline-dark/50 md:hidden"
          >
            <ExpenseCard
              v-for="expense in visibleExpenses"
              :key="expense.id"
              :expense="expense"
              @open-rent="openRent"
              @delete="deleteWithUndo"
              @edit="openEditModal"
              @click-detail="openDetailModal"
            />
          </TransitionGroup>
          <p v-if="!visibleExpenses.length" class="md:hidden text-center py-10 text-brand-ink-mute-light dark:text-brand-ink-mute-dark text-sm">
            {{ searchQuery ? 'Nenhuma despesa encontrada.' : 'Nenhuma despesa neste mês ainda.' }}
          </p>

          <!-- Desktop: table with category column -->
          <ExpenseTable
            class="hidden md:block"
            :expenses="visibleExpenses"
            @open-rent="openRent"
            @delete="deleteWithUndo"
            @edit="openEditModal"
            @click-detail="openDetailModal"
          />


          <!-- ── Agendadas (despesas para meses futuros) ─────────────────── -->
          <div v-if="scheduledStore.count" class="mt-5 md:mt-6">
            <button
              @click="scheduledCollapsed = !scheduledCollapsed"
              class="flex items-center justify-between w-full mb-2 group"
            >
              <h3 class="text-[11px] font-bold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark flex items-center gap-1.5">
                Agendadas
                <span class="bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-full px-1.5 py-0.5 text-[9px] font-bold text-brand-ink-mute-light dark:text-brand-ink-mute-dark">
                  {{ scheduledStore.count }}
                </span>
              </h3>
              <svg
                class="w-3.5 h-3.5 text-brand-ink-mute-light dark:text-brand-ink-mute-dark transition-transform duration-300"
                :class="scheduledCollapsed ? '' : 'rotate-180'"
                viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
              >
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </button>

            <div
              class="overflow-hidden transition-all duration-300 ease-in-out"
              :style="scheduledCollapsed ? 'max-height: 0; opacity: 0;' : 'max-height: 1000px; opacity: 1;'"
            >
              <div class="rounded-xl overflow-hidden border border-brand-hairline-light dark:border-brand-hairline-dark/60 bg-white dark:bg-brand-canvas-soft-dark/40">
                <template v-for="group in scheduledStore.byMonth" :key="`${group.year}-${group.month}`">
                  <div class="px-4 py-1.5 bg-brand-canvas-soft-light/70 dark:bg-brand-canvas-soft-dark/50 text-[10px] font-bold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark">
                    {{ monthLabel(group.year, group.month) }}
                  </div>
                  <template v-for="(s, idx) in group.items" :key="s.id">
                    <div class="w-full flex items-center gap-3 px-4 py-3">
                      <span class="flex-1 min-w-0 text-sm font-medium text-brand-ink-light dark:text-white truncate">
                        {{ s.name }}
                      </span>
                      <span class="flex-shrink-0 text-sm font-semibold font-tabular text-brand-ink-light dark:text-white">
                        {{ fmtLoanAmt(s.amount) }}
                      </span>
                      <button
                        @click="scheduledStore.remove(s.id)"
                        class="w-7 h-7 flex items-center justify-center rounded-lg text-brand-ink-mute-light dark:text-brand-ink-mute-dark hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 active:opacity-60 transition-all flex-shrink-0"
                        title="Remover agendada"
                      >
                        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/>
                        </svg>
                      </button>
                    </div>
                    <div v-if="idx < group.items.length - 1" class="h-px bg-brand-hairline-light dark:bg-brand-hairline-dark/30 mx-4" />
                  </template>
                </template>
              </div>
            </div>
          </div>

          <!-- ── Empréstimos Ativos ──────────────────────────────────────── -->
          <div v-if="activeLoans.length" class="mt-5 md:mt-6">
            <!-- Header sanfona -->
            <button
              @click="toggleLoans"
              class="flex items-center justify-between w-full mb-2 group"
            >
              <h3 class="text-[11px] font-bold uppercase tracking-wider text-brand-ink-mute-light dark:text-brand-ink-mute-dark flex items-center gap-1.5">
                Empréstimos
                <span class="bg-brand-canvas-soft-light dark:bg-brand-canvas-soft-dark border border-brand-hairline-light dark:border-brand-hairline-dark rounded-full px-1.5 py-0.5 text-[9px] font-bold text-brand-ink-mute-light dark:text-brand-ink-mute-dark">
                  {{ activeLoans.length }}
                </span>
              </h3>
              <div class="flex items-center gap-2">
                <button
                  @click.stop="debtsStore.openLoanModal()"
                  class="text-[10px] text-brand-primary dark:text-brand-primary-soft font-semibold hover:underline"
                >
                  + novo
                </button>
                <svg
                  class="w-3.5 h-3.5 text-brand-ink-mute-light dark:text-brand-ink-mute-dark transition-transform duration-300"
                  :class="loansCollapsed ? '' : 'rotate-180'"
                  viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
                >
                  <polyline points="6 9 12 15 18 9" />
                </svg>
              </div>
            </button>

            <!-- Lista sanfona -->
            <div
              class="overflow-hidden transition-all duration-300 ease-in-out"
              :style="loansCollapsed ? 'max-height: 0; opacity: 0;' : 'max-height: 600px; opacity: 1;'"
            >
              <div class="rounded-xl overflow-hidden border border-brand-hairline-light dark:border-brand-hairline-dark/60 bg-white dark:bg-brand-canvas-soft-dark/40">
                <template v-for="(loan, idx) in activeLoans" :key="loan.id">
                  <button
                    @click="debtsStore.openLoanModal(loan)"
                    class="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-brand-canvas-soft-light dark:hover:bg-brand-canvas-soft-dark/60 transition-colors active:opacity-70"
                  >
                    <!-- Direction badge -->
                    <span
                      class="flex-shrink-0 text-[9px] font-bold uppercase tracking-wide px-2 py-0.5 rounded-full border"
                      :class="loan.direction === 'me_deve'
                        ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400'
                        : 'bg-red-500/10 border-red-400/20 text-red-500 dark:text-red-400'"
                    >
                      {{ loan.direction === 'me_deve' ? 'Me deve' : 'Eu devo' }}
                    </span>

                    <!-- Name -->
                    <span class="flex-1 min-w-0 text-sm font-medium text-brand-ink-light dark:text-white truncate">
                      {{ loan.name }}
                    </span>

                    <!-- Due date -->
                    <span
                      v-if="loan.due_date"
                      class="flex-shrink-0 text-[10px] font-medium"
                      :class="isLoanOverdue(loan) ? 'text-red-500 dark:text-red-400' : 'text-brand-ink-mute-light dark:text-brand-ink-mute-dark'"
                    >
                      {{ isLoanOverdue(loan) ? 'Atrasado' : fmtLoanDate(loan.due_date) }}
                    </span>

                    <!-- Amount -->
                    <span
                      class="flex-shrink-0 text-sm font-semibold font-tabular"
                      :class="loan.direction === 'me_deve' ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-500 dark:text-red-400'"
                    >
                      {{ fmtLoanAmt(loan.estimated_amount) }}
                    </span>
                  </button>
                  <div v-if="idx < activeLoans.length - 1" class="h-px bg-brand-hairline-light dark:bg-brand-hairline-dark/30 mx-4" />
                </template>
              </div>
            </div>
          </div>

          <!-- Turnover -->
          <div v-if="!store.isReadOnly" class="mt-6 md:mt-8 pt-6 md:pt-6 border-t border-brand-hairline-light dark:border-brand-hairline-dark">
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
    <ExpenseDetailModal
      v-model="showDetailModal"
      :expense="selectedDetailExpense"
      @edit="openEditModal"
      @open-rent="openRent"
      @delete="deleteWithUndo"
    />
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

    <BaseModal v-model="showExpenseModal" :title="editTarget ? 'Editar Despesa' : 'Nova Despesa'" :full-screen-on-mobile="true">
      <div class="space-y-3">
        <input
          v-model="addForm.name"
          placeholder="Nome da despesa"
          class="w-full px-4 py-3 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
        />
        <div>
          <label class="text-[11px] font-semibold uppercase tracking-wide text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-1 block">
            Categoria <span class="font-normal normal-case opacity-70">· opcional</span>
          </label>
          <CategoryPicker v-model="addForm.category_id" />
        </div>
        <div>
          <label class="text-[11px] font-semibold uppercase tracking-wide text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-1 block">
            Quem pagou?
          </label>
          <AppSelect v-model="addForm.responsavel" :options="responsavelOpts" />
        </div>
        <CurrencyInput
          v-if="!editTarget || editTarget.expense_type !== 'rent'"
          v-model="addForm.amount"
          input-class="w-full pr-4 py-3 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input font-tabular text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
        />
        <div v-if="!editTarget">
          <label class="text-[11px] font-semibold uppercase tracking-wide text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-1 block">
            Lançar em
          </label>
          <AppSelect v-model="addForm.target" :options="scheduleOpts" />
          <p v-if="isScheduling" class="mt-1.5 text-[11px] text-brand-ink-mute-light dark:text-brand-ink-mute-dark leading-snug">
            Aparece sozinha quando esse mês abrir — não entra no caixa de agora.
          </p>
        </div>
        <div v-if="editTarget?.expense_type === 'installment'" class="grid grid-cols-2 gap-2">
          <div>
            <label class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-1 block">Parcela atual</label>
            <input
              v-model.number="addForm.installment_current"
              type="number" min="1"
              class="w-full px-4 py-3 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm font-tabular focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
              placeholder="Ex: 3"
            />
          </div>
          <div>
            <label class="text-xs text-brand-ink-mute-light dark:text-brand-ink-mute-dark mb-1 block">Total de parcelas</label>
            <input
              v-model.number="addForm.installment_total"
              type="number" min="1"
              class="w-full px-4 py-3 border border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark text-brand-ink-light dark:text-white rounded-stripe-input text-sm font-tabular focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
              placeholder="Ex: 12"
            />
          </div>
        </div>
        <label v-if="!editTarget && !isScheduling" @click="addForm.is_paid = !addForm.is_paid" class="flex items-center gap-3 py-1 cursor-pointer select-none">
          <div
            class="w-5 h-5 rounded border flex items-center justify-center transition-colors flex-shrink-0 pointer-events-none"
            :class="addForm.is_paid ? 'bg-brand-primary border-brand-primary' : 'border-brand-hairline-light dark:border-brand-hairline-dark bg-white dark:bg-brand-canvas-dark'"
          >
            <svg v-if="addForm.is_paid" class="w-3 h-3 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </div>
          <span class="text-sm text-brand-ink-light dark:text-white">Já paguei</span>
        </label>
      </div>
      <template #footer>
        <button
          @click="editTarget ? saveExpenseEdit() : quickAdd()"
          :disabled="!addForm.name.trim() || submitting || store.saving"
          class="w-full py-3 rounded-full bg-brand-primary text-white text-sm font-medium hover:bg-brand-primary-hover disabled:opacity-40 active:scale-[.98] transition-all"
        >
          {{ (submitting || store.saving) ? 'Salvando…' : (editTarget ? 'Salvar alterações' : (isScheduling ? 'Agendar despesa' : 'Adicionar despesa')) }}
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, reactive, computed } from 'vue'
import { useDashboardStore } from '../stores/dashboard.js'
import { useDebtsStore } from '../stores/debts.js'
import { useCategoriesStore } from '../stores/categories.js'
import { useScheduledStore } from '../stores/scheduled.js'
import { monthLabel } from '../utils/date.js'
import { usePullToRefresh } from '../composables/usePullToRefresh.js'
import PullRefreshIndicator from '../components/ui/PullRefreshIndicator.vue'
import BalanceSummary from '../components/dashboard/BalanceSummary.vue'
import ExpenseCard from '../components/dashboard/ExpenseCard.vue'
import ExpenseTable from '../components/dashboard/ExpenseTable.vue'
import RentModal from '../components/modals/RentModal.vue'
import TurnoverModal from '../components/modals/TurnoverModal.vue'
import BaseModal from '../components/ui/BaseModal.vue'
import CategoryPicker from '../components/ui/CategoryPicker.vue'
import CurrencyInput from '../components/ui/CurrencyInput.vue'
import AppSelect from '../components/ui/AppSelect.vue'
import ExpenseDetailModal from '../components/modals/ExpenseDetailModal.vue'

const store = useDashboardStore()
const debtsStore = useDebtsStore()
const catStore = useCategoriesStore()
const scheduledStore = useScheduledStore()

// ── Search ─────────────────────────────────────────────────────────────────────
const searchQuery = ref('')

const visibleExpenses = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return store.filteredExpenses
  return store.filteredExpenses.filter((e) =>
    e.name.toLowerCase().includes(q) ||
    (e.category || '').toLowerCase().includes(q) ||
    String(parseFloat(e.amount) || 0).includes(q)
  )
})

// ── Loans ──────────────────────────────────────────────────────────────────────
const activeLoans = computed(() =>
  debtsStore.debts.filter((d) => d.status === 'ativo')
)

const loansCollapsed = ref(true)        // sanfonas sempre iniciam fechadas
const scheduledCollapsed = ref(true)

function toggleLoans() {
  loansCollapsed.value = !loansCollapsed.value
}

function isLoanOverdue(loan) {
  if (!loan.due_date) return false
  return new Date(loan.due_date) < new Date()
}

function fmtLoanDate(d) {
  if (!d) return ''
  return new Date(d + 'T12:00:00').toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' })
}

function fmtLoanAmt(n) {
  return (parseFloat(n) || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

const showRent = ref(false)
const rentExpense = ref(null)
const showTurnover = ref(false)
const showAddForm = ref(false)
const showExpenseModal = ref(false)
const editTarget = ref(null)
const showDetailModal = ref(false)
const selectedDetailExpense = ref(null)

function openDetailModal(expense) {
  selectedDetailExpense.value = expense
  showDetailModal.value = true
}

const { pullDistance, refreshing, handleTouchStart, handleTouchMove, handleTouchEnd } =
  usePullToRefresh(() => store.fetchCurrent())

const addForm = reactive({ name: '', category_id: null, responsavel: 'conjunto', amount: 0, is_paid: false, installment_current: null, installment_total: null, target: 'current' })
const submitting = ref(false)

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

// "Lançar em": este mês (default) + próximos 6 meses, a partir do período aberto
const scheduleOpts = computed(() => {
  const opts = [{ value: 'current', label: 'Este mês' }]
  const y = store.period?.year, m = store.period?.month
  if (!y || !m) return opts
  for (let i = 1; i <= 6; i++) {
    let ny = y, nm = m + i
    while (nm > 12) { nm -= 12; ny += 1 }
    opts.push({ value: `${ny}-${nm}`, label: monthLabel(ny, nm) })
  }
  return opts
})

const isScheduling = computed(() => addForm.target && addForm.target !== 'current')

function resetAddForm() {
  addForm.name = ''
  addForm.category_id = null
  addForm.amount = 0
  addForm.responsavel = 'conjunto'
  addForm.installment_current = null
  addForm.installment_total = null
  addForm.is_paid = false
  addForm.target = 'current'
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
    editTarget.value = null
  }
})

onMounted(async () => {
  // categorias em paralelo (dedupe garante 1 request) → ícones preenchem ao resolver
  await Promise.all([store.fetchCurrent(), catStore.fetch()])
  if (!debtsStore.debts.length) debtsStore.fetchDebts()
  scheduledStore.fetch()
  if (store.quickAddOpen && !store.isReadOnly && store.period) {
    showExpenseModal.value = true
    store.quickAddOpen = false
  }
})

onUnmounted(() => {
  if (undoState.value) {
    clearTimeout(undoState.value.timerId)
    store.hardDeleteExpense(undoState.value.expense.id)
    undoState.value = null
  }
})

function openRent(expense) {
  rentExpense.value = expense
  showRent.value = true
}

function openEditModal(expense) {
  editTarget.value = expense
  addForm.name = expense.name
  addForm.category_id = expense.category_id ?? null
  addForm.responsavel = expense.responsavel
  addForm.amount = parseFloat(expense.amount) || 0
  addForm.is_paid = expense.is_paid
  addForm.installment_current = expense.installment_current ?? null
  addForm.installment_total = expense.installment_total ?? null
  showExpenseModal.value = true
}

async function saveExpenseEdit() {
  if (!editTarget.value) return
  const payload = {
    name: addForm.name.trim(),
    category_id: addForm.category_id,
    responsavel: addForm.responsavel,
    ...(editTarget.value.expense_type !== 'rent' && { amount: addForm.amount }),
    ...(editTarget.value.expense_type === 'installment' && {
      installment_current: addForm.installment_current,
      installment_total: addForm.installment_total,
    }),
  }
  try {
    await store.updateExpenseFull(editTarget.value.id, payload)
    showExpenseModal.value = false
  } catch {
    // store.error já foi populado — modal permanece aberto para o usuário ver o erro
  }
}

async function quickAdd() {
  submitting.value = true
  try {
    if (isScheduling.value) {
      const [ty, tm] = addForm.target.split('-').map(Number)
      await scheduledStore.create({
        target_year: ty,
        target_month: tm,
        name: addForm.name.trim(),
        category_id: addForm.category_id,
        expense_type: 'variable',
        responsavel: addForm.responsavel,
        amount: addForm.amount,
      })
    } else {
      await store.addExpense({
        name: addForm.name.trim(),
        category_id: addForm.category_id,
        expense_type: 'variable',
        responsavel: addForm.responsavel,
        amount: addForm.amount,
        is_paid: addForm.is_paid,
      })
    }
    showAddForm.value = false
    showExpenseModal.value = false
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
/* Button: shrinks out fast, pops back in with spring overshoot */
.btn-bounce-leave-active {
  animation: btn-shrink 0.18s ease-in forwards;
}
.btn-bounce-enter-active {
  animation: btn-pop 0.42s var(--ease-spring) forwards;
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

/* Form: slides down softly — ease-out-expo entry, quick exit */
.form-slide-enter-active {
  animation: form-in 0.28s var(--ease-out-expo) forwards;
}
.form-slide-leave-active {
  animation: form-in 0.15s var(--ease-in) reverse forwards;
}

@keyframes form-in {
  from { opacity: 0; transform: translateY(-10px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

/* Undo toast */
.toast-slide-enter-active { animation: toast-in  0.3s var(--ease-spring) forwards; }
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

/* Lista de despesas (mobile): entra suave, sai deslizando, vizinhos reacomodam */
.exp-enter-active { transition: opacity 0.25s ease, transform 0.25s var(--ease-out-expo); }
.exp-leave-active { transition: opacity 0.18s ease, transform 0.18s ease; position: absolute; width: 100%; }
.exp-enter-from   { opacity: 0; transform: translateY(8px); }
.exp-leave-to     { opacity: 0; transform: translateX(-16px); }
.exp-move         { transition: transform 0.28s var(--ease-out-expo); }
</style>

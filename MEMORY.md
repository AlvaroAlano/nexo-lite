# MEMORY — Nexo Lite

Log resumido de mudanças, decisões arquiteturais e ajustes relevantes.
Entradas em ordem cronológica inversa (mais recente no topo).

## 2026-07-01 (3) — Backend: fecha regras de negócio faltantes em expenses.py/templates.py

Continuação da blindagem de `expenses.py`. Adicionado ao mesmo módulo:
- `_ensure_period_open(expense)`: todas as rotas de escrita (update, update-rent, toggle-paid, toggle-excluded, delete, add/delete note) agora rejeitam (400) mudanças em despesa de período `closed` — RN-10 ("meses fechados são somente leitura") só era aplicada no frontend (inputs desabilitados), não no backend; qualquer chamada direta à API furava a regra. `list_notes` (GET) continua liberado, só escrita é bloqueada.
- `_get_owned_category(db, category_id, user_id)`: `update_expense`/`create_expense` aceitavam qualquer `category_id` sem checar se pertencia ao usuário (diferente de `templates.py`, que já checava mas nem assim rejeitava — só ignorava o nome se não achasse, e mesmo assim **gravava** o `category_id` estranho). Corrigido nos dois routers: agora rejeita com 404 se a categoria não pertence ao usuário.
- `update_expense`: passou a validar `installment_current <= installment_total` (mesma regra que já existia em `templates.py` para `installment_paid`).
- `safe_decimal` (`schemas/expense.py`) agora rejeita valor negativo (`ValueError` → 422 do Pydantic) — cobre `RentItem.amount`, `ExpenseCreate/Update.amount`, `TemplateCreate/Update.base_amount`, e `ScheduledExpense.amount` (que reusa a mesma função importada). Não mexi em `schemas/period.py` (income/carryover têm sua própria cópia da função, fora do escopo desta rodada).

**RLS reavaliado:** `DATABASE_URL` conecta ao Supabase como `postgres` (superuser) e o frontend não usa `supabase-js`/anon key em lugar nenhum — logo RLS não protegeria nada hoje (superuser bypassa RLS por padrão). Rebaixado de prioridade no TODO.md com essa nota; isolamento real continua sendo o filtro `user_id` no FastAPI.

`_get_owned_expense` passou a usar `joinedload(MonthlyExpense.period)` para permitir checar `.period.status` sem uma segunda query lazy (que quebraria em contexto async).

---

## 2026-07-01 (2) — Fecha IDOR em expenses.py + remove /summary (dead code)

**IDOR em `routers/expenses.py`:** era o único router sem `get_current_user_id` (todos os demais já tinham sido blindados em 2026-06-22). `MonthlyExpense` não tem `user_id` próprio — só `period_id`. Criada `_get_owned_expense(db, expense_id, user_id)` que faz join com `MonthlyPeriod` e retorna 404 (não 403, para não revelar existência) se a despesa não pertencer ao usuário do token. Aplicada em todas as rotas: create (via período), update, update-rent, toggle-paid, toggle-excluded, delete, e as 3 sub-rotas de notas (list/add/delete). Sem impacto no modo demo local — `get_current_user_id` cai em `DEMO_USER_ID` quando não há token, igual aos outros routers.

**Removido `routers/summary.py` + `schemas/summary.py` + `summaryApi` (frontend):** confirmado dead code (nenhuma chamada no frontend, endpoint `/summary/{period_id}` duplicava lógica de `/periods/current`). Desregistrado de `main.py` e `schemas/__init__.py`. Não confundir com `/vault/summary` (endpoint ativo, feature da Caixinha) — mantido.

Build do frontend (`npm run build`) e sintaxe do backend (`ast.parse`) validados após as mudanças.

---

## 2026-07-01 — Bug real: despesa "some" ao adicionar via recorrência/quick-add + auditoria completa (4 agentes)

**Bug reportado:** usuário cadastrou uma recorrência parcelada com 1 parcela já paga e marcou "Adicionar ao mês atual" — a despesa não aparecia no Check-in.

**Causa raiz:** `TemplatesView.vue` e o `quickAdd` do `DashboardView.vue` usavam `dashboardStore.period` direto do cache do `localStorage`, sem nunca chamar `fetchCurrent()`. Como o app é usado a dois, se a virada de mês acontece em outro dispositivo (ou a sessão fica aberta por muito tempo), o período em cache fica obsoleto/fechado — a despesa era criada presa ao período errado, ou `addExpense` retornava silenciosamente (guard `isReadOnly`) sem lançar erro nem avisar o usuário.

**Correção:**
- `TemplatesView.vue`: `fetchCurrent()` no `onMounted` + revalidação do período imediatamente antes de gravar a despesa no mês atual; aviso visível (`saveWarning`) se o mês não estiver aberto ou a gravação falhar.
- `DashboardView.vue` `quickAdd`: mesmo padrão — revalida com `fetchCurrent()` antes de criar despesa "para este mês" (não afeta agendamento futuro), aviso visível (`addExpenseWarning`) em vez de fechar o modal como se tivesse dado certo.
- Backend `expenses.py` `create_expense`: agora rejeita (400) criação de despesa em período fechado/inexistente — blindagem mesmo se o front enviar `period_id` obsoleto.
- `turnover.py`: carryover estava somando despesas com `is_excluded=true` no cálculo (`Σ expenses`); o frontend já ignorava essas despesas nos totais/saldos desde o commit `bbd8c45`, mas o backend não tinha sido atualizado. Corrigido para excluir `is_excluded` da soma.

**Auditoria completa (4 agentes em paralelo — backend, frontend, banco, UI/UX):** achados não corrigidos nesta sessão, registrados no `TODO.md` (seção "🔎 Auditoria completa 2026-07-01"). Destaques:
- `routers/expenses.py` e `routers/summary.py` são os únicos routers sem `get_current_user_id` (IDOR) — ficaram de fora da blindagem de 2026-06-22.
- `dependencies/auth.py` tem fallback de JWT com `verify_signature=False` — sem `SUPABASE_JWT_SECRET`, aceita token forjado com qualquer `sub`.
- RLS continua 100% ausente em todas as tabelas do Supabase (já era conhecido, reforçado).
- `ConfirmModal.vue` fecha/emite `@confirm` antes do handler assíncrono do chamador resolver — mesma classe do bug relatado se repete em `TemplatesView` (toggleActive/doDelete), `SettingsView` (categorias, sem tratamento de erro nenhum em `categories.js`), `RentModal.save`, e vários handlers do `LoanModal`.
- Lógica de outbox duplicada entre `dashboard.js` e `debts.js`; `scheduled.js` não tem resiliência offline como as outras stores.
- `schema.sql` tem drift menor vs migrations (índice da 018 ausente, `models/__init__.py` não exporta todos os models, coluna legada `category` texto convive com `category_id` sem nunca ter sido limpa).

**Decisão:** não implementar as correções maiores (RLS, auth em expenses/summary, refatorar ConfirmModal, sistema de toast) nesta sessão — são mudanças de maior escopo/risco (fronteira de auth, comportamento usado por muitos chamadores) que exigem priorização explícita do usuário antes de mexer.

---

## 2026-06-22 — Implementação de Resiliência Offline, Segurança e Transações Atômicas

- **Fila Outbox & Cache (Frontend)**: Refatorados stores `dashboard.js` e `debts.js` para salvar dados localmente em `localStorage` e processar requisições offline/cold-start via fila outbox FIFO resiliente. Implementado remapeamento de `tempId` para ID definitivo no retorno do POST e tratamento otimista das escritas.
- **Contraste de Salários no Modal**: Refatorado [IncomeRow.vue](file:///d:/Projetos/nexo-lite/nexo-lite/frontend/src/components/dashboard/IncomeRow.vue) e suas chamadas no [BalanceSummary.vue](file:///d:/Projetos/nexo-lite/nexo-lite/frontend/src/components/dashboard/BalanceSummary.vue) para suportar classes de estilo customizadas (`labelClass`, `valueClass`, `inputClass`), adaptando os textos e inputs dos salários fixos aos temas light/dark dentro do modal, mantendo a compatibilidade do painel escuro fixo no dashboard.
- **Indicador de Sincronismo (`AppHeader.vue`)**: Adicionado ícone de nuvem inteligente na barra superior integrado ao outbox das stores, exibindo se o app está offline, sincronizando ou com pendências na fila.
- **Supabase Auth & Prevenção de IDOR**: Criada dependência centralizada `get_current_user_id` em `auth.py` para validar tokens JWT do Supabase com fallback de desenvolvimento. Injetada a validação nos routers de períodos, templates, categorias, scheduled, debts e vault, prevenindo IDOR.
- **Migration & Consolidated Schema**: Criada migration `017_user_settings.sql` para tabela de preferências sincronizada e atualizado o arquivo global `supabase/schema.sql` consolidado (limpo de colunas legadas e alinhado com todas as migrations).
- **Atomicidade no Turnover**: Envolvida a criação e clonagem de despesas em bloco `async with db.begin_nested()` em `turnover.py`, garantindo rollback em caso de falhas. Escrito e executado com sucesso o script de testes `test_turnover_transaction.py` validando os rollbacks.

## 2026-06-22 — Saldo anterior zerado, múltiplas rendas adicionais (JSONB) e refinamentos estéticos no modal

**Saldo anterior zerado:** O carryover do novo mês agora é inicializado como zero (`0.00`) no motor de virada (`turnover.py`) e ao auto-criar períodos. Evita erros de saldo acumulado indevidamente do mês passado.
**Múltiplas Rendas Adicionais:** Adicionada coluna `additional_income_items` JSONB em `monthly_periods` (migration 016, substituindo a anterior) para suportar múltiplas fontes de receitas adicionais (freelancer, dividendos, etc.) com descrição e valor personalizados.
**Refinamentos de UI/UX no Modal:**
- Adicionada a propriedade `full-screen-on-mobile` ao `BaseModal` de rendimentos no `BalanceSummary.vue` para compatibilidade estética com os outros modais.
- Adicionado um ícone sutil de lápis `✎` ao lado do valor nas linhas de salários e adicionais no modal (via `IncomeRow.vue`), indicando visualmente que o campo é editável.
- Limpeza visual com a mudança do título da seção para apenas "Rendas Adicionais" e o placeholder de novas receitas adicionais para "Descrição".
**Edição Premium com Botão Check:** Implementada interface de edição inline nas rendas/períodos e despesas mobile/desktop (`ExpenseCard.vue` e `ExpenseTable.vue`):
- Exibe um botão de check verde ao lado do input ao editar.
- Dispara uma animação CSS premium pop-out (`scale` + fade) de 300ms no check ao salvar.
- Cancela a edição e reverte ao valor original ao clicar fora (blur) em vez de salvar automaticamente.

---

## 2026-06-19 — Despesas agendadas, entrada cinematográfica, fix ícones, campo categoria

**Despesas agendadas (mês futuro):** nova fila `scheduled_expenses` (migration 014) para "comprar agora, pagar mês que vem". Não toca em nenhuma agregação do mês atual (caixa/saldos/carryover) — por construção. Materializa em `monthly_expenses` quando o período do mês alvo nasce, em 2 pontos: `run_turnover` (após clonar templates) e `get_current_period` (auto-criação). Service único `services/scheduled.py::materialize_scheduled`. No front: store `scheduled.js`, `scheduledApi`, seletor "Lançar em" no modal de Nova Despesa (Este mês + próximos 6, via `monthLabel`) e seção sanfona "Agendadas" no dashboard (agrupada por mês, com excluir). UX: ao agendar, esconde "Já paguei" e o botão vira "Agendar despesa".

**Sanfonas sempre fechadas:** Empréstimos e Agendadas agora iniciam **sempre colapsadas** ao carregar o dashboard (Empréstimos não lê mais `localStorage` para o estado inicial).

**Entrada cinematográfica (AuthView):** hold da splash 1.7s → **3.2s** (ainda pulável ao toque). Cubo entra com `scale+blur` (mola) + **aura radial** que floresce + **sweep de luz** diagonal cruzando o "N"; wordmark expande o `letter-spacing`. `NeonWave` ganhou *ramp* de amplitude (0→1, easeOutCubic ~900ms) no mount — a onda "cresce" ao surgir. Tudo respeita `prefers-reduced-motion`.

**Fix: ícones de categoria não apareciam no dashboard ao entrar** (só após passar por Configurações). Causa: `categories.fetch()` era fire-and-forget sem dedupe/retry; numa 1ª request lenta/falha o dashboard ficava no fallback cinza. Correção: **dedupe de request em voo** no store (promise compartilhada, limpa em sucesso/falha), `await catStore.fetch()` no `onMounted` do DashboardView (em paralelo com `fetchCurrent`), e skeleton `animate-pulse` no ExpenseCard quando a despesa tem `category_id` mas a categoria ainda não carregou.

**Campo Categoria empilhado:** "Categoria (opcional)" quebrava em 2 linhas e desalinhava do campo de responsável. Agora os campos do modal/form são **empilhados com micro-rótulos** (`CATEGORIA · opcional` / `QUEM PAGOU?`); placeholder do CategoryPicker virou "Selecionar" + `truncate`.

---

## 2026-06-18 — Tokens de movimento unificados + nova entrada (onda neon)

**Unificação de easing (motion-consistency):** todos os `cubic-bezier(...)` crus viraram tokens CSS em `:root` (`assets/main.css`): `--ease-out-expo`, `--ease-in`, `--ease-in-out`, `--ease-out-quint`, `--ease-spring`, `--ease-spring-soft`, `--ease-sheet` + `--dur-enter/leave`. Mapeamento 1:1 (mesmas curvas → zero mudança visual). Migrados: App, BaseModal, DashboardView, AuthView, BottomNav, DebtsList, SettingsView, TemplatesView, MilestoneToast, ExpenseCard, ExpenseTable, ForecastModal. Só a curva de "shake" do PIN ficou inline (one-off). Documentado em COMPONENTS.md.

**Nova entrada do AuthView:** removido o typewriter sequencial "Organize./Controle./Nexo Lite." (lento). Agora: cubo Nexo (mola) sobre uma **onda neon** animada + wordmark + hint "toque para entrar". Avança rápido — auto em ~1.7s **ou ao toque/tecla** (skip). Estágio `splash` eliminado; `intro` é o inicial.

**`components/ui/NeonWave.vue` (novo):** onda neon em `<canvas>` 2D puro (sem Three.js — o prompt de referência era React/Three/TS; recriado na stack Vue/JS). Núcleo branco com fade nas pontas + cópias índigo/esmeralda deslocadas (aberração cromática) e brilho aditivo (`globalCompositeOperation='lighter'` + shadowBlur). DPR-aware, ResizeObserver, respeita `prefers-reduced-motion` (quadro estático). Decisão: não adicionar `three` (~150KB gzip) só para um splash.

---

## 2026-06-18 — Polimento de motion (transições de tela, modais, listas)

Auditoria de UI/UX focada em transições. Rotas e modais já estavam bem feitos; correções pontuais:
- `App.vue`: **bug de direção** do slide de rota — `routeOrder` estava `{dashboard,templates,settings,stats}` mas a ordem visual das abas é `{dashboard,stats,templates,settings}`. Corrigido para o slide seguir o sentido real da navegação.
- `assets/main.css`: adicionado **`prefers-reduced-motion`** global (neutraliza animações/transições quase-instantaneamente) — antes só o AuthView tratava. Adicionada util reutilizável **`.stagger-in`** (cascata em filhos diretos, até 8) + keyframe `nx-rise`.
- `StatsView.vue`: cards entram com **stagger** (classe `stagger-in`).
- `DashboardView.vue`: lista de despesas mobile virou **`TransitionGroup`** (`exp-*`) — adicionar/excluir-com-undo/buscar agora animam (entra suave, sai deslizando, vizinhos reacomodam via `.exp-move`). Empty state movido para fora do grupo.

Recomendação não aplicada (registrada no TODO): unificar tokens de easing/duração via CSS vars (motion-consistency) — hoje os cubic-beziers estão repetidos por componente.

---

## 2026-06-18 — DOCUMENTACAO.md reescrita (estado atual completo)

Documentação oficial estava defasada (só cobria Check-in/Recorrências/Ajustes + schema antigo). Reescrita incorporando: stack tecnológica; Tela de Acesso (Auth/biometria/PIN); privacidade e busca no Check-in; Modal de Detalhes + observações (notas); Estatísticas completas (Caixinha, Dívidas com buckets pagável/recebível/quitada, Plano de Quitação, Radar, Evolução, Liquidez, Cabo de Guerra); Empréstimos/Dívidas (LoanModal); Projeção de Recorrências (ForecastModal); BottomNav + speed-dial. Schema atualizado (debts, debt_payments, vault_reconciliations, expense_notes; `is_paid`, `rent_items`, `interest_rate`; colunas rent_* legadas removidas). Endpoints completos (categories, vault, debts+payments+settle, notes, history). Migrations 001–013 tabeladas. Adicionadas seções de estado em localStorage e de Autenticação/Segurança (auth cosmética, demo user, sem token/RLS).

---

## 2026-06-18 — Motor de Quitação (Bola de Neve vs Avalanche)

Primeira peça do motor de quitação, com foco forte em UI/UX e microcopy explicativa.

**Backend:**
- Migration `013_debt_interest_rate.sql`: coluna `interest_rate NUMERIC(6,2)` em `debts` = juros ao MÊS em pontos percentuais (5.00 = 5% a.m.; 0 = sem juros). Model/schemas (Create/Update/Response)/router atualizados.

**Frontend:**
- `composables/usePayoffPlan.js`: `simulatePayoff(debts, monthlyBudget, strategy)` — função pura, simula mês a mês com juros compostos. Modelo: juros incidem sobre todo saldo; aporte aplicado em ordem de prioridade (alvo primeiro, transbordo) — espelha como a Caixinha é jogada inteira na dívida da vez. Detecta inviabilidade (aporte < juros mensais → não quita, retorna `feasible:false`). `usePayoffPlan()` expõe `plan` + `comparison` (roda as 2 estratégias). Validado: avalanche é sempre ≤ juros da snowball.
- `components/stats/PayoffPlan.vue`: seletor de estratégia (Bola de Neve `Snowflake` / Avalanche `MountainSnow`) com badge dinâmico de economia; aporte mensal (CurrencyInput + slider `accent-brand-primary` + chips ±), persistido em `localStorage` (`nexo_payoff_budget`/`nexo_payoff_strategy`); hero "Você fica livre em <mês/ano>" com juros totais; estado inviável em âmbar com sugestão de aporte mínimo (~24 meses); strip de comparação de estratégias; timeline "ordem de ataque" com nº, badge de juros, "Próxima" e data de quitação por dívida. Sugestão de aporte = média de aportes da Caixinha → free cash → 300.
- `LoanModal.vue`: campo "Juros ao mês (% a.m.)" só para `eu_devo`; badge âmbar no detalhe; incluído em create/edit/save.
- `StatsView.vue`: card "Plano de Quitação" (md:col-span-2) após "Dívidas Ativas".

**Decisão:** juros em % ao mês (padrão BR p/ cartão/cheque especial), não APR anual. `me_deve` nunca tem juros no payload.

---

## 2026-06-18 — Auditoria geral + correção de bugs no módulo de dívidas

Análise completa do sistema (API, front, back, banco) com foco no objetivo de quitar dívidas. 4 bugs concretos corrigidos no módulo de dívidas; demais achados (segurança/motor de quitação) registrados no TODO.

**Bugs corrigidos:**
- `DebtsList.vue` (`saveEdit`): edição inline passava número cru a `store.updateDebt`, que repassa ao `PATCH /debts/{id}` (espera objeto `DebtUpdate`) → 422 revertido em silêncio. Agora envia `{ estimated_amount }`.
- `useGamification.js`: `vaultProgressPct`/`payoffEstimate` liam `nextTargetDebt.amount` (campo real é `estimated_amount`) → progresso travado em 100% e payoff NaN. Corrigido + `nextTargetDebt` agora filtra `eu_devo` e `status != quitado`. Idem consumidor em `BalanceSummary.vue`.
- `DebtsList.vue` double-count: cobertura media a mesma caixinha contra cada dívida. Agora `allocation` snowball — caixinha aplicada no foco primeiro, transbordo para as próximas (ordem crescente). `coveragePct` usa o valor alocado.
- `DebtsList.vue` poluição de cálculo: quitadas (saldo 0) viravam "foco" e `me_deve` entrava em `totalDebt`/cobertura. Board separado em **pagáveis** (eu_devo, ativas → foco/totais/cobertura), **recebíveis** (me_deve → seção "Te devem", sem cobertura) e **quitadas** (seção recolhível, acessível para reabrir).

**Achados não corrigidos (registrados no TODO):**
- Segurança: PIN `0610` hardcoded no bundle; WebAuthn sem verificação server-side; Axios não envia token → backend 100% aberto (DEMO_USER fixo). IDOR latente (rotas de debts/expenses/periods filtram por id, não por user_id). Sem RLS. OK para localhost, crítico se hospedar.
- `schema.sql` desatualizado vs migrações (mostra colunas rent_* dropadas na 009; sem debts/vault/categories).
- Zero testes automatizados (turnover/carryover/parcelas são candidatos ideais).
- Estados de casal (nomes, meta, foco, milestones, tema) só no localStorage → divergem entre os 2 dispositivos.
- Motor de quitação incompleto: sem juros/APR (impede avalanche), DebtPayment desconectado da caixinha, sem burn-down nem simulador de payoff, "Auditor IA" é mock.

---

## 2026-06-08 — Auditoria e correção sistemática: backend, frontend, integração e regras de negócio

Análise em 4 partes via subagentes. Nenhuma RN principal estava quebrada, mas vários bugs silenciosos foram corrigidos.

**Backend (críticos corrigidos):**
- `turnover.py`: condição `>` → `>=` na parcela de aluguel (clonava uma vez a mais após último pagamento); variável `current` shadoweava o período aberto (renomeada `inst_current`)
- `expenses.py`: `PATCH /expenses/{id}` passou a bloquear edição direta de `amount` em despesas de aluguel (400)
- `periods.py`: income legado não mais atribui total ao Álvaro (deixava alexandra com 0)

**Backend (médios/baixos):**
- `/history`: N+1 queries → 1 query com JOIN + GROUP BY
- `/turnover`: retorna 400 se não há período aberto
- `/{year}/{month}`: valida `1 <= month <= 12`
- `templates.py`: valida `installment_paid <= installment_total` no PATCH
- `turnover.py`: Caixinha rastreada pelo nome da expense criada (não categoria do template)
- `schemas/expense.py`: `list[dict]` → `list[RentItem]` nos schemas de input; campos legacy `rent_base/water/gas/extras` removidos do model e schema
- `database.py`: `pool_timeout=30` adicionado
- `periods.py`: update de income bloqueia período fechado
- `PeriodWithExpenses` schema criado; endpoints `/current` e `/{year}/{month}` trocaram `response_model=dict`
- Migration `009` criada para dropar colunas legacy do banco

**Regras de negócio:**
- Proteção do Caixinha (delete + detecção no turnover) agora usa `name OR category == "Caixinha"`
- `free_cash` no histórico aplica `max(0, ...)` — consistente com carryover real
- `TemplateCreate` valida `installment_total` obrigatório para `expense_type=installment`

**Frontend (críticos):**
- `deleteExpense`: rollback otimista se API falhar
- `updateIncome`: expõe erro no `error.value` e relança
- `DashboardView`: `onUnmounted` cancela timer do undo e executa delete pendente
- `TemplatesView`: criação de template parcelado empurra para a lista independente do PATCH de `installment_paid`
- `ExpenseDetailModal`: divisor entre rent items estava fora do escopo do `v-for` (`idx` inacessível) — corrigido com `<template>`

**Frontend (médios/baixos):**
- `categories.js`: `fetch(force=false)` — pull-to-refresh passa `true`
- `SettingsView`: pull-to-refresh com force; feedback visual de erro no save de salários
- `StatsView`: `fetchAll` com guard (só dispara se sem dados)
- `useGamification`: fallback `|| 600` → `|| 0`; watcher de milestone registrado apenas uma vez
- `App.vue`: removido `catStore.fetch()` redundante (router guard já cobre)
- `TemplatesView`: error handling no `fetchTemplates` com state visível
- `updateExpenseFull`: expõe erro; modal de edição só fecha em caso de sucesso

**Integração:**
- `runTurnover`: catch com erro exibido no `TurnoverModal` (modal não fecha em falha)
- `updateExpenseAmount`: guard contra `expense_type === 'rent'` antes de chamar API
- `addToCurrentMonth` para aluguel: recalcula `amount` de `rent_items` em vez de usar `base_amount`

---

## 2026-06-08 — Feature: Pull-to-refresh no Mobile (Dashboard)

**Contexto:** Aplicativos PWA instalados no mobile ou rodando em modo flex com `overflow-hidden` no body perdem o gesto nativo do browser de puxar para atualizar (pull-to-refresh). Para atualizar o app, o usuário precisava fechá-lo por completo e abri-lo novamente.

**Criado / Alterado:**
- Alterado `views/DashboardView.vue`:
  - Adicionados eventos de toque (`touchstart`, `touchmove`, `touchend`) no container do Dashboard.
  - Implementada a detecção se a rolagem está no topo e o cálculo de distância com resistência física dinâmica.
  - Adicionado o componente de Pull-to-refresh (exclusivo para mobile) com transição suave, seta rotativa que se transforma em spinner e texto de instrução reativo.
  - Disparado `store.fetchCurrent()` ao soltar no limiar de 45px e resetado o estado.

---

## 2026-06-08 — Fix: Suporte a Safe Area (Notch / Status Bar) no iOS

**Contexto:** No iPhone 13 (e outros aparelhos iOS com notch/câmera física no topo), a barra de status translúcida causava sobreposição do cabeçalho da aplicação e cabeçalhos de modais de tela cheia, impedindo a interação com os botões.

**Criado / Alterado:**
- Alterado `components/layout/AppHeader.vue`: adicionado padding superior usando a variável de ambiente CSS `env(safe-area-inset-top, 0px)` para empurrar o conteúdo do header para fora da área do notch.
- Alterado `components/ui/BaseModal.vue`: adicionado cálculo dinâmico de padding superior no cabeçalho do modal base se estiver em modo `fullScreenOnMobile`, garantindo que botões e títulos fiquem visíveis e clicáveis em modais tela inteira no iOS.

---

## 2026-06-08 — Feature: Modal de detalhes e menu 3 pontinhos na Dashboard

**Contexto:** Melhorar a UX na Dashboard de despesas ao ocultar botões diretos de ações (editar/excluir) e reuni-los em um menu dropdown vertical de 3 pontinhos, além de introduzir a visualização detalhada de qualquer despesa (composição do aluguel inclusa) ao clicar no card ou na linha correspondente.

**Criado / Alterado:**
- Criado `components/modals/ExpenseDetailModal.vue`: exibe informações estruturadas da despesa (nome, valor, status de pagamento, categoria com ícone e cor, responsável, progresso de parcelas e lista detalhada de sub-itens de aluguel se houver), além de oferecer ações rápidas.
- Alterado `components/dashboard/ExpenseCard.vue` (mobile) e `ExpenseTable.vue` (desktop):
  - Habilitado evento de clique para abrir o modal de detalhes e propagação de clique bloqueada nas outras interações.
  - Substituídos botões fixos de edição e exclusão pelo menu de 3 pontinhos vertical com dropdown flutuante (opções: Ver detalhes, Editar, Excluir).
- Alterado `views/DashboardView.vue`: importado `ExpenseDetailModal`, definidos estados controladores e conectados todos os eventos de clique e ações filhas.

---

## 2026-06-08 — Fix: Sincronização e carregamento de categorias no Login/SPA

**Contexto:** Ao carregar a aplicação pela primeira vez sem estar autenticado, o `App.vue` realizava o fetch das categorias no `onMounted` e falhava/retornava vazio por falta de autorização. Com o redirecionamento para `/auth`, o usuário digitava o PIN e entrava na Dashboard (sem recarregar o `App.vue`), mantendo o store de categorias vazio. As categorias só apareciam após recarregar a página manualmente (F5) enquanto logado.

**Criado / Alterado:**
- Alterado `stores/categories.js`: adicionada a função `clear()` para redefinir `categories.value = []`.
- Alterado `router/index.js`: importado `useCategoriesStore` e chamada a action `catStore.fetch()` no `beforeEach` caso o usuário esteja autenticado, garantindo o carregamento ao passar pelo login ou em qualquer transição de rota de segurança.
- Alterado `views/SettingsView.vue` e `components/ui/CategoryPicker.vue`: adicionada chamada resiliente `store.fetch()` no `onMounted` como garantia dupla caso o store ainda esteja vazio.
- Alterado `views/AuthView.vue`: adicionada chamada para `catStore.fetch()` no sucesso da autenticação (via PIN ou biometria) e `catStore.clear()` junto a `sessionStorage.removeItem('nexo_authenticated')` no `switchProfile()`.

---

## 2026-06-06 — Fix: Fluxo de edição de categorias no mobile

**Contexto:** O formulário de edição de categorias no mobile ficava oculto (`hidden md:block`), impossibilitando a edição a partir do menu de 3 pontos. Além disso, o watcher de abertura do modal limpava o estado de edição sempre que era aberto.

**Criado / Alterado:**
- Alterado `SettingsView.vue`:
  - Feito o título do modal responsivo para mostrar "Editar Categoria" quando a categoria estiver sendo editada.
  - Atualizado o watcher de `quickAddCategoryOpen` para apenas resetar o formulário se não houver categoria em edição, e chamar `cancelEdit()` ao fechar.
  - Atualizado `startEdit()` para abrir o modal de categorias (`quickAddCategoryOpen = true`) no mobile.
  - Atualizado o botão de salvar no rodapé do modal para exibir "Salvar alterações" se estiver em modo de edição.

---

## 2026-06-06 — Fix: Espaçamento da Virada de Mês no mobile

**Contexto:** O painel de "Virada de Mês" tinha margens e paddings fixos muito grandes (`mt-8 pt-6`), gerando um espaçamento exagerado abaixo do último item da lista de despesas (geralmente a Caixinha) no layout mobile.

**Criado / Alterado:**
- Alterado `DashboardView.vue`: ajustada a classe do container de Virada de Mês para utilizar valores responsivos (`mt-0 md:mt-8 pt-0 md:pt-6`), removendo o margin top e padding top no mobile para sanar totalmente o espaço em branco abaixo da Caixinha.

---

## 2026-06-05 — Aluguel: editor de componentes no template + turnover inteligente

**Contexto:** Usuário deletou a despesa manual de R$ 1.800 do Check-in e precisa de um sistema próprio para o boleto do aluguel com componentes (fixos, variáveis como gás, parcelados como IPTU).

**Criado / Alterado:**
- Criado `RentItemsEditor.vue` em `ui/`: componente reutilizável para editar `rent_items[]`. Props: `modelValue`/`v-model`. Mostra lista de itens (badge de tipo, edição de valor inline), formulário de adição de item (tipo fixo/variável/parcela), total calculado.
- Alterado `TemplatesView.vue`: formulário de Aluguel agora exibe `RentItemsEditor` no lugar do campo `base_amount`. `emptyForm()` e `startEdit()` carregam `rent_items`. Payloads de criação/edição incluem `rent_items`; `base_amount` é calculado como soma dos itens. `addToCurrentMonth` para rent também passa `rent_items`.
- Alterado `schemas/expense.py`: adicionado `rent_items: list[dict] = []` em `TemplateCreate`, `TemplateUpdate` (Optional) e `TemplateResponse`; adicionado `rent_items: list[dict] = []` em `ExpenseCreate`.
- Alterado `routers/templates.py`: `create_template` passa `rent_items=payload.rent_items`.
- Alterado `routers/expenses.py`: `create_expense` passa `rent_items` quando `expense_type == 'rent'`.
- Alterado `services/turnover.py`: clonagem inteligente por tipo de item — fixo clona igual; variável clona com `amount="0.00"` (usuário preenche no mês); parcela clona com `installment_current` atual e incrementa o template (quando `current > total`, item é pulado).

**Decisão:** `installment_current > installment_total` = item concluído (permanece no template para histórico, não clona). Variáveis sempre zeram no clone — usuário preenche via RentModal. Template atualiza `rent_items` no DB a cada turnover para rastrear progresso das parcelas.

---

## 2026-06-05 — Fix: Navegação fixa no mobile (BottomNav)

**Contexto:** O menu inferior (BottomNav) não estava respeitando a posição fixa na tela em dispositivos mobile, comportando-se de forma absoluta/scrollável junto com o conteúdo (exigindo rolar a página até o final para aparecer). Isso é um comportamento comum no iOS Safari e Android Chrome quando o `html` e `body` possuem altura forçada em 100% e o conteúdo os ultrapassa.

**Criado / Alterado:**
- Alterado `index.html` para remover a classe `h-full` das tags `<html>`, `<body>` e `<div id="app">`, permitindo que o documento cresça naturalmente e delegando o scroll corretamente ao navegador de forma nativa.
- Alterado `App.vue` para substituir a classe `min-h-full` do container principal por `min-h-[100dvh]`, garantindo que o app ocupe no mínimo a tela inteira (respeitando a barra de endereços dinâmica dos navegadores mobile), sem restringir o comportamento de elementos com posição `fixed`, e adicionado `pb-28` para compensar a altura do menu flutuante.
- Alterado `BottomNav.vue` para centralizar horizontalmente e fixar o menu flutuante no rodapé. O componente agora utiliza `<Teleport to="body">` e um wrapper flexível com `pointer-events-none` e `inset-x-0` para garantir posicionamento absoluto matematicamente preciso, imune ao contexto de empilhamento de contêineres pais com transformações (como as transições do Vue).
- Removida a classe `md:hidden` do componente `BottomNav` no `App.vue`, sendo movida nativamente para dentro da hierarquia do próprio componente no `Teleport`.

---

## 2026-06-03 — Customização de Nomes, Salários e Aba de Ajustes

**Contexto:** Unificação do gerenciamento de perfis e categorias na aba de Ajustes. Suporte à edição dinâmica dos nomes dos membros do casal no frontend e inputs rápidos de renda do mês ativo na tela de configurações.

**Criado / Alterado:**
- Alterado `dashboard.js` para gerenciar os nomes reativos `nameAlvaro` e `nameAlexandra` persistidos no `localStorage`.
- Alterado `SettingsView.vue` para renomear título/subtítulo para "Ajustes", adicionar uma nova seção "Membros e Rendas" com inputs para customizar os nomes em tempo real e campos rápidos (`CurrencyInput`) integrados a `updateIncome` do mês atual.
- Alterado `BottomNav.vue` e `AppHeader.vue` para evoluir a aba "Categorias" para "Ajustes", alterando os rótulos e substituindo o ícone `Tag` por `Settings` (engrenagem). Reordenadas as abas de navegação (Check-in -> Estatísticas -> FAB -> Recorrências -> Ajustes) para agrupar operação/dados à esquerda e planejamento/ajustes à direita.
- Alterado `BottomNav.vue` para ocultar o FAB (botão '+') na rota de Ajustes (Settings), deixando a interface mais limpa.
- Alterado `SettingsView.vue` para adicionar botão compacto '+ Categoria' com ícone Plus ao lado do título da seção, que abre o modal de categorias no mobile e foca/rola até o input correspondente no desktop.
- Alterado `BalanceSummary.vue` para exibir dinamicamente os nomes dos membros da store nas abas gerais, nas rendas individuais e nos saldos livres de Álvaro/Alexandra.
- Alterados `DashboardView.vue` e `TemplatesView.vue` para tornar o array `responsavelOpts` uma propriedade computed que utiliza os nomes configurados pelo usuário na store Pinia.
- Alterados `ExpenseCard.vue` e `ExpenseTable.vue` para exibir o nome dinâmico nos badges de responsável das despesas.
- Alterado `TemplatesView.vue` para reorganizar o card de recorrência, posicionando o nome no topo (ocupando toda a largura útil) e o badge de tipo na linha inferior, inline ao lado da categoria. Isso otimiza o espaço horizontal e previne que nomes longos sofram truncagem precoce no mobile.
- Validada compilação estática do bundle via build de produção.

---

## 2026-06-03 — Deleção de despesas & Melhorias em Parcelamentos (Recorrências)

**Contexto:** Adição de deleção de despesas no Check-in e otimização no fluxo de criação de parcelas no formulário de Recorrências.

**Criado / Alterado:**
- Alterado `ExpenseCard.vue` para adicionar botão compacto com lixeira (SVG) condicional a `!isReadOnly` emitindo `@delete`.
- Alterado `ExpenseTable.vue` para adicionar coluna de deleção que se revela no hover da linha, condicional a `!isReadOnly` e ajustando `colspan` da linha vazia.
- Alterado `DashboardView.vue` para importar/renderizar `ConfirmModal` e manipular o estado de confirmação e disparo da action da store `store.deleteExpense()`.
- Alterado `TemplatesView.vue` para calcular dinamicamente o valor de cada parcela a partir do valor total inserido, exibir labels dinâmicos para despesas parceladas, apresentar um resumo de parcelas (pagas/restantes/totais) e exibir o valor total na listagem de recorrências à direita.
- Corrigido o modal de criação mobile em `TemplatesView.vue`, substituindo as tags `<option>` nativas pelas propriedades `:options="responsavelOpts"` e `:options="expenseTypeOpts"` no `AppSelect`.
- Alterado `AppHeader.vue` para exibir o logo box compacto `"N"` no canto esquerdo da barra de navegação superior nos layouts mobile.
- Criado `icon.svg` e gerados os ícones físicos `icon-192.png` e `icon-512.png` na pasta `public/icons` (usando a ferramenta `sharp` temporária), tornando a aplicação um PWA 100% instalável e offline-ready (22 recursos no precache do Service Worker).
- Alterados `BottomNav.vue` e `AppHeader.vue` para aumentar paddings, tamanhos de botões, ícones e fontes nos layouts mobile (melhorando a acessibilidade e targets de toque).
- Alterados `DashboardView.vue` e `TemplatesView.vue` para remover o focus automático (`.focus()`) nos campos de input ao abrir os modais mobile rápidos, prevenindo a abertura indesejada do teclado virtual.
- Validada compilação do bundle via build de produção completo.

---

## 2026-06-03 — Stripe-Inspired Design System & Dark Mode

**Contexto:** Refatoração de frontend para aplicar design system inspirado na arquitetura de confiança do Stripe, responsividade mobile-first e Dark Mode.

**Criado / Alterado:**
- `design_system.md` na raiz do projeto documentando os tokens e diretrizes Stripe.
- Configuração do Tailwind (`tailwind.config.js`) com `darkMode: 'class'`, novas cores brand, sombras stripe-1/stripe-2 e arredondamentos stripe-card/stripe-input.
- Reset de cores em `main.css` baseadas nos canvas e textos Stripe (Light/Dark), e novas classes `.font-ss01` e `.font-tabular` (`font-feature-settings` e `letter-spacing: -0.42px`).
- Injeção de script de FOUC preventivo no `<head>` do `index.html` e adição do peso 300 da fonte Inter.
- Botão de toggle de tema minimalista com ícones no `AppHeader.vue` persistido via `localStorage`.
- Componentes e Views refatorados para suporte a Light/Dark Mode, botões pílula (`rounded-full`), inputs arredondados (`rounded-stripe-input`), área de toque de no mínimo 40px no mobile, tipografia `font-tabular` em valores monetários, e modais de tela cheia no mobile com rodapé fixo e seguro.
- Modais Híbridos (Mobile): Modais contendo formulários/listas (como `RentModal.vue` e `TurnoverModal.vue`) configurados para usar o padrão de tela inteira (`full-screen-on-mobile`), enquanto modais de confirmação simples (`ConfirmModal.vue`) ou seletores flutuam centralizados com `backdrop-blur`. Regras e diretrizes devidamente documentadas em `design_system.md`, `COMPONENTS.md` e `CLAUDE.md` como padrão do sistema.
- Bloqueio de Scroll do Body: Adicionada lógica de controle no `BaseModal.vue` usando watchers e hooks de desmontagem para adicionar/remover a classe `overflow-hidden` do `document.body` quando um modal é aberto/fechado, impedindo a rolagem do plano de fundo.
- Desacoplamento da Coluna Esquerda: Adicionada a classe `md:self-start` ao container sticky da coluna esquerda (`div.md:sticky`) no `DashboardView.vue` para forçar `align-self: flex-start`, impedindo que a coluna esquerda se estique verticalmente acompanhando o crescimento da lista de despesas da coluna direita.

---

## 2026-06-03 — Estrutura base do projeto

**Contexto:** Início do projeto Nexo Lite — sistema de check-in financeiro mensal.

**Criado:**
- Backend FastAPI: `app/models/` (period, expense/template), `app/schemas/` (Pydantic v2 com `safe_decimal`), `app/routers/` (periods, expenses, templates, summary), `app/services/turnover.py`
- Frontend Vue 3 + Pinia: views (Dashboard, Templates), components (BalanceSummary, ExpenseCard, ExpenseTable, RentModal, TurnoverModal, BaseModal), stores/dashboard.js, services/api.js, utils (currency, date)
- Supabase: `migrations/001_initial_schema.sql` com 3 tabelas, indexes, triggers `updated_at` e seed de demo

**Decisões:**
- Auth: demo user hardcoded (`00000000-...-0001`); `get_user_id()` em `routers/periods.py` e `routers/templates.py` é o único ponto de troca quando Supabase Auth for integrado
- Carryover: `max(0, income + carryover_anterior - Σ expenses.amount)` — não propaga débito entre meses
- Aluguel: `amount` sempre = soma dos componentes (rent_base + water + gas + extras), nunca editado diretamente
- Instalments: `expense_templates.installment_paid` é o contador real; ao clonar, incrementa e cria `monthly_expenses` com `installment_current = novo valor`

---

## 2026-06-03 — Titularidade por pessoa + navegação de meses

**Contexto:** Revisão do prompt com Gemini adicionou divisão de casal e histórico de meses.

**Adicionado:**
- Migration `002_add_responsavel_and_income_split.sql`: novas colunas `responsavel` (alvaro/alexandra/conjunto) em `expense_templates` e `monthly_expenses`; colunas `income_alvaro` e `income_alexandra` em `monthly_periods`
- Arquivo `regras.md` com as 10 regras de negócio do sistema (RN-01 a RN-10)
- Endpoint `GET /api/periods/{year}/{month}` para navegação de meses
- Store: `currentView` (geral/alvaro/alexandra), `isReadOnly`, `notFoundMonth`, `fetchByMonth`, saldos por pessoa computados (`saldoAlvaro`, `saldoAlexandra`)
- AppHeader: `< Junho 2026 >` com botões de navegação; retorna ao mês atual ao clicar no label
- BalanceSummary: abas de 3 visões (Visão Geral / Álvaro / Alexandra), separado em sub-componentes `IncomeRow` e `FreeCashDisplay`
- DashboardView: formulário expandível de adição com campo `responsavel`; modo read-only (meses fechados ocultam botões de edição); estado "mês não criado" com CTA de virada
- ExpenseCard: badge colorido de titularidade (azul=Álvaro, rosa=Alexandra, cinza=Casal)
- Templates e formulários: campo `responsavel` em todas as telas de criação

**Decisões:**
- Despesas `conjunto` aparecem apenas na aba "Visão Geral" (não nos saldos individuais) — RN-02
- `income` original mantido para compatibilidade; `income_alvaro + income_alexandra` é a fonte de verdade — RN-03
- Navegação para mês futuro inexistente mostra estado vazio com CTA de virada — RN-05

---

## 2026-06-03 — Setup local + scripts de inicialização

**Contexto:** Criar scripts para rodar o sistema localmente sem precisar de git push.

**Problema encontrado:** Python 3.14 (único instalado) não tem wheels pré-compiladas para `asyncpg==0.30.0` (exige MSVC) nem para `pydantic-core==2.27.1` (exige Rust + link.exe).

**Solução:** Trocado `asyncpg` por `psycopg[binary]>=3.2.0` (tem wheel cp314 no PyPI) e liberalizadas as versões do pydantic/fastapi para pegar o binário mais recente. Adicionado `--prefer-binary` no pip install.

**Criado:**
- `setup.bat` — instala venv Python, deps, npm (roda uma vez)
- `start.bat` — duplo clique abre Backend + Frontend em janelas separadas + browser
- `backend/app/services/__init__.py` — arquivo faltante
- `"type": "module"` em `package.json` — remove warning do Node sobre ES module

**Testado:**
- Backend: `uvicorn` sobe, imports OK, `/health` responde
- Frontend: Vite inicia em 495ms em `http://localhost:5173`
- DATABASE_URL: ainda precisa ser preenchida com dados reais do Supabase

---

## 2026-06-03 — Correcao encoding dos .bat (ASCII puro)

**Problema:** `setup.bat` e `start.bat` foram escritos em UTF-8 com caracteres especiais (╔, ║, ç). O CMD do Windows le arquivos .bat em ANSI (cp1252), transformando os bytes UTF-8 em lixo que tenta executar como comandos.

**Solucao:** Reescritos ambos os arquivos em ASCII puro (0-127 apenas). Verificado com `[System.IO.File]::ReadAllBytes()` — 0 bytes acima de 127. Regra para o futuro: arquivos .bat devem ser 100% ASCII — sem acentos, sem box-drawing, sem emoji.

---

## 2026-06-03 — Remove categorias da UI

Categorias removidas de: ExpenseCard (badge), ExpenseTable (coluna), DashboardView (agrupamento e form), TemplatesView (form). Campo `category` mantido no DB/model sem migration. Lista de despesas agora é flat, ordenada por `display_order`. Badge de titularidade adicionado na tabela desktop.

---

## 2026-06-03 — Aluguel com itens dinâmicos (JSONB)

Boleto real: Aluguel 1200 + Condomínio 215 + CredPago 9/12 + IPTU 5/8 + Seguro + Gás (variável). Os 4 campos fixos (rent_base/water/gas/extras) não comportavam essa estrutura.

Solução: `rent_items JSONB` em `monthly_expenses` e `expense_templates`. Cada item tem: id, name, amount, type (fixed/variable/installment), installment_current, installment_total. Antigos campos mantidos no DB mas ignorados pela app. Migration 003 adicionada. RentModal redesenhado com lista dinâmica, adição/remoção de itens, edição de valor inline, preview no card.

---

## 2026-06-03 — Categorias com cor e ícone (tela de configurações)

Nova tabela `categories` (migration 004) com `name`, `color` (chave da paleta), `icon` (emoji). FK `category_id` adicionada em `monthly_expenses` e `expense_templates` (nullable, SET NULL on delete). Backend: model, schemas, router CRUD. Frontend: `utils/categories.js` (12 cores + 30 ícones), `stores/categories.js`, `CategoryPicker.vue` (dropdown reutilizável), `SettingsView.vue` com picker de cor + emoji + preview em tempo real. Badge colorido no ExpenseCard usa cor da categoria via `category_id`. Carregamento de categorias no `App.vue` (uma vez, cached na store).

---

## 2026-06-03 — Ícones Lucide (traço fino, SVG, sem emoji)

Emoji substituídos por ícones Lucide (lucide-vue-next). Ícones: stroke-width 1.5, traço fino, estilo big tech (Linear, Vercel). 30 ícones curados para categorias financeiras. DB armazena o nome do ícone (string, ex: 'Home', 'CreditCard'). Migration 004 atualizada: VARCHAR(50), nomes Lucide. `utils/categories.js` exporta mapa de componentes. `SettingsView`, `CategoryPicker` e `ExpenseCard` usam `<component :is="getIconComponent(key)">`.

---

## 2026-06-03 — CurrencyInput com máscara em tempo real

Componente `CurrencyInput.vue` criado. Lógica: armazena centavos como inteiro, formata com `Intl.NumberFormat pt-BR` a cada tecla pressionada — digitar `12345` exibe `123,45`. Props: `modelValue` (Number), `inputClass`, `hidePrefix`. Emite `confirm` (Enter) e `cancel` (Escape) para fechar inline edits. Aplicado em: DashboardView (add form), TemplatesView (base_amount), RentModal (item amount), IncomeRow (renda), ExpenseCard (inline edit), ExpenseTable (inline edit). Todos os campos de valor migrados de `type="number"` para `CurrencyInput`.

---

## 2026-06-03 — Fixes: parcelas no template, template→mês atual, foco CurrencyInput

1. `TemplatesView`: form de parcelada agora tem dois campos — "Parcelas já pagas" (default 0) e "Total de parcelas". Validação: paid ≤ total. Checkbox "Adicionar ao mês atual também" — quando marcado, cria a expense no mês aberto via dashboard store com installment_current = paid+1.
2. `ExpenseTable`: foco corrigido usando `$el.querySelector('input')` em vez de `editInputRef.value?.focus()` (CurrencyInput é um componente, não um input nativo). Adicionado @blur para salvar ao clicar fora.
3. `ExpenseCard`: @blur adicionado no CurrencyInput inline para salvar ao tirar o foco.
4. Backend: `ExpenseCreate` agora aceita `installment_current` e `installment_total`; router passa esses campos ao criar.

---

## 2026-06-03 — AppSelect + biblioteca de componentes (COMPONENTS.md)

`AppSelect.vue` criado em `ui/`: wraps native `<select>` com `appearance-none`, seta Lucide ChevronDown, `rounded-xl`, padrão visual do sistema. Substituído em TemplatesView (2x), DashboardView (1x), RentModal (1x). `COMPONENTS.md` criado na raiz como referência da biblioteca: documenta todos os componentes `ui/`, estrutura de pastas, design tokens (cores, bordas, tipografia, ícones). CLAUDE.md atualizado com regra: consultar COMPONENTS.md antes de criar UI nova.

---

## 2026-06-03 — ConfirmModal substitui confirm() nativo

`ConfirmModal.vue` criado em `ui/`. Props: title, message, confirmLabel, cancelLabel, variant (danger/default). Substituiu `confirm()` nativo em TemplatesView (excluir recorrência) e SettingsView (excluir categoria). Regra adicionada ao CLAUDE.md: nunca usar confirm/alert/prompt nativos. Documentado no COMPONENTS.md.

---
<!-- Adicionar entradas acima desta linha -->

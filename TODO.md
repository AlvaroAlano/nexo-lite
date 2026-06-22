# TODO — Nexo Lite

Lista de tarefas do projeto. Atualize sempre que uma tarefa for concluída ou nova for identificada.

**Legenda:**
- `[ ]` — pendente
- `[~]` — em andamento
- `[x]` — concluído (data entre parênteses)

---

## 🏗️ Infraestrutura & Setup

- [x] Estrutura de pastas do projeto (backend + frontend) — (2026-06-03)
- [x] Arquivo `requirements.txt` e `.env.example` — (2026-06-03)
- [x] `package.json`, `vite.config.js`, `tailwind.config.js` — (2026-06-03)
- [x] Migration `001_initial_schema.sql` para Supabase — (2026-06-03)
- [x] Migration `002_add_responsavel_and_income_split.sql` — (2026-06-03)
- [x] `regras.md` com 10 regras de negócio (RN-01 a RN-10) — (2026-06-03)
- [x] `setup.bat` — instalação de dependências em um clique — (2026-06-03)
- [x] `start.bat` — liga Backend + Frontend + abre browser — (2026-06-03)
- [x] Trocar `asyncpg` por `psycopg[binary]` para compatibilidade com Python 3.14 — (2026-06-03)
- [x] `"type": "module"` no package.json — remove warning ES module do Node — (2026-06-03)
- [x] Backend testado: imports OK, uvicorn sobe, /health responde — (2026-06-03)
- [x] Frontend testado: Vite 6.4.3 inicia em ~500ms — (2026-06-03)
- [ ] Rodar migrations 001–008 no Supabase
- [ ] Rodar migration 009 (dropar colunas legacy rent_base/water/gas/extras) no Supabase
- [ ] Preencher `backend/.env` com DATABASE_URL real do Supabase
- [ ] Testar fluxo completo com banco de dados conectado

## ⚙️ Backend

- [x] Models SQLAlchemy: `MonthlyPeriod`, `ExpenseTemplate`, `MonthlyExpense` — (2026-06-03)
- [x] Schemas Pydantic com `safe_decimal` anti-quebra — (2026-06-03)
- [x] Router `/periods` (current, income patch, turnover) — (2026-06-03)
- [x] Router `/expenses` (CRUD + toggle-paid + rent breakdown) — (2026-06-03)
- [x] Router `/templates` (CRUD) — (2026-06-03)
- [x] Router `/summary` (dashboard aggregation) — (2026-06-03)
- [x] Serviço de virada de mês (`services/turnover.py`) — (2026-06-03)
- [x] Endpoint `GET /periods/{year}/{month}` para navegação de meses — (2026-06-03)
- [x] Campo `responsavel` em models, schemas, routers e serviço de turnover — (2026-06-03)
- [x] Campos `income_alvaro` / `income_alexandra` no model `MonthlyPeriod` — (2026-06-03)
- [x] Router `/summary` com saldos por pessoa (saldo_alvaro, saldo_alexandra) — (2026-06-03)
- [x] Auditoria completa de backend, frontend, integração e regras de negócio — (2026-06-08)
- [x] Corrigir bugs críticos/médios/baixos identificados na auditoria — (2026-06-08)
- [x] Despesas agendadas: migration 014 + model/schema/router `/scheduled` + `services/scheduled.py` (materialize na virada e na auto-criação do período) — (2026-06-19)
- [ ] Integrar Supabase Auth (trocar `get_user_id()` por JWT real)
- [ ] Rodar migration 014 (scheduled_expenses) no Supabase
- [ ] Testes unitários do serviço de turnover (edge cases: sem period aberto, mês 12→1)
- [ ] Endpoint `GET /periods` para listar histórico de todos os meses
- [ ] Remover `summaryApi` de `api.js` e o endpoint `/summary` do backend (dead code)
- [x] Saldo anterior de novos períodos vem zerado por padrão no turnover/auto-criação — (2026-06-22)
- [x] Suporte para salvar carryover_balance e additional_income no PATCH `/periods/{id}/income` — (2026-06-22)

## 🎨 Frontend

- [x] App.vue + router (Dashboard e Templates views) — (2026-06-03)
- [x] Layout: AppHeader, BottomNav — (2026-06-03)
- [x] BalanceSummary: painel escuro com salário editável, carryover, livre — (2026-06-03)
- [x] ExpenseCard (mobile) com edição de valor e toggle pago — (2026-06-03)
- [x] ExpenseTable (desktop) com edição inline — (2026-06-03)
- [x] RentModal: breakdown base + água + gás + extras com total live — (2026-06-03)
- [x] RentItemsEditor.vue: editor reutilizável de rent_items (fixo/variável/parcela) — (2026-06-05)
- [x] TemplatesView: editor de componentes de aluguel inline no formulário — (2026-06-05)
- [x] Turnover inteligente: variáveis → amount=0, parcelas dentro do rent → incrementa/expira — (2026-06-05)
- [x] TurnoverModal: preview de carryover e confirmação — (2026-06-03)
- [x] BaseModal: slide-up mobile / centered desktop — (2026-06-03)
- [x] TemplatesView: CRUD de recorrências — (2026-06-03)
- [x] Store Pinia com optimistic update no toggle-paid — (2026-06-03)
- [x] Navegação de meses no AppHeader (`< Junho 2026 >`) — (2026-06-03)
- [x] BalanceSummary: abas Visão Geral / Álvaro / Alexandra com saldos individuais — (2026-06-03)
- [x] Sub-componentes `IncomeRow` e `FreeCashDisplay` — (2026-06-03)
- [x] DashboardView: formulário de adição com `responsavel`, modo read-only, estado "mês não criado" — (2026-06-03)
- [x] ExpenseCard: badge de titularidade (azul/rosa/cinza) — (2026-06-03)
- [x] TemplatesView: campo `responsavel` no formulário de criação — (2026-06-03)
- [x] Stripe Design System, responsividade e Dark/Light Mode completo — (2026-06-03)
- [x] Testar fluxo completo no browser (mobile e desktop) — (2026-06-03)
- [x] Deleção de despesas mensais no Check-in (Mobile e Desktop) com modal de confirmação — (2026-06-03)
- [ ] Feedback visual (toast) após salvar / virar mês
- [ ] Swipe-to-delete nos cards mobile (UX extra)
- [x] PWA: criar ícones reais (192px e 512px) — (2026-06-03)
- [x] Tela de Ajustes unificada com customização reativa de nomes e edição de salários do mês ativo — (2026-06-03)
- [x] Inverter layout do card de recorrências, colocando nome no topo e badge de tipo na linha inferior para evitar corte no mobile — (2026-06-03)
- [x] Reordenar navegação no desktop e mobile, agrupando Dados (Check-in/Estatísticas) e Planejamento (Recorrências/Ajustes) — (2026-06-03)
- [x] Ocultar FAB no mobile na rota de Ajustes e adicionar botão '+ Categoria' ao lado do cabeçalho de Categorias — (2026-06-03)
- [x] Ajustar espaçamento acima da Virada de Mês no mobile para reduzir o espaço sob a Caixinha — (2026-06-06)
- [x] Corrigir fluxo de edição de categorias no mobile abrindo o modal dinamicamente — (2026-06-06)
- [x] Corrigir carregamento de categorias no login/início garantindo sincronia com a autenticação e recarregamento redundante nos componentes — (2026-06-08)
- [x] Ocultar botões de ações na Dashboard em dropdown de 3 pontinhos e abrir modal de visualização detalhada da despesa no clique do card/linha — (2026-06-08)
- [x] Corrigir suporte a safe areas (notch/câmera e barra de status superior) no iOS no cabeçalho e modais em tela cheia — (2026-06-08)
- [x] Adicionar gesto Pull-to-refresh no mobile para recarregar o mês atual de forma rápida sem precisar fechar e reabrir o app — (2026-06-08)
- [x] Botão de modo privacidade (ícone olho) no AppHeader para mascarar todos os valores monetários — (2026-06-08)
- [x] Despesas agendadas para mês futuro: store `scheduled.js` + seletor "Lançar em" no modal + seção sanfona "Agendadas" no dashboard — (2026-06-19)
- [x] Exibir Saldo anterior e Valor adicional editáveis no BalanceSummary — (2026-06-22)
- [x] Edição inline de rendas, carryover, adicionais e despesas com botão check animado e cancelamento no blur — (2026-06-22)
- [x] Correção de consistência: carryover anterior não é mais herdado automaticamente para evitar valores incorretos — (2026-06-22)

## 🔐 Auth

- [ ] Configurar Supabase Auth (email/senha ou magic link)
- [ ] Página de login
- [ ] Proteger rotas do frontend (router guards)
- [ ] Row Level Security (RLS) no Supabase para isolar dados por usuário

## 🚀 Deploy

- [ ] Deploy backend (Railway / Render / Fly.io)
- [ ] Deploy frontend (Vercel / Netlify)
- [ ] Configurar CORS em produção
- [ ] Variáveis de ambiente de produção

---

## ✨ Polimento de UI/UX (motion)

- [x] Corrigir direção do slide de transição de rota (ordem das abas) — (2026-06-18)
- [x] `prefers-reduced-motion` global no main.css — (2026-06-18)
- [x] Stagger de entrada nos cards de Estatísticas (`.stagger-in`) — (2026-06-18)
- [x] Lista de despesas mobile com TransitionGroup (add/excluir/buscar animados) — (2026-06-18)
- [x] Unificar tokens de easing/duração via CSS vars (`:root` em main.css; todos os componentes migrados) — (2026-06-18)
- [x] Refazer entrada do AuthView: onda neon (`NeonWave.vue` canvas) + cubo, rápida e pulável (toque/auto ~1.7s) — (2026-06-18)
- [x] Entrada cinematográfica: hold 3.2s, cubo com scale+blur+aura+sweep de luz, wordmark com letter-spacing, onda com ramp de amplitude — (2026-06-19)
- [x] Sanfonas (Empréstimos + Agendadas) sempre iniciam fechadas no dashboard — (2026-06-19)
- [ ] Aplicar TransitionGroup também na ExpenseTable (desktop) para paridade

## 🐞 Bugs corrigidos

- [x] Edição inline de valor de dívida não salvava (passava número cru ao PATCH que espera objeto) — (2026-06-18)
- [x] "Poder de Quitação" sempre 100% / payoff NaN — gamificação lia `.amount` em vez de `.estimated_amount` — (2026-06-18)
- [x] Caixinha contada várias vezes (double-count) na cobertura por dívida — agora alocação snowball (foco primeiro, transbordo) — (2026-06-18)
- [x] Dívidas quitadas viravam "foco" (saldo 0) e `me_deve` poluía total/cobertura — board agora separa pagáveis / recebíveis / quitadas — (2026-06-18)
- [x] Ícones de categoria não apareciam no dashboard ao entrar (só após Configurações) — dedupe de fetch + await no mount + skeleton — (2026-06-19)
- [x] Campo "Categoria (opcional)" quebrava em 2 linhas e desalinhava — campos empilhados com micro-rótulos — (2026-06-19)

## 🔮 Motor de quitação

- [x] Campo `interest_rate` (% a.m.) por dívida — migration 013 + model/schema/router + LoanModal — (2026-06-18)
- [x] `PayoffPlan.vue` — estratégia Bola de Neve vs Avalanche, aporte ajustável, data-livre projetada, comparação de economia e timeline de ataque — (2026-06-18)
- [x] `usePayoffPlan.js` — simulação mês a mês com juros compostos + comparação de estratégias — (2026-06-18)
- [ ] Ação "Quitar com a caixinha" (vincula vault ↔ debt_payment atomicamente)
- [ ] Burn-down chart por dívida (usa DebtPayment + original_amount)
- [ ] Plugar API Claude real no "Auditor IA" (hoje mock em useGamification)
- [ ] Rodar migration 013 no Supabase

## 💡 Backlog / Ideias futuras

- [ ] Histórico de meses anteriores (view de retrospectiva)
- [ ] Gráfico de evolução do saldo livre mês a mês
- [ ] Categorias customizáveis com ícones
- [ ] Export para PDF do check-in mensal
- [ ] Modo multiusuário / compartilhamento de budget (ex: casal)
- [ ] Notificação push no início do mês lembrando do check-in

---
<!-- Adicionar novas tarefas nas seções acima -->

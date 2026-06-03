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
- [ ] Rodar migrations 001 e 002 no Supabase
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
- [ ] Integrar Supabase Auth (trocar `get_user_id()` por JWT real)
- [ ] Testes unitários do serviço de turnover (edge cases: sem period aberto, mês 12→1)
- [ ] Endpoint `GET /periods` para listar histórico de todos os meses

## 🎨 Frontend

- [x] App.vue + router (Dashboard e Templates views) — (2026-06-03)
- [x] Layout: AppHeader, BottomNav — (2026-06-03)
- [x] BalanceSummary: painel escuro com salário editável, carryover, livre — (2026-06-03)
- [x] ExpenseCard (mobile) com edição de valor e toggle pago — (2026-06-03)
- [x] ExpenseTable (desktop) com edição inline — (2026-06-03)
- [x] RentModal: breakdown base + água + gás + extras com total live — (2026-06-03)
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

## 💡 Backlog / Ideias futuras

- [ ] Histórico de meses anteriores (view de retrospectiva)
- [ ] Gráfico de evolução do saldo livre mês a mês
- [ ] Categorias customizáveis com ícones
- [ ] Export para PDF do check-in mensal
- [ ] Modo multiusuário / compartilhamento de budget (ex: casal)
- [ ] Notificação push no início do mês lembrando do check-in

---
<!-- Adicionar novas tarefas nas seções acima -->

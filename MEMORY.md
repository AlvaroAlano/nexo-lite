# MEMORY — Nexo Lite

Log resumido de mudanças, decisões arquiteturais e ajustes relevantes.
Entradas em ordem cronológica inversa (mais recente no topo).

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

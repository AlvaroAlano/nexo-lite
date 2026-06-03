# CLAUDE.md — Nexo Lite

Regras para o Claude Code neste projeto. Leia antes de qualquer tarefa.

---

## 1. Economia de tokens — regra principal

- **Respostas curtas por padrão.** Uma linha por atualização de status. Sem narrativa de processo.
- **Não resumir o que já foi feito** ao final de cada resposta — o diff fala por si.
- **Não repetir contexto** que já está na conversa ou nos arquivos.
- **Não explicar código óbvio.** Só comentar o *porquê* quando for não-óbvio.
- **Não criar docstrings multi-linha** — uma linha curta no máximo, só se necessário.
- **Editar arquivos, não reescrever.** Usar `Edit` para mudanças pontuais, não `Write` em arquivo completo desnecessariamente.
- **Ler só o necessário.** Antes de ler um arquivo inteiro, tentar `grep` ou leitura parcial com `offset/limit`.
- **Não perguntar o óbvio.** Se a tarefa é clara, executar. Perguntar só quando há ambiguidade real que impede o trabalho.
- **Sem listas de "o que foi feito"** após implementar — só dizer o que mudou e qual próximo passo, se houver.

---

## 2. Documentação obrigatória (pós-sessão)

### MEMORY.md
- Entrada datada (`## YYYY-MM-DD — Título`) com bullets curtos: o quê + por quê.
- Ordem inversa (mais recente no topo). Não detalhar código.

### TODO.md
- `[x] tarefa — (YYYY-MM-DD)` ao concluir. `[~]` ao iniciar. `[ ]` ao identificar.
- Nunca remover tarefas concluídas.

---

## 3. Migrações de banco

- Todo SQL que altera schema → `supabase/migrations/NNN_descricao.sql` (sequencial, zero-padded).
- Cabeçalho obrigatório: número, título, data, onde rodar.
- Nunca editar migration existente — criar nova.

---

## 4. Stack — não alterar sem acordo

| Camada   | Tecnologia                                 |
|----------|--------------------------------------------|
| Frontend | Vue 3 (Composition API) + Pinia + Tailwind |
| Backend  | FastAPI + SQLAlchemy async + Pydantic v2   |
| Banco    | Supabase (PostgreSQL via psycopg[binary])  |
| HTTP     | Axios                                      |

- Sem libs de UI (Vuetify, PrimeVue, etc.) — tudo em Tailwind.
- **Nunca usar `confirm()`, `alert()` ou `prompt()` nativos do browser.** Sempre usar `ConfirmModal` (para confirmações) ou `BaseModal` (para qualquer outro diálogo).
- **Antes de criar qualquer elemento de UI, consultar `COMPONENTS.md`.** Se o componente já existe, usar. Se é novo e reutilizável, criar em `src/components/ui/` e documentar no `COMPONENTS.md`.

---

## 5. Design system

- **Paleta:** Slate + Emerald (positivo) + Red (negativo) + Amber (warning). Sem neon.
- **Tipografia:** Inter + `font-mono tabular` para valores monetários.
- **Bordas:** `rounded-xl` ou `rounded-2xl`. Nunca `rounded-full` em containers.
- Mobile-first. Testar em 375px antes de declarar pronto.
- **Modais Híbridos (Mobile):** Formulários e listas longas (ex: `RentModal`, `TurnoverModal`) usam `full-screen-on-mobile` (tela cheia com slide-up); alertas e confirmações (ex: `ConfirmModal`) ou pickers simples flutuam centrados com `backdrop-blur`.

---

## 6. Regras de negócio — nunca quebrar

**Carryover:** `max(0, income_alvaro + income_alexandra + carryover_anterior - Σ expenses.amount)`

**Aluguel (rent):** `amount` = soma automática dos componentes. Nunca editar `amount` direto — sempre via `PATCH /expenses/{id}/rent`.

**Parcelas:** contador `installment_paid` fica em `expense_templates`. Se `paid >= total` → não clonar no turnover.

**Saldos por pessoa:**
- `saldo_alvaro = income_alvaro - Σ(expenses onde responsavel='alvaro')`
- `saldo_alexandra = income_alexandra - Σ(expenses onde responsavel='alexandra')`
- Despesas `conjunto` só reduzem o saldo total.

**safe_decimal:** todo valor monetário no backend passa por `safe_decimal()`. No frontend, `parseFloat() || 0` sempre.

---

## 7. Auth (estado atual)

- Demo user fixo: `00000000-0000-0000-0000-000000000001`.
- `get_user_id()` em `routers/periods.py` e `routers/templates.py` — único ponto de troca para auth real.

---

## 8. Convenções de código

- Python: snake_case, type hints obrigatórios.
- Vue/JS: camelCase (vars), PascalCase (componentes), kebab-case (nomes de arquivo).
- SQL: UPPER CASE palavras reservadas, snake_case colunas/tabelas.
- **Arquivos .bat: ASCII puro (0-127).** CMD lê .bat em ANSI — UTF-8 vira lixo executável.
- YAGNI: sem abstrações prematuras, sem error handling para casos impossíveis.

---

## 9. Fluxo de trabalho

1. Ler `TODO.md` + `MEMORY.md` para contexto.
2. Executar a tarefa.
3. SQL alterado → migration numerada.
4. Atualizar `TODO.md` e `MEMORY.md`.

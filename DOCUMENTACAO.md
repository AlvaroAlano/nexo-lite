# Nexo Lite — Sistema de Check-in Financeiro de Casal

O **Nexo Lite** é um sistema simplificado de check-in financeiro mensal projetado especificamente para casais (Álvaro & Alexandra) gerenciarem seus orçamentos de maneira clara, ágil e visualmente deslumbrante.

---

## 🎯 Proposta de Valor & Dor Resolvida

Diferente de gerenciadores financeiros complexos baseados em fluxo de caixa diário ou planilhas pesadas, o **Nexo Lite** atua como um **Check-in Mensal**. 

- **A Dor**: Casais frequentemente enfrentam atrito ao tentar conciliar contas conjuntas com rendas e gastos individuais. O controle detalhado de cada centavo consome tempo e desestimula a organização.
- **A Solução**: Um fechamento focado no saldo livre remanescente. O casal define as rendas individuais, adiciona despesas fixas, variáveis, parceladas ou conjuntas, e acompanha em tempo real o "saldão" de cada parceiro e o saldo conjunto da casa. A transição de mês (virada) é automatizada, herdando templates e carregando o saldo positivo (*carryover*) sem complicação.

---

## 🛠️ Tecnologias Utilizadas

A stack foi projetada para ser ágil, moderna e de fácil execução local ou em produção.

- **Backend**:
  - [FastAPI](https://fastapi.tiangolo.com/) (Python) para uma API RESTful de alta performance e baixo overhead.
  - [SQLAlchemy](https://www.sqlalchemy.org/) como ORM.
  - [PostgreSQL](https://www.postgresql.org/) (Supabase) como banco de dados principal.
  - [Pydantic v2](https://docs.pydantic.dev/) para serialização e validações robustas com tratamento numérico seguro (`safe_decimal`).
- **Frontend**:
  - [Vue 3](https://vuejs.org/) (Composition API) com Vite.
  - [Pinia](https://pinia.vuejs.org/) para gerenciamento de estado global reativo.
  - [Tailwind CSS](https://tailwindcss.com/) com um design system inspirado na arquitetura de confiança da Stripe, suporte total a **Dark Mode** e layouts mobile-first responsivos.
  - [Lucide Icons](https://lucide.dev/) (`lucide-vue-next`) para ícones de interface limpos e lineares.
- **Funcionalidades PWA (Progressive Web App)**:
  - Service Workers ativos para cache de recursos estáticos.
  - Totalmente instalável e funcional offline para operações locais básicas.
- **Automação de Setup**:
  - Scripts de terminal Windows (.bat) em puro ASCII (`setup.bat` para instalação rápida de dependências e `start.bat` para inicialização paralela de servidores frontend e backend).

---

## 📱 Fluxo de Funcionamento & Detalhamento das Telas

O Nexo Lite é estruturado em quatro telas principais, acessíveis via um menu de navegação responsivo (Bottom Navigation no mobile, Sidebar/Header no desktop).

```
Check-in (Dashboard) ──► Estatísticas (Summary) ──► FAB (+) ──► Recorrências (Templates) ──► Ajustes (Settings)
```

### 1. Cabeçalho & Controle Temporal (`AppHeader.vue`)
- **Seletor de Períodos**: No formato `< Mês Ano >`. Permite navegar no histórico de meses.
  - Clicar nas setas permite consultar períodos passados (somente leitura) ou criar novos períodos no futuro.
  - Clicar no nome do período atual redireciona o usuário instantaneamente para o mês do calendário real vigente.
- **Toggle de Dark Mode**: Botão minimalista no topo para alternar instantaneamente os temas Claro e Escuro, persistido no navegador.

### 2. Check-in Financeiro (`DashboardView.vue`)
O painel central do mês corrente exibe o resumo financeiro atualizado em tempo real.
- **Painel de Resumo (`BalanceSummary.vue`)**:
  - **Três Abas de Visão**: Permite filtrar os saldos entre *Visão Geral* (saldos e despesas consolidados), *Álvaro* e *Alexandra* (dados individuais).
  - **IncomeRow**: Renda declarada de cada cônjuge para o mês ativo.
  - **Carryover Display**: Exibe o saldo positivo trazido do mês anterior (não propaga saldo negativo).
  - **FreeCashDisplay**: Indica o saldo livre de Álvaro/Alexandra ou o total da casa, calculados dinamicamente.
- **Lista de Despesas**:
  - **Mobile (`ExpenseCard.vue`)**: Visualização em formato de cards empilhados. O nome da despesa e categoria aparecem em destaque, com um botão switch para marcar como pago e valor editável.
  - **Desktop (`ExpenseTable.vue`)**: Exibição em tabela. Revela botão de exclusão no hover da linha, edição rápida de valores via clique no campo e badges de titularidade.
  - **Modal de Aluguel (`RentModal.vue`)**: Permite destrinchar o boleto de aluguel em parcelas dinâmicas como condomínio, água, gás, aluguel base e taxas. Os itens são editáveis inline no modal e o valor total se propaga automaticamente.
- **Motor de Virada de Mês (`TurnoverModal.vue`)**:
  - Botão principal visível no Dashboard ("Virar o Mês") que abre um modal com o preview do carryover que será carregado. Ao confirmar, o período atual fecha e as despesas recorrentes do novo período são geradas.

### 3. Recorrências (`TemplatesView.vue`)
Área de planejamento para gerenciar despesas que se repetem todos os meses.
- **Tipos de Recorrência**:
  - **Fixa**: Valor idêntico copiado todos os meses.
  - **Variável**: Entra zerada para preenchimento manual durante o check-in.
  - **Parcelada (Installment)**: Copia a despesa incrementando o contador (ex: `1/12`). Expira automaticamente quando atinge o limite configurado (`installment_total`).
  - **Aluguel (Rent)**: Estrutura base de aluguel que inicia o mês zerada para preenchimento de faturas de água/gás flutuantes.
- **Layout Inteligente**: Cards redesenhados para o mobile para exibir o nome da despesa em largura total no topo, com a categoria e badge de tipo na linha inferior para evitar corte de texto.

### 4. Ajustes (`SettingsView.vue`)
O painel de configurações central do sistema.
- **Customização de Nomes**:
  - Campos para alterar os nomes de Álvaro e Alexandra. As mudanças refletem instantaneamente em todas as telas, badges de despesas, abas do resumo financeiro e modais. Os nomes são mantidos no `localStorage` do frontend.
- **Edição de Salários Ativos**:
  - Campos rápidos integrados ao `CurrencyInput` que atualizam em tempo real a renda do cônjuge correspondente no banco de dados para o mês ativo selecionado.
- **Gerenciamento de Categorias**:
  - Lista de categorias disponíveis. Cada categoria tem um nome, uma cor da paleta Stripe (12 opções) e um ícone Lucide representativo (30 opções).
  - Formulário para criar novas categorias e excluir as antigas com modal de confirmação.
  - Botão "+ Categoria" compacto e prático posicionado estrategicamente ao lado do título da seção no cabeçalho de Ajustes.

---

## ⚖️ Regras de Negócio (RN) Consolidadas

Para garantir a consistência matemática do Nexo Lite, as seguintes regras são aplicadas rigorosamente:

1. **RN-01 (Banco de Dados Inicial Vazio)**: O sistema começa zerado. Nenhum dado é gerado automaticamente além da virada comandada pelo usuário ou importação direta.
2. **RN-02 (Titularidade)**: Despesas e templates pertencem a `alvaro`, `alexandra` ou `conjunto`. Filtros de visualização e cálculos de saldos individuais dependem dessa classificação.
3. **RN-03 (Fórmula de Saldo)**: 
   - Saldo Álvaro = `income_alvaro − Σ(despesas 'alvaro')`
   - Saldo Alexandra = `income_alexandra − Σ(despesas 'alexandra')`
   - Saldo Total = `(income_alvaro + income_alexandra) + carryover − Σ(todas as despesas)`
4. **RN-04 (Carryover/Saldo Rolado)**: O carryover trazido de um mês fechado para um mês novo é dado por `max(0, saldo_total)`. Déficits (saldos negativos) nunca são propagados para o mês seguinte.
5. **RN-05 (Navegação de Períodos)**: Meses passados são definidos como `closed` e tornam-se de leitura exclusiva (formulários e inputs ocultos/desabilitados). Meses futuros inexistentes oferecem botão para iniciar a virada de mês.
6. **RN-06 (Motor de Virada de Mês)**: Ao virar o período: fecha o mês atual, calcula o carryover, gera o novo registro de mês e clona os templates de despesas (incrementando parcelas ou preparando o aluguel).
7. **RN-07 (Aluguel Variável)**: O total do aluguel (`amount`) é sempre a soma de seus componentes secundários em formato JSONB (`rent_base + water + gas + extras`). Ele nunca é editado manualmente de forma direta.
8. **RN-08 (Prevenção de Quebras Numéricas)**: Toda entrada numérica no frontend usa fallbacks `|| 0` e no backend passa pela função `safe_decimal()` para impedir bugs de arredondamento de float (`NaN` ou erros de banco de dados).
9. **RN-09 (Parcelamentos)**: Templates de parcelamento registram o número total de parcelas. Quando clonados pelo motor de virada, são incrementados em 1 unidade. Quando `installment_paid` atinge `installment_total`, o template é desativado para os períodos subsequentes.
10. **RN-10 (Modo Somente Leitura)**: Interface desabilita todos os botões de ação e inputs de texto, exibindo um aviso de visualização histórica quando o período do mês é classificado com status `'closed'`.

---

## 🎨 Biblioteca de Componentes e Design System
O visual da aplicação segue à risca o Stripe Design System documentado em [design_system.md](file:///d:/Finan%C3%A7as%20-%20Saas/nexo-lite/design_system.md) e faz uso dos componentes utilitários padrão em [COMPONENTS.md](file:///d:/Finan%C3%A7as%20-%20Saas/nexo-lite/COMPONENTS.md):
- **AppSelect.vue**: Select customizado com chevron.
- **CurrencyInput.vue**: Input com formatação financeira `pt-BR` em tempo real.
- **ConfirmModal.vue**: Substitui caixas de diálogo nativas do navegador por modais sofisticados e com blur.
- **BaseModal.vue**: Modal responsivo com bloqueio de scroll de background.

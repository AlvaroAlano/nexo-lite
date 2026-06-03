# Nexo Lite — Design System (Stripe-Inspired Architecture of Trust)

Este documento estabelece as regras e tokens de design visual aplicados ao front-end do Nexo Lite, inspirados na arquitetura de confiança e estética editorial do Stripe.

---

## 1. Cores e Temas (Paleta de Cores)

O sistema suporta nativamente **Light Mode** e **Dark Mode** via classe `dark` aplicada ao elemento HTML.

### Ação Principal (Indigo)
- **Primary (Padrão):** `#533afd` (Tailwind custom `indigo-brand-500`)
- **Hover/Pressed:** `#2e2b8c` (Tailwind custom `indigo-brand-700`)
- **Fundo Suave (Highlight/Secondary/Soft):** `#b9b9f9` (Tailwind custom `indigo-brand-200`)

### Light Mode
- **Canvas Principal (Fundo):** `#ffffff` (White)
- **Canvas Soft (Destaque/Secundário):** `#f6f9fc` (Tailwind custom `slate-brand-canvas-soft`)
- **Textos:**
  - **Navy Ink (Principal):** `#0d253d` (Texto principal - nunca preto puro)
  - **Ink Mute (Secundário/Legendas):** `#64748d` (Texto secundário)
- **Bordas:**
  - **Hairline:** `#e3e8ee` (Bordas ultra-finas e discretas)

### Dark Mode (Dashboard / Dark App)
- **Canvas Principal (Fundo):** `#1c1e54` (Azul marinho extremamente profundo)
- **Canvas Soft (Destaque/Secundário):** `#12143d` (Contraste ligeiramente mais escuro)
- **Textos:**
  - **On Primary (Principal/Secundário):** `#ffffff` (Branco puro)
  - **On Primary Mute (Legendas):** `#a5b4fc` (Azul indigo suave)
- **Bordas:**
  - **Dark Hairline:** `#2c2e64` (Bordas escuras e discretas)

---

## 2. Tipografia

### Fonte Principal
- **Família:** `Inter` (Google Fonts)
- **Pesos:**
  - **Títulos/Headings:** Peso `300` (Light) para uma aparência refinada e editorial.
  - **Apoio/Botões/Texto Geral:** Peso `400` (Regular) para legibilidade.
  - **Labels/Semibold:** Peso `500`/`600` permitidos apenas para pequenos marcadores ou semântica secundária.

### Tracking (Espaçamento de Letras)
- Títulos exigem espaçamento negativo de letras para manter o apelo editorial e evitar que fiquem muito espalhados:
  - **Títulos Grandes (ex: Hero/Saldos):** `letter-spacing: -1.4px`
  - **Títulos de Cards/Subseções:** `letter-spacing: -0.2px` a `-0.6px`

### Sinalização Financeira (Tabular Figures)
- **Financial Signal (Global):** Todos os componentes pai do painel ou tabelas financeiras devem ter a classe utilitária de funcionalidade de fonte `font-feature-settings: "ss01"` ativada.
- **Tabular Figures (CRÍTICO):** Qualquer célula, card ou linha que exiba dinheiro, saldo, parcelas ou numerais deve ter obrigatoriamente:
  - `font-feature-settings: "tnum"`
  - `letter-spacing: -0.42px`
  - Isso garante que os números fiquem perfeitamente alinhados verticalmente nas colunas e listas de transações.

---

## 3. Formas, Bordas e Sombras

### Arredondamento (Border Radius)
- **Botões de Ação:** Formato pílula estrito (`rounded-full` / `9999px`), curtos e transacionais.
- **Cards de Conteúdo/Despesas:** Bordas de `12px` (`rounded-xl` / `rounded-lg`).
- **Inputs/Formulários/Campos de Texto:** Arredondamento menor de `6px` (`rounded-md` / `rounded-sm`).

### Padding Padrão
- **Botões padrão:** `8px 16px` (`py-2 px-4`).

### Sombras (Elevations)
O design é limpo e evita sombras excessivas:
- **Nível 1 (Cards sobre fundo branco):** `box-shadow: rgba(0, 55, 112, 0.08) 0px 1px 3px`
- **Nível 2 (Modais flutuantes/Dropdowns):** `box-shadow: rgba(0, 55, 112, 0.08) 0px 8px 24px, rgba(0, 55, 112, 0.04) 0px 2px 6px`

---

## 4. Responsividade e Mobile-First

### Áreas de Toque (Touch Targets)
- Em telas **Mobile** (`< 768px`), os botões de pílula e campos de formulário devem aumentar seus paddings/alturas para garantir uma área de toque mínima de **40px a 44px** de altura, facilitando a interação por toque sem erros.

### Comportamento do Layout (Grids)
- A visualização de grids de despesas e templates deve se adaptar dinamicamente ao viewport:
  - **Desktop (>= 1024px):** 3 ou 4 colunas.
  - **Tablet (>= 768px e < 1024px):** 2 colunas.
  - **Mobile (< 768px):** 1 coluna empilhada verticalmente.

### Tipografia Responsiva
- Títulos de grande impacto visual devem escalar conforme o dispositivo:
  - **Desktop:** `text-5xl` (ou ~56px).
  - **Mobile:** `text-3xl` (ou ~36px).

### Comportamento Híbrido de Modais (CRÍTICO)
Para garantir usabilidade máxima no mobile e evitar problemas de clipping e sobreposição do teclado virtual:
- **Modais Complexos / Formulários / Listas Longas (ex: `RentModal`, `TurnoverModal`):** Devem se tornar **tela inteira no mobile** (`full-screen-on-mobile`). Eles deslizam de baixo para cima (slide-up) ocupando 100% da viewport, com rodapé fixo e área segura para o teclado.
- **Confirmações Rápidas / Alertas / Pickers Simples (ex: `ConfirmModal`, `CategoryPicker`):** Devem permanecer como **diálogos centralizados flutuantes** com fundo fosco/translúcido (`backdrop-blur`).

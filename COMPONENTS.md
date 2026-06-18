# COMPONENTS.md — Nexo Lite UI Library

Referência dos componentes reutilizáveis do sistema.
**Regra:** antes de criar qualquer elemento de UI novo, verifique se já existe um componente aqui.

---

## Estrutura de pastas

```
src/components/
  ui/          ← Design system (primitivos reutilizáveis em qualquer tela)
  layout/      ← Estrutura da página (header, nav)
  dashboard/   ← Componentes específicos do check-in mensal
  modals/      ← Janelas modais de domínio
```

---

## `ui/` — Design System

### `BaseModal.vue`
Modal universal com suporte a comportamento híbrido no mobile.
- `title` — título exibido no header
- `full-screen-on-mobile` (Boolean, default `false`) — se `true`, transforma o modal em tela cheia no mobile (com slide-up completo da base e rodapé fixo). Recomendado para formulários e listas longas. Se `false`, o modal flutua no centro da tela.
```vue
<BaseModal v-model="show" title="Título" full-screen-on-mobile>
  Conteúdo aqui
  <template #footer>
    <button>Ação</button>
  </template>
</BaseModal>
```

---

### `AppSelect.vue`
Select estilizado no padrão do sistema (rounded-xl, seta customizada Lucide, sem aparência nativa do browser).
```vue
<AppSelect v-model="value">
  <option value="a">Opção A</option>
  <option value="b">Opção B</option>
</AppSelect>
```

---

### `CurrencyInput.vue`
Input monetário com máscara em tempo real (pt-BR). Digitar `12345` exibe `123,45`.
- `v-model` recebe e emite `Number`
- Emite `@confirm` (Enter) e `@cancel` (Escape)
- Prop `hide-prefix` remove o `R$` (use em inputs inline)
- Prop `input-class` para estilização do input interno
```vue
<CurrencyInput v-model="amount" input-class="w-full py-3 border ..." />
<CurrencyInput v-model="amount" hide-prefix input-class="..." />
```

---

### `ConfirmModal.vue`
Modal de confirmação para ações destrutivas. **Substitui `confirm()` nativo do browser.**
- `title` — título da modal
- `message` — texto descritivo da ação
- `confirm-label` / `cancel-label` — textos dos botões (default: "Confirmar" / "Cancelar")
- `variant` — `'danger'` (botão vermelho, padrão) ou `'default'` (botão slate)
- Emite `@confirm` quando o usuário confirma
```vue
<ConfirmModal
  v-model="showDelete"
  title="Remover item"
  message="Tem certeza? Esta ação não pode ser desfeita."
  confirm-label="Remover"
  @confirm="doDelete"
/>
```

---

### `AppSelect.vue`
Select estilizado no padrão do sistema (rounded-xl, seta ChevronDown Lucide, `appearance-none`).
**Substitui `<select>` nativo.** Aceita `<option>` como slot.
```vue
<AppSelect v-model="value">
  <option value="a">Opção A</option>
</AppSelect>
```

---

### `NeonWave.vue`
Onda neon animada em `<canvas>` 2D (sem dependências). Núcleo branco com fade nas pontas + cópias índigo/esmeralda deslocadas (aberração cromática) e brilho aditivo. Preenche o container pai (`w-full h-full`). Respeita `prefers-reduced-motion` (renderiza quadro estático). Usado na entrada do `AuthView`.
```vue
<div class="relative h-48"><NeonWave /></div>
```

---

### `CategoryPicker.vue`
Dropdown de seleção de categoria com ícone Lucide + cor da paleta.
- `v-model` recebe e emite o `id` (UUID string) da categoria
- Fecha ao clicar fora
```vue
<CategoryPicker v-model="form.category_id" />
```

---

## `layout/`

### `AppHeader.vue`
Header fixo com navegação de meses (`< Junho 2026 >`), links desktop e indicador de salvamento.

### `BottomNav.vue`
Navegação inferior mobile com 3 abas: Check-in, Recorrências, Categorias.

---

## `modals/`

### `BaseModal.vue`
Base já documentada em `ui/` — use sempre como wrapper de qualquer modal novo.

### `RentModal.vue`
Modal de composição do boleto de aluguel com itens dinâmicos (JSONB).

### `TurnoverModal.vue`
Modal de confirmação de virada de mês com preview de carryover.

---

## Design Tokens

### Paleta de cores
| Uso               | Classe Tailwind          |
|-------------------|--------------------------|
| Fundo app         | `bg-slate-50`            |
| Card / surface    | `bg-white`               |
| Borda padrão      | `border-slate-200`       |
| Texto primário    | `text-slate-900`         |
| Texto secundário  | `text-slate-500`         |
| Positivo / pago   | `text-emerald-500`       |
| Negativo / alerta | `text-red-500`           |
| Focus ring        | `focus:ring-2 focus:ring-slate-200` |

### Bordas
- Containers grandes: `rounded-2xl` (16px)
- Inputs, botões, badges: `rounded-xl` (12px)
- Badges pequenos: `rounded-full`

### Tipografia
- Valores monetários: `font-mono tabular`
- Rótulos de seção: `text-xs font-semibold text-slate-400 uppercase tracking-wide`

### Ícones
Biblioteca: **Lucide** (`lucide-vue-next`)
- `stroke-width="1.5"` para ícones de interface (padrão)
- `stroke-width="2"` para ícones pequenos (badges, inline)
- `stroke-width="2.5"` para ícones de ação (check, close)

### Movimento (tokens em `:root`, ver `assets/main.css`)
Use **sempre** estes tokens em transições/animações — nunca `cubic-bezier(...)` cru.
| Token | Uso |
|-------|-----|
| `var(--ease-out-expo)` | entradas (desaceleração ágil) |
| `var(--ease-in)` | saídas (partida limpa) |
| `var(--ease-in-out)` | loops/pulsos |
| `var(--ease-out-quint)` | menus/dropdowns |
| `var(--ease-spring)` | mola com overshoot (pops/FAB) |
| `var(--ease-spring-soft)` | mola sutil (modal desktop) |
| `var(--ease-sheet)` | bottom sheet iOS |

- Entrada 250–400ms, saída ~60–70% disso. Só `transform`/`opacity`.
- Util `.stagger-in` anima filhos diretos em cascata (até 8).
- `prefers-reduced-motion` é tratado globalmente em `main.css`.

---

## `stats/` — Visualizações de Estatísticas

### `StatCard.vue`
Card wrapper padrão para todos os gráficos da tela de Estatísticas.
- `title` — título do gráfico
- `subtitle` — descrição curta (opcional)
```vue
<StatCard title="Cabo de Guerra" subtitle="Distribuição de carga financeira">
  <WarBar :data="warData" />
</StatCard>
```

---

### `PayoffPlan.vue`
Motor de quitação de dívidas. Lê `useDebtsStore` (dívidas `eu_devo` ativas) + `useVaultStore` (sugestão de aporte). Sem props.
- Seletor de estratégia: **Bola de Neve** (menor saldo primeiro) vs **Avalanche** (maior juro primeiro), com badge dinâmico de economia.
- Aporte mensal ajustável (CurrencyInput + slider + chips), persistido no `localStorage`.
- Projeção: data em que fica livre, meses, juros totais; alerta quando o aporte é menor que os juros mensais.
- Comparação de economia entre estratégias + timeline "ordem de ataque".
- Cálculo em `composables/usePayoffPlan.js` (`simulatePayoff` é função pura, testável).
```vue
<StatCard title="Plano de Quitação" subtitle="...">
  <PayoffPlan />
</StatCard>
```

---

### `WarBar.vue`
Barra horizontal empilhada com 3 segmentos: Álvaro / Alexandra / Conjunto.
- `data` — objeto `{ alvaro, alexandra, conjunto }` cada um com `{ label, amount }`
- Hover nas fatias escurece as demais (opacity)
- Labels acima mostram nome, % e valor monetário proporcionalmente
```vue
<WarBar :data="{ alvaro: { label: 'Álvaro', amount: 3200 }, alexandra: { label: 'Alexandra', amount: 1800 }, conjunto: { label: 'Conjunto', amount: 2400 } }" />
```

---

## Adicionando novos componentes

1. Criar o arquivo em `src/components/ui/`
2. Seguir o padrão: `defineOptions({ inheritAttrs: false })` + `v-bind="$attrs"` quando necessário
3. Documentar aqui no `COMPONENTS.md`
4. Registrar no `MEMORY.md`

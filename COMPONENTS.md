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

---

## Adicionando novos componentes

1. Criar o arquivo em `src/components/ui/`
2. Seguir o padrão: `defineOptions({ inheritAttrs: false })` + `v-bind="$attrs"` quando necessário
3. Documentar aqui no `COMPONENTS.md`
4. Registrar no `MEMORY.md`

# Regras de Negócio — Nexo Lite

Documento de referência das regras de negócio do sistema.
**Não alterar sem discussão.** Qualquer mudança deve ser refletida também no `CLAUDE.md` e registrada no `MEMORY.md`.

---

## RN-01 — Banco de Dados Inicial Vazio

O banco de dados de cada mês **começa zerado** para novos usuários.
Ao fazer a Virada de Mês (Motor de Virada), os templates ativos são clonados para o novo período.
Não existe pré-carregamento automático de dados na primeira abertura do sistema.

---

## RN-02 — Titularidade (responsavel)

Cada despesa e template possui o campo `responsavel` com três valores possíveis:
- `alvaro` — conta exclusiva de Álvaro
- `alexandra` — conta exclusiva de Alexandra
- `conjunto` — conta compartilhada do casal

**Regra de exibição:**
| Aba          | Exibe                                      |
|--------------|--------------------------------------------|
| Visão Geral  | Todas as despesas                          |
| Álvaro       | Apenas `responsavel = 'alvaro'`            |
| Alexandra    | Apenas `responsavel = 'alexandra'`         |

Despesas do tipo `conjunto` aparecem **somente** na aba Visão Geral.

---

## RN-03 — Fórmula de Saldo

```
Saldo Álvaro    = income_alvaro    − Σ(expenses onde responsavel = 'alvaro')
Saldo Alexandra = income_alexandra − Σ(expenses onde responsavel = 'alexandra')
Saldo Total     = (income_alvaro + income_alexandra) + carryover − Σ(todas as expenses)
```

- O Saldo Total é a fonte principal do check-in mensal.
- Saldos individuais servem para auditoria e análise por pessoa.
- Despesas `conjunto` reduzem apenas o Saldo Total, não os individuais.

---

## RN-04 — Carryover (Saldo Rolado)

- O carryover_balance é inicializado como **zero** (`0.00`) na criação de novos períodos (virada ou navegação).
- O usuário preenche manualmente o saldo anterior caso queira rolar sobras ou compensações.
- O carryover é atribuído ao período, sem divisão por pessoa.
- Nunca propagar saldo negativo entre meses.

---

## RN-05 — Navegação de Meses

- O cabeçalho exibe o mês atual com botões `<` (anterior) e `>` (próximo).
- **Meses passados** (status = `'closed'`): somente leitura — nenhuma edição permitida.
- **Mês atual** (status = `'open'`): edição completa.
- **Mês futuro inexistente**: ao navegar para frente, o sistema oferece a opção de criar o próximo mês (aciona o Motor de Virada sob demanda). Não cria meses em branco automaticamente.

---

## RN-06 — Motor de Virada de Mês

Ao acionar a Virada, o sistema:
1. Fecha o período atual (`status = 'closed'`).
2. Calcula o carryover (ver RN-04).
3. Cria o novo período para o mês seguinte.
4. Clona os templates ativos:
   - **`fixed` / `variable`**: copia com `amount = base_amount` e `pago = false`.
   - **`rent`**: copia com `amount = 0` e `rent_base = base_amount` (usuário preenche o breakdown no check-in).
   - **`installment`**: copia com parcela incrementada (`+1`). Se `installment_paid >= installment_total`, o template **expira** e não é clonado.
5. O `responsavel` do template é herdado pela expense clonada.

---

## RN-07 — Aluguel Variável

O card/linha de "Aluguel" possui subcampos:
- `rent_base` — valor base do contrato
- `rent_water` — água
- `rent_gas` — gás
- `rent_extras` — taxas, condomínio, extras

O campo `amount` é **sempre** calculado automaticamente:
```
amount = rent_base + rent_water + rent_gas + rent_extras
```

Nunca editar `amount` diretamente em despesas do tipo `rent`.
No backend, o endpoint `PATCH /expenses/{id}/rent` recalcula `amount` automaticamente.

---

## RN-08 — Prevenção de Quebra de Cálculo

- Todo valor monetário que chega do frontend deve passar por `safe_decimal()` no backend.
- `safe_decimal(None)` retorna `Decimal('0.00')`.
- No frontend, todo `parseFloat()` deve ter `|| 0` como fallback.
- Campos vazios nunca devem resultar em `NaN` ou `undefined` sendo exibidos.

---

## RN-09 — Parcelas (installment)

- O contador de parcelas fica em `expense_templates.installment_paid`.
- `monthly_expenses.installment_current` registra a parcela do mês em questão.
- Ao clonar: `installment_current = installment_paid + 1` (após incremento).
- Se `installment_paid >= installment_total` → template expira, não é clonado.
- Exemplo: template com `installment_total = 5` e `installment_paid = 4` → último clone com `current = 5`; no próximo mês, não clona mais.

---

## RN-10 — Modo Leitura (Meses Passados)

Quando `period.status === 'closed'`:
- Todos os inputs ficam desabilitados.
- Botões "Pagar", "Editar" e "Adicionar" ficam ocultos ou desabilitados.
- O cabeçalho exibe banner `"Visualização — Mês Fechado"`.
- A operação de Virada de Mês não pode ser acionada.

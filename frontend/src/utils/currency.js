const BRL = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  minimumFractionDigits: 2,
})

/**
 * Format a number or string as BRL currency.
 * Returns "R$ 0,00" for null/undefined/empty to prevent #VALUE! display.
 */
export function formatCurrency(value) {
  const num = parseFloat(value)
  if (isNaN(num)) return 'R$ 0,00'
  return BRL.format(num)
}

/**
 * Parse a user-typed string like "1.234,56" → 1234.56
 */
export function parseCurrency(raw) {
  if (!raw && raw !== 0) return 0
  const cleaned = String(raw)
    .replace(/[R$\s]/g, '')
    .replace(/\./g, '')
    .replace(',', '.')
  const num = parseFloat(cleaned)
  return isNaN(num) ? 0 : num
}

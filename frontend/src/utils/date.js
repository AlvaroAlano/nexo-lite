const MONTHS_PT = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
]

export function monthLabel(year, month) {
  if (!year || !month) return ''
  return `${MONTHS_PT[month - 1]} ${year}`
}

export function monthLabelShort(year, month) {
  if (!year || !month) return ''
  return `${MONTHS_PT[month - 1].slice(0, 3)} ${year}`
}

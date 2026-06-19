import axios from 'axios'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10_000,
  headers: { 'Content-Type': 'application/json' },
})

// ─── Periods ────────────────────────────────────────────────────────────────
export const periodsApi = {
  getCurrent:   () => http.get('/periods/current'),
  getByMonth:   (year, month) => http.get(`/periods/${year}/${month}`),
  updateIncome: (periodId, data) => http.patch(`/periods/${periodId}/income`, data),
  turnover:     () => http.post('/periods/turnover'),
  history:      (limit = 12) => http.get('/periods/history', { params: { limit } }),
}

// ─── Expenses ───────────────────────────────────────────────────────────────
export const expensesApi = {
  create: (periodId, data) => http.post(`/expenses/${periodId}`, data),
  update: (expenseId, data) => http.patch(`/expenses/${expenseId}`, data),
  updateRent: (expenseId, components) => http.patch(`/expenses/${expenseId}/rent`, components),
  togglePaid: (expenseId) => http.patch(`/expenses/${expenseId}/toggle-paid`),
  delete: (expenseId) => http.delete(`/expenses/${expenseId}`),
}

// ─── Templates ──────────────────────────────────────────────────────────────
export const templatesApi = {
  list: () => http.get('/templates/'),
  create: (data) => http.post('/templates/', data),
  update: (id, data) => http.patch(`/templates/${id}`, data),
  delete: (id) => http.delete(`/templates/${id}`),
}

// ─── Categories ─────────────────────────────────────────────────────────────
export const categoriesApi = {
  list: () => http.get('/categories/'),
  create: (data) => http.post('/categories/', data),
  update: (id, data) => http.patch(`/categories/${id}`, data),
  delete: (id) => http.delete(`/categories/${id}`),
}

// ─── Scheduled (Despesas agendadas p/ mês futuro) ────────────────────────────
export const scheduledApi = {
  list:   () => http.get('/scheduled/'),
  create: (data) => http.post('/scheduled/', data),
  delete: (id) => http.delete(`/scheduled/${id}`),
}

// ─── Summary ────────────────────────────────────────────────────────────────
export const summaryApi = {
  get: (periodId) => http.get(`/summary/${periodId}`),
}

// ─── Debts (Dívidas / Empréstimos) ───────────────────────────────────────────
export const debtsApi = {
  list:         ()           => http.get('/debts/'),
  create:       (data)       => http.post('/debts/', data),
  update:       (id, data)   => http.patch(`/debts/${id}`, data),
  settle:       (id)         => http.patch(`/debts/${id}/settle`),
  delete:       (id)         => http.delete(`/debts/${id}`),
  listPayments: (id)         => http.get(`/debts/${id}/payments`),
  addPayment:   (id, data)   => http.post(`/debts/${id}/payments`, data),
}

// ─── Expense Notes ────────────────────────────────────────────────────────────
export const expenseNotesApi = {
  list:   (expenseId)           => http.get(`/expenses/${expenseId}/notes`),
  create: (expenseId, data)     => http.post(`/expenses/${expenseId}/notes`, data),
  delete: (expenseId, noteId)   => http.delete(`/expenses/${expenseId}/notes/${noteId}`),
}

// ─── Vault (Caixinha) ────────────────────────────────────────────────────────
export const vaultApi = {
  getSummary: () => http.get('/vault/summary'),
  reconcile: (realBalance) => http.post('/vault/reconcile', { real_balance: realBalance }),
}

export default http

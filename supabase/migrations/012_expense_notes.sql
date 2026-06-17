-- 012 — Expense notes / observations history
-- 2026-06-17
-- Run in: Supabase SQL Editor

CREATE TABLE IF NOT EXISTS expense_notes (
    id          UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    expense_id  UUID         NOT NULL REFERENCES monthly_expenses(id) ON DELETE CASCADE,
    body        TEXT         NOT NULL,
    created_by  VARCHAR(100) NOT NULL DEFAULT 'Usuário',
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_expense_notes_expense ON expense_notes(expense_id, created_at DESC);

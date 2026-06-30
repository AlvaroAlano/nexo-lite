-- Migration 018: Add is_excluded to monthly_expenses
-- Objetivo: Permitir exclusão temporária de despesas dos cálculos de dashboard (simulação)

ALTER TABLE public.monthly_expenses
ADD COLUMN is_excluded BOOLEAN NOT NULL DEFAULT FALSE;

CREATE INDEX idx_monthly_expenses_is_excluded ON public.monthly_expenses (is_excluded);

-- ============================================================
-- Migration 002 — Add responsavel field + split income per person
-- Project : Nexo Lite
-- Date    : 2026-06-03
-- Depends : 001_initial_schema.sql
-- Run in  : Supabase SQL Editor
-- ============================================================

-- ── 1. Split income on monthly_periods ───────────────────────────────────
ALTER TABLE monthly_periods
    ADD COLUMN IF NOT EXISTS income_alvaro    NUMERIC(12,2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS income_alexandra NUMERIC(12,2) NOT NULL DEFAULT 0;

-- Migrate existing data: assume current income belongs to 'alvaro' (adjust manually if needed)
UPDATE monthly_periods
SET income_alvaro = income
WHERE income_alvaro = 0 AND income > 0;

-- ── 2. Add responsavel to expense_templates ───────────────────────────────
ALTER TABLE expense_templates
    ADD COLUMN IF NOT EXISTS responsavel VARCHAR(20) NOT NULL DEFAULT 'conjunto'
    CHECK (responsavel IN ('alvaro', 'alexandra', 'conjunto'));

-- ── 3. Add responsavel to monthly_expenses ────────────────────────────────
ALTER TABLE monthly_expenses
    ADD COLUMN IF NOT EXISTS responsavel VARCHAR(20) NOT NULL DEFAULT 'conjunto'
    CHECK (responsavel IN ('alvaro', 'alexandra', 'conjunto'));

-- Sync responsavel from template to existing expense rows
UPDATE monthly_expenses me
SET responsavel = et.responsavel
FROM expense_templates et
WHERE me.template_id = et.id;

-- ── 4. Update demo seed data ──────────────────────────────────────────────
DO $$
DECLARE
    demo_user UUID := '00000000-0000-0000-0000-000000000001';
BEGIN
    -- Split demo income: Álvaro 5000, Alexandra 3500
    UPDATE monthly_periods
    SET income_alvaro = 5000.00, income_alexandra = 3500.00
    WHERE user_id = demo_user;

    -- Assign responsavel to demo templates
    UPDATE expense_templates SET responsavel = 'conjunto' WHERE user_id = demo_user AND name IN ('Aluguel', 'Internet', 'Streaming');
    UPDATE expense_templates SET responsavel = 'alvaro'   WHERE user_id = demo_user AND name IN ('Celular', 'Academia');
    UPDATE expense_templates SET responsavel = 'conjunto' WHERE user_id = demo_user AND name = 'Fatura Cartão';

    -- Sync to monthly expenses
    UPDATE monthly_expenses me
    SET responsavel = et.responsavel
    FROM expense_templates et
    WHERE me.template_id = et.id AND me.period_id IN (
        SELECT id FROM monthly_periods WHERE user_id = demo_user
    );
END $$;

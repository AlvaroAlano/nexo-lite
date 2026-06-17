-- 010 — Expand debts for personal loans (direction, dates, status, original_amount)
-- 2026-06-17
-- Run in: Supabase SQL Editor

ALTER TABLE debts
    ADD COLUMN IF NOT EXISTS direction       VARCHAR(20)    NOT NULL DEFAULT 'eu_devo',
    ADD COLUMN IF NOT EXISTS status          VARCHAR(20)    NOT NULL DEFAULT 'ativo',
    ADD COLUMN IF NOT EXISTS original_amount NUMERIC(12, 2),
    ADD COLUMN IF NOT EXISTS loan_date       DATE,
    ADD COLUMN IF NOT EXISTS due_date        DATE;

-- Backfill original_amount from estimated_amount for existing rows
UPDATE debts SET original_amount = estimated_amount WHERE original_amount IS NULL;

-- 016 — Convert additional_income to additional_income_items JSONB
-- 2026-06-22
-- Run in: Supabase SQL Editor

ALTER TABLE monthly_periods
DROP COLUMN IF EXISTS additional_income;

ALTER TABLE monthly_periods
ADD COLUMN IF NOT EXISTS additional_income_items JSONB NOT NULL DEFAULT '[]';

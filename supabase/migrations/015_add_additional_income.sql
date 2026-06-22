-- 015 — Add additional_income to monthly_periods
-- 2026-06-22

ALTER TABLE monthly_periods
ADD COLUMN IF NOT EXISTS additional_income NUMERIC(12, 2) NOT NULL DEFAULT 0;

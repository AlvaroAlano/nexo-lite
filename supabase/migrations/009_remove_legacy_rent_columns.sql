-- 009 — Remove legacy rent breakdown columns from monthly_expenses
-- Date: 2026-06-08
-- Run on: Supabase SQL editor (production) or local psql

ALTER TABLE monthly_expenses
    DROP COLUMN IF EXISTS rent_base,
    DROP COLUMN IF EXISTS rent_water,
    DROP COLUMN IF EXISTS rent_gas,
    DROP COLUMN IF EXISTS rent_extras;

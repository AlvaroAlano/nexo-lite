-- ============================================================
-- Migration 003 — Dynamic rent line items (JSONB)
-- Project : Nexo Lite
-- Date    : 2026-06-03
-- Depends : 002_add_responsavel_and_income_split.sql
-- Run in  : Supabase SQL Editor
-- ============================================================
-- Replaces the 4 hardcoded fields (rent_base/water/gas/extras)
-- with a flexible JSONB array of named line items.
-- Old columns are kept for backward compatibility but ignored by the app.
-- ============================================================

ALTER TABLE monthly_expenses
    ADD COLUMN IF NOT EXISTS rent_items JSONB NOT NULL DEFAULT '[]';

ALTER TABLE expense_templates
    ADD COLUMN IF NOT EXISTS rent_items JSONB NOT NULL DEFAULT '[]';

-- Migrate existing demo data to the new format
UPDATE monthly_expenses
SET rent_items = jsonb_build_array(
    jsonb_build_object(
        'id',     'base-' || id::text,
        'name',   'Aluguel',
        'amount', rent_base,
        'type',   'fixed',
        'installment_current', NULL,
        'installment_total',   NULL
    )
)
WHERE expense_type = 'rent' AND rent_base > 0 AND rent_items = '[]';

-- 011 — Debt payments history table
-- 2026-06-17
-- Run in: Supabase SQL Editor

CREATE TABLE IF NOT EXISTS debt_payments (
    id         UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    debt_id    UUID         NOT NULL REFERENCES debts(id) ON DELETE CASCADE,
    amount     NUMERIC(12, 2) NOT NULL,
    notes      TEXT,
    paid_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_debt_payments_debt ON debt_payments(debt_id, paid_at DESC);

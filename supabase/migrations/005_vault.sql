-- 005 — Vault (Caixinha) reconciliation history
-- 2026-06-04
-- Run in: Supabase SQL Editor

CREATE TABLE IF NOT EXISTS vault_reconciliations (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id      UUID NOT NULL,
    real_balance NUMERIC(12, 2) NOT NULL,
    recorded_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vault_reconciliations_user
    ON vault_reconciliations(user_id, recorded_at DESC);

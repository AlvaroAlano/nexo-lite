-- 006 — Active Debts (Dívidas Ativas)
-- 2026-06-04
-- Run in: Supabase SQL Editor

CREATE TABLE IF NOT EXISTS debts (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id          UUID NOT NULL,
    name             VARCHAR(255) NOT NULL,
    estimated_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    display_order    INTEGER NOT NULL DEFAULT 0,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_debts_user
    ON debts(user_id, display_order);

CREATE TRIGGER trg_debts_updated
    BEFORE UPDATE ON debts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Seed demo
INSERT INTO debts (user_id, name, estimated_amount, display_order)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'Nubank',        9000.00, 1),
    ('00000000-0000-0000-0000-000000000001', 'Banco do Brasil',10000.00, 2),
    ('00000000-0000-0000-0000-000000000001', 'Renner',         2000.00, 3)
ON CONFLICT DO NOTHING;

-- ============================================================
-- Migration 001 — Initial Schema
-- Project : Nexo Lite
-- Date    : 2026-06-03
-- Run in  : Supabase SQL Editor (once, on a fresh database)
-- ============================================================

-- ── Prerequisites ────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Tables ───────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS monthly_periods (
    id                UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id           UUID        NOT NULL,
    year              INTEGER     NOT NULL,
    month             INTEGER     NOT NULL CHECK (month BETWEEN 1 AND 12),
    status            VARCHAR(20) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'closed')),
    income            NUMERIC(12,2) NOT NULL DEFAULT 0,
    carryover_balance NUMERIC(12,2) NOT NULL DEFAULT 0,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, year, month)
);

CREATE TABLE IF NOT EXISTS expense_templates (
    id                UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id           UUID        NOT NULL,
    name              VARCHAR(255) NOT NULL,
    category          VARCHAR(100) NOT NULL DEFAULT 'Outros',
    expense_type      VARCHAR(20)  NOT NULL DEFAULT 'fixed'
                      CHECK (expense_type IN ('fixed', 'variable', 'installment', 'rent')),
    base_amount       NUMERIC(12,2) NOT NULL DEFAULT 0,
    is_active         BOOLEAN     NOT NULL DEFAULT TRUE,
    installment_total INTEGER,
    installment_paid  INTEGER     NOT NULL DEFAULT 0,
    display_order     INTEGER     NOT NULL DEFAULT 0,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS monthly_expenses (
    id                  UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    period_id           UUID        NOT NULL REFERENCES monthly_periods(id) ON DELETE CASCADE,
    template_id         UUID        REFERENCES expense_templates(id) ON DELETE SET NULL,
    name                VARCHAR(255) NOT NULL,
    category            VARCHAR(100) NOT NULL DEFAULT 'Outros',
    expense_type        VARCHAR(20)  NOT NULL DEFAULT 'fixed'
                        CHECK (expense_type IN ('fixed', 'variable', 'installment', 'rent')),
    amount              NUMERIC(12,2) NOT NULL DEFAULT 0,
    is_paid             BOOLEAN     NOT NULL DEFAULT FALSE,
    paid_at             TIMESTAMPTZ,
    installment_current INTEGER,
    installment_total   INTEGER,
    rent_base           NUMERIC(12,2) NOT NULL DEFAULT 0,
    rent_water          NUMERIC(12,2) NOT NULL DEFAULT 0,
    rent_gas            NUMERIC(12,2) NOT NULL DEFAULT 0,
    rent_extras         NUMERIC(12,2) NOT NULL DEFAULT 0,
    display_order       INTEGER     NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Indexes ──────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_monthly_periods_user_status
    ON monthly_periods(user_id, status);

CREATE INDEX IF NOT EXISTS idx_expense_templates_user_active
    ON expense_templates(user_id, is_active);

CREATE INDEX IF NOT EXISTS idx_monthly_expenses_period
    ON monthly_expenses(period_id);

-- ── Auto-update updated_at ────────────────────────────────────

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_monthly_periods_updated') THEN
        CREATE TRIGGER trg_monthly_periods_updated
            BEFORE UPDATE ON monthly_periods
            FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_expense_templates_updated') THEN
        CREATE TRIGGER trg_expense_templates_updated
            BEFORE UPDATE ON expense_templates
            FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_monthly_expenses_updated') THEN
        CREATE TRIGGER trg_monthly_expenses_updated
            BEFORE UPDATE ON monthly_expenses
            FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    END IF;
END $$;

-- ── Demo seed (single user — remove before production) ───────

DO $$
DECLARE
    demo_user  UUID := '00000000-0000-0000-0000-000000000001';
    period_id  UUID;
BEGIN
    -- Current period (June 2026)
    INSERT INTO monthly_periods (user_id, year, month, income, carryover_balance)
    VALUES (demo_user, 2026, 6, 8500.00, 320.00)
    ON CONFLICT (user_id, year, month) DO NOTHING
    RETURNING id INTO period_id;

    IF period_id IS NULL THEN RETURN; END IF;

    -- Templates
    INSERT INTO expense_templates (user_id, name, category, expense_type, base_amount, display_order) VALUES
        (demo_user, 'Aluguel',      'Moradia',   'rent',     1800.00, 1),
        (demo_user, 'Internet',     'Moradia',   'fixed',     109.90, 2),
        (demo_user, 'Streaming',    'Lazer',     'fixed',      55.90, 3),
        (demo_user, 'Celular',      'Serviços',  'fixed',      89.90, 4),
        (demo_user, 'Academia',     'Saúde',     'fixed',     109.00, 5),
        (demo_user, 'Fatura Cartão','Variável',  'variable',    0.00, 6);

    -- Monthly expenses for June 2026
    INSERT INTO monthly_expenses (period_id, template_id, name, category, expense_type, amount, rent_base, display_order)
    SELECT
        period_id,
        t.id,
        t.name,
        t.category,
        t.expense_type,
        CASE WHEN t.expense_type = 'rent' THEN 0 ELSE t.base_amount END,
        CASE WHEN t.expense_type = 'rent' THEN t.base_amount ELSE 0 END,
        t.display_order
    FROM expense_templates t
    WHERE t.user_id = demo_user;
END $$;

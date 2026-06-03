-- Nexo Lite — Supabase PostgreSQL Schema
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─── Monthly Periods ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS monthly_periods (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL,
    year            INTEGER NOT NULL,
    month           INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    status          VARCHAR(20) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'closed')),
    income          NUMERIC(12, 2) NOT NULL DEFAULT 0,
    carryover_balance NUMERIC(12, 2) NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, year, month)
);

-- ─── Expense Templates (master recurring list) ─────────────────────────────
CREATE TABLE IF NOT EXISTS expense_templates (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL,
    name                VARCHAR(255) NOT NULL,
    category            VARCHAR(100) NOT NULL DEFAULT 'Outros',
    expense_type        VARCHAR(20) NOT NULL DEFAULT 'fixed'
                        CHECK (expense_type IN ('fixed', 'variable', 'installment', 'rent')),
    base_amount         NUMERIC(12, 2) NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    installment_total   INTEGER,
    installment_paid    INTEGER NOT NULL DEFAULT 0,
    display_order       INTEGER NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── Monthly Expenses (instances per period) ───────────────────────────────
CREATE TABLE IF NOT EXISTS monthly_expenses (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    period_id           UUID NOT NULL REFERENCES monthly_periods(id) ON DELETE CASCADE,
    template_id         UUID REFERENCES expense_templates(id) ON DELETE SET NULL,
    name                VARCHAR(255) NOT NULL,
    category            VARCHAR(100) NOT NULL DEFAULT 'Outros',
    expense_type        VARCHAR(20) NOT NULL DEFAULT 'fixed'
                        CHECK (expense_type IN ('fixed', 'variable', 'installment', 'rent')),
    amount              NUMERIC(12, 2) NOT NULL DEFAULT 0,
    is_paid             BOOLEAN NOT NULL DEFAULT FALSE,
    paid_at             TIMESTAMPTZ,
    installment_current INTEGER,
    installment_total   INTEGER,
    -- Rent breakdown components (only used when expense_type = 'rent')
    rent_base           NUMERIC(12, 2) NOT NULL DEFAULT 0,
    rent_water          NUMERIC(12, 2) NOT NULL DEFAULT 0,
    rent_gas            NUMERIC(12, 2) NOT NULL DEFAULT 0,
    rent_extras         NUMERIC(12, 2) NOT NULL DEFAULT 0,
    display_order       INTEGER NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── Indexes ────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_monthly_periods_user_status ON monthly_periods(user_id, status);
CREATE INDEX IF NOT EXISTS idx_expense_templates_user_active ON expense_templates(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_monthly_expenses_period ON monthly_expenses(period_id);

-- ─── Auto-update updated_at trigger ─────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_monthly_periods_updated
    BEFORE UPDATE ON monthly_periods
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_expense_templates_updated
    BEFORE UPDATE ON expense_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_monthly_expenses_updated
    BEFORE UPDATE ON monthly_expenses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ─── Seed demo data (single demo user, remove in production) ────────────────
DO $$
DECLARE
    demo_user UUID := '00000000-0000-0000-0000-000000000001';
    period_id UUID;
    tmpl_rent UUID;
    tmpl_internet UUID;
    tmpl_streaming UUID;
    tmpl_phone UUID;
    tmpl_gym UUID;
    tmpl_credit UUID;
    tmpl_car UUID;
BEGIN
    -- Create current period (June 2026)
    INSERT INTO monthly_periods (id, user_id, year, month, income, carryover_balance)
    VALUES (uuid_generate_v4(), demo_user, 2026, 6, 8500.00, 320.00)
    ON CONFLICT (user_id, year, month) DO NOTHING
    RETURNING id INTO period_id;

    IF period_id IS NULL THEN RETURN; END IF;

    -- Templates
    INSERT INTO expense_templates (id, user_id, name, category, expense_type, base_amount, display_order)
    VALUES
        (uuid_generate_v4(), demo_user, 'Aluguel',     'Moradia',    'rent',     1800.00, 1),
        (uuid_generate_v4(), demo_user, 'Internet',    'Moradia',    'fixed',     109.90, 2),
        (uuid_generate_v4(), demo_user, 'Streaming',   'Lazer',      'fixed',      55.90, 3),
        (uuid_generate_v4(), demo_user, 'Celular',     'Serviços',   'fixed',      89.90, 4),
        (uuid_generate_v4(), demo_user, 'Academia',    'Saúde',      'fixed',     109.00, 5),
        (uuid_generate_v4(), demo_user, 'Fatura Cartão','Variável',  'variable',    0.00, 6)
    RETURNING id;

    -- Get ids for monthly expenses seed
    SELECT id INTO tmpl_rent     FROM expense_templates WHERE user_id = demo_user AND name = 'Aluguel';
    SELECT id INTO tmpl_internet FROM expense_templates WHERE user_id = demo_user AND name = 'Internet';
    SELECT id INTO tmpl_streaming FROM expense_templates WHERE user_id = demo_user AND name = 'Streaming';
    SELECT id INTO tmpl_phone    FROM expense_templates WHERE user_id = demo_user AND name = 'Celular';
    SELECT id INTO tmpl_gym      FROM expense_templates WHERE user_id = demo_user AND name = 'Academia';
    SELECT id INTO tmpl_credit   FROM expense_templates WHERE user_id = demo_user AND name = 'Fatura Cartão';

    -- Monthly expenses for current period
    INSERT INTO monthly_expenses (period_id, template_id, name, category, expense_type, amount, rent_base, display_order)
    VALUES
        (period_id, tmpl_rent,      'Aluguel',      'Moradia',   'rent',     0.00, 1800.00, 1),
        (period_id, tmpl_internet,  'Internet',     'Moradia',   'fixed',  109.90,    0.00, 2),
        (period_id, tmpl_streaming, 'Streaming',    'Lazer',     'fixed',   55.90,    0.00, 3),
        (period_id, tmpl_phone,     'Celular',      'Serviços',  'fixed',   89.90,    0.00, 4),
        (period_id, tmpl_gym,       'Academia',     'Saúde',     'fixed',  109.00,    0.00, 5),
        (period_id, tmpl_credit,    'Fatura Cartão','Variável',  'variable',  0.00,   0.00, 6);

END $$;

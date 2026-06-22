-- ============================================================
-- Nexo Lite — Consolidated PostgreSQL Schema
-- Run this in Supabase SQL Editor to set up a fresh database
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─── Categories ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.categories (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL,
    name        VARCHAR(100) NOT NULL,
    icon        VARCHAR(50) NOT NULL DEFAULT 'Tag',
    color       VARCHAR(20) NOT NULL DEFAULT 'slate',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, name)
);

-- ─── Monthly Periods ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.monthly_periods (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                 UUID NOT NULL,
    year                    INTEGER NOT NULL,
    month                   INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    status                  VARCHAR(20) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'closed')),
    income_alvaro           NUMERIC(12,2) NOT NULL DEFAULT 0,
    income_alexandra        NUMERIC(12,2) NOT NULL DEFAULT 0,
    carryover_balance       NUMERIC(12,2) NOT NULL DEFAULT 0,
    additional_income_items JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, year, month)
);

-- ─── Expense Templates (master recurring list) ───────────────────────────────
CREATE TABLE IF NOT EXISTS public.expense_templates (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL,
    name                VARCHAR(255) NOT NULL,
    category            VARCHAR(100) NOT NULL DEFAULT 'Outros',
    category_id         UUID REFERENCES public.categories(id) ON DELETE SET NULL,
    expense_type        VARCHAR(20) NOT NULL DEFAULT 'fixed'
                        CHECK (expense_type IN ('fixed', 'variable', 'installment', 'rent')),
    base_amount         NUMERIC(12, 2) NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    installment_total   INTEGER,
    installment_paid    INTEGER NOT NULL DEFAULT 0,
    display_order       INTEGER NOT NULL DEFAULT 0,
    responsavel         VARCHAR(20) NOT NULL DEFAULT 'conjunto',
    rent_items          JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── Monthly Expenses (instances per period) ─────────────────────────────────
CREATE TABLE IF NOT EXISTS public.monthly_expenses (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    period_id           UUID NOT NULL REFERENCES public.monthly_periods(id) ON DELETE CASCADE,
    template_id         UUID REFERENCES public.expense_templates(id) ON DELETE SET NULL,
    name                VARCHAR(255) NOT NULL,
    category            VARCHAR(100) NOT NULL DEFAULT 'Outros',
    category_id         UUID REFERENCES public.categories(id) ON DELETE SET NULL,
    expense_type        VARCHAR(20) NOT NULL DEFAULT 'fixed'
                        CHECK (expense_type IN ('fixed', 'variable', 'installment', 'rent')),
    amount              NUMERIC(12, 2) NOT NULL DEFAULT 0,
    is_paid             BOOLEAN NOT NULL DEFAULT FALSE,
    paid_at             TIMESTAMPTZ,
    installment_current INTEGER,
    installment_total   INTEGER,
    display_order       INTEGER NOT NULL DEFAULT 0,
    responsavel         VARCHAR(20) NOT NULL DEFAULT 'conjunto',
    rent_items          JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── Vault Reconciliations ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.vault_reconciliations (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL,
    real_balance        NUMERIC(12,2) NOT NULL DEFAULT 0,
    computed_balance    NUMERIC(12,2) NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── Debts & Loans ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.debts (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL,
    name                VARCHAR(255) NOT NULL,
    original_amount     NUMERIC(12,2) NOT NULL DEFAULT 0,
    estimated_amount    NUMERIC(12,2) NOT NULL DEFAULT 0,
    status              VARCHAR(20) NOT NULL DEFAULT 'ativo' CHECK (status IN ('ativo', 'quitado')),
    direction           VARCHAR(10) NOT NULL DEFAULT 'eu_devo' CHECK (direction IN ('eu_devo', 'me_deve')),
    due_date            DATE,
    notes               TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    interest_rate       NUMERIC(6,2) NOT NULL DEFAULT 0.00,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── Debt Payments ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.debt_payments (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    debt_id     UUID NOT NULL REFERENCES public.debts(id) ON DELETE CASCADE,
    amount      NUMERIC(12,2) NOT NULL,
    paid_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    notes       TEXT
);

-- ─── Expense Notes ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.expense_notes (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    expense_id  UUID NOT NULL REFERENCES public.monthly_expenses(id) ON DELETE CASCADE,
    content     TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── Scheduled Expenses ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.scheduled_expenses (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL,
    target_year     INTEGER NOT NULL,
    target_month    INTEGER NOT NULL CHECK (target_month BETWEEN 1 AND 12),
    name            VARCHAR(255) NOT NULL,
    category_id     UUID REFERENCES public.categories(id) ON DELETE SET NULL,
    expense_type    VARCHAR(20) NOT NULL DEFAULT 'variable',
    responsavel     VARCHAR(20) NOT NULL DEFAULT 'conjunto',
    amount          NUMERIC(12,2) NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── User Settings (Preferences Cloud Sync) ──────────────────────────────────
CREATE TABLE IF NOT EXISTS public.user_settings (
    user_id     UUID PRIMARY KEY,
    settings    JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── Indexes ─────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_categories_user ON public.categories(user_id);
CREATE INDEX IF NOT EXISTS idx_monthly_periods_user_status ON public.monthly_periods(user_id, status);
CREATE INDEX IF NOT EXISTS idx_expense_templates_user_active ON public.expense_templates(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_monthly_expenses_period ON public.monthly_expenses(period_id);
CREATE INDEX IF NOT EXISTS idx_vault_reconciliations_user ON public.vault_reconciliations(user_id);
CREATE INDEX IF NOT EXISTS idx_debts_user_status ON public.debts(user_id, status);
CREATE INDEX IF NOT EXISTS idx_debt_payments_debt ON public.debt_payments(debt_id);
CREATE INDEX IF NOT EXISTS idx_expense_notes_expense ON public.expense_notes(expense_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_expenses_user_target ON public.scheduled_expenses(user_id, target_year, target_month);

-- ─── Auto-update updated_at trigger function ─────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ─── Triggers ────────────────────────────────────────────────────────────────
CREATE OR REPLACE TRIGGER trg_categories_updated
    BEFORE UPDATE ON public.categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE OR REPLACE TRIGGER trg_monthly_periods_updated
    BEFORE UPDATE ON public.monthly_periods
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE OR REPLACE TRIGGER trg_expense_templates_updated
    BEFORE UPDATE ON public.expense_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE OR REPLACE TRIGGER trg_monthly_expenses_updated
    BEFORE UPDATE ON public.monthly_expenses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE OR REPLACE TRIGGER trg_debts_updated
    BEFORE UPDATE ON public.debts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE OR REPLACE TRIGGER trg_expense_notes_updated
    BEFORE UPDATE ON public.expense_notes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE OR REPLACE TRIGGER trg_user_settings_updated
    BEFORE UPDATE ON public.user_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ─── Seed Demo Data (Optional, for development purposes) ──────────────────────
DO $$
DECLARE
    demo_user UUID := '00000000-0000-0000-0000-000000000001';
    period_id UUID;
    cat_moradia UUID;
    cat_lazer UUID;
    cat_servicos UUID;
    cat_saude UUID;
    cat_variavel UUID;
    tmpl_rent UUID;
    tmpl_internet UUID;
    tmpl_streaming UUID;
    tmpl_phone UUID;
    tmpl_gym UUID;
    tmpl_credit UUID;
BEGIN
    -- Seed categories
    INSERT INTO public.categories (user_id, name, icon, color) VALUES
        (demo_user, 'Moradia', 'Home', 'indigo'),
        (demo_user, 'Lazer', 'Tv', 'rose'),
        (demo_user, 'Serviços', 'Cpu', 'blue'),
        (demo_user, 'Saúde', 'HeartPulse', 'emerald'),
        (demo_user, 'Variável', 'CreditCard', 'amber')
    ON CONFLICT (user_id, name) DO NOTHING;

    SELECT id INTO cat_moradia FROM public.categories WHERE user_id = demo_user AND name = 'Moradia';
    SELECT id INTO cat_lazer FROM public.categories WHERE user_id = demo_user AND name = 'Lazer';
    SELECT id INTO cat_servicos FROM public.categories WHERE user_id = demo_user AND name = 'Serviços';
    SELECT id INTO cat_saude FROM public.categories WHERE user_id = demo_user AND name = 'Saúde';
    SELECT id INTO cat_variavel FROM public.categories WHERE user_id = demo_user AND name = 'Variável';

    -- Create current period (June 2026)
    INSERT INTO public.monthly_periods (user_id, year, month, income_alvaro, income_alexandra, carryover_balance)
    VALUES (demo_user, 2026, 6, 4500.00, 4000.00, 0.00)
    ON CONFLICT (user_id, year, month) DO NOTHING
    RETURNING id INTO period_id;

    IF period_id IS NULL THEN RETURN; END IF;

    -- Templates
    INSERT INTO public.expense_templates (user_id, name, category, category_id, expense_type, base_amount, display_order)
    VALUES
        (demo_user, 'Aluguel',     'Moradia',    cat_moradia,  'rent',     1800.00, 1),
        (demo_user, 'Internet',    'Moradia',    cat_moradia,  'fixed',     109.90, 2),
        (demo_user, 'Streaming',   'Lazer',      cat_lazer,    'fixed',      55.90, 3),
        (demo_user, 'Celular',     'Serviços',   cat_servicos, 'fixed',      89.90, 4),
        (demo_user, 'Academia',    'Saúde',      cat_saude,    'fixed',     109.00, 5),
        (demo_user, 'Fatura Cartão','Variável',  cat_variavel, 'variable',    0.00, 6)
    ON CONFLICT DO NOTHING;

    -- Get template ids for monthly expenses seed
    SELECT id INTO tmpl_rent     FROM public.expense_templates WHERE user_id = demo_user AND name = 'Aluguel';
    SELECT id INTO tmpl_internet FROM public.expense_templates WHERE user_id = demo_user AND name = 'Internet';
    SELECT id INTO tmpl_streaming FROM public.expense_templates WHERE user_id = demo_user AND name = 'Streaming';
    SELECT id INTO tmpl_phone    FROM public.expense_templates WHERE user_id = demo_user AND name = 'Celular';
    SELECT id INTO tmpl_gym      FROM public.expense_templates WHERE user_id = demo_user AND name = 'Academia';
    SELECT id INTO tmpl_credit   FROM public.expense_templates WHERE user_id = demo_user AND name = 'Fatura Cartão';

    -- Monthly expenses for current period
    INSERT INTO public.monthly_expenses (period_id, template_id, name, category, category_id, expense_type, amount, display_order)
    VALUES
        (period_id, tmpl_rent,      'Aluguel',      'Moradia',   cat_moradia,  'rent',     0.00, 1),
        (period_id, tmpl_internet,  'Internet',     'Moradia',   cat_moradia,  'fixed',  109.90, 2),
        (period_id, tmpl_streaming, 'Streaming',    'Lazer',     cat_lazer,    'fixed',   55.90, 3),
        (period_id, tmpl_phone,     'Celular',      'Serviços',  cat_servicos, 'fixed',   89.90, 4),
        (period_id, tmpl_gym,       'Academia',     'Saúde',     cat_saude,    'fixed',  109.00, 5),
        (period_id, tmpl_credit,    'Fatura Cartão','Variável',  cat_variavel, 'variable',  0.00, 6)
    ON CONFLICT DO NOTHING;

END $$;

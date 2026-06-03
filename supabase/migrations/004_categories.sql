-- ============================================================
-- Migration 004 — Categories with color and icon
-- Project : Nexo Lite
-- Date    : 2026-06-03
-- Depends : 003_rent_items_jsonb.sql
-- Run in  : Supabase SQL Editor
-- ============================================================

CREATE TABLE IF NOT EXISTS categories (
    id            UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id       UUID        NOT NULL,
    name          VARCHAR(100) NOT NULL,
    color         VARCHAR(20)  NOT NULL DEFAULT 'slate',   -- key used in frontend palette
    icon          VARCHAR(50)  NOT NULL DEFAULT 'Package',  -- Lucide icon name
    display_order INTEGER      NOT NULL DEFAULT 0,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, name)
);

CREATE INDEX IF NOT EXISTS idx_categories_user ON categories(user_id);

-- category_id (nullable) on monthly_expenses and expense_templates
ALTER TABLE monthly_expenses
    ADD COLUMN IF NOT EXISTS category_id UUID REFERENCES categories(id) ON DELETE SET NULL;

ALTER TABLE expense_templates
    ADD COLUMN IF NOT EXISTS category_id UUID REFERENCES categories(id) ON DELETE SET NULL;

-- ── Default categories for demo user ─────────────────────────────────────
DO $$
DECLARE
    demo UUID := '00000000-0000-0000-0000-000000000001';
    cid_moradia   UUID; cid_lazer    UUID; cid_servicos UUID;
    cid_saude     UUID; cid_variavel UUID; cid_outros   UUID;
BEGIN
    INSERT INTO categories (user_id, name, color, icon, display_order) VALUES
        (demo, 'Moradia',    'blue',    'Home',        1),
        (demo, 'Lazer',      'violet',  'Gamepad2',    2),
        (demo, 'Serviços',   'amber',   'Smartphone',  3),
        (demo, 'Saúde',      'emerald', 'Heart',       4),
        (demo, 'Variável',   'orange',  'CreditCard',  5),
        (demo, 'Outros',     'slate',   'Package',     6)
    ON CONFLICT (user_id, name) DO NOTHING;

    SELECT id INTO cid_moradia   FROM categories WHERE user_id = demo AND name = 'Moradia';
    SELECT id INTO cid_lazer     FROM categories WHERE user_id = demo AND name = 'Lazer';
    SELECT id INTO cid_servicos  FROM categories WHERE user_id = demo AND name = 'Serviços';
    SELECT id INTO cid_saude     FROM categories WHERE user_id = demo AND name = 'Saúde';
    SELECT id INTO cid_variavel  FROM categories WHERE user_id = demo AND name = 'Variável';

    -- Link existing expenses
    UPDATE monthly_expenses SET category_id = cid_moradia  WHERE category = 'Moradia'  AND category_id IS NULL;
    UPDATE monthly_expenses SET category_id = cid_lazer    WHERE category = 'Lazer'    AND category_id IS NULL;
    UPDATE monthly_expenses SET category_id = cid_servicos WHERE category = 'Serviços' AND category_id IS NULL;
    UPDATE monthly_expenses SET category_id = cid_saude    WHERE category = 'Saúde'    AND category_id IS NULL;
    UPDATE monthly_expenses SET category_id = cid_variavel WHERE category = 'Variável' AND category_id IS NULL;

    -- Link templates
    UPDATE expense_templates SET category_id = cid_moradia  WHERE category = 'Moradia'  AND category_id IS NULL;
    UPDATE expense_templates SET category_id = cid_lazer    WHERE category = 'Lazer'    AND category_id IS NULL;
    UPDATE expense_templates SET category_id = cid_servicos WHERE category = 'Serviços' AND category_id IS NULL;
    UPDATE expense_templates SET category_id = cid_saude    WHERE category = 'Saúde'    AND category_id IS NULL;
    UPDATE expense_templates SET category_id = cid_variavel WHERE category = 'Variável' AND category_id IS NULL;
END $$;

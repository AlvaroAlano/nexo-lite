-- 007 — Seed template "Caixinha" para o demo user
-- 2026-06-04
-- Run in: Supabase SQL Editor

INSERT INTO expense_templates (user_id, name, category, expense_type, base_amount, is_active, display_order)
SELECT
    '00000000-0000-0000-0000-000000000001',
    'Caixinha',
    'Caixinha',
    'variable',
    0.00,
    TRUE,
    99
WHERE NOT EXISTS (
    SELECT 1 FROM expense_templates
    WHERE user_id = '00000000-0000-0000-0000-000000000001'
      AND category = 'Caixinha'
);

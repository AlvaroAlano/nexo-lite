-- 008 — Garante despesa "Caixinha" em todo período aberto sem ela
-- 2026-06-04
-- Run in: Supabase SQL Editor

INSERT INTO monthly_expenses (period_id, name, category, expense_type, amount, is_paid, display_order)
SELECT
    mp.id,
    'Caixinha',
    'Caixinha',
    'variable',
    0.00,
    FALSE,
    999
FROM monthly_periods mp
WHERE mp.user_id = '00000000-0000-0000-0000-000000000001'
  AND mp.status = 'open'
  AND NOT EXISTS (
      SELECT 1 FROM monthly_expenses me
      WHERE me.period_id = mp.id
        AND me.category = 'Caixinha'
  );

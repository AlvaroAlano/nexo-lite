-- 013 — Juros por dívida (motor de quitação: Bola de Neve vs Avalanche)
-- 2026-06-18
-- Run in: Supabase SQL Editor

ALTER TABLE debts
    ADD COLUMN IF NOT EXISTS interest_rate NUMERIC(6, 2) NOT NULL DEFAULT 0;

-- interest_rate = juros ao MÊS em pontos percentuais (ex.: 5.00 = 5% a.m.).
-- 0 = sem juros (empréstimo entre pessoas, dívida sem encargo).
COMMENT ON COLUMN debts.interest_rate IS 'Juros ao mes em pontos percentuais (5.00 = 5%/mes)';

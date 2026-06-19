-- 014 — Scheduled expenses (despesas agendadas para mês futuro)
-- 2026-06-19
-- Run in: Supabase SQL Editor
--
-- Fila de despesas lançadas para um mês que ainda não existe (ex.: comprar agora,
-- pagar mês que vem). NÃO entra em nenhuma agregação do mês atual; materializa em
-- monthly_expenses quando o período do mês alvo é criado (virada ou auto-criação).

CREATE TABLE IF NOT EXISTS scheduled_expenses (
    id                  UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID         NOT NULL,
    target_year         INTEGER      NOT NULL,
    target_month        INTEGER      NOT NULL CHECK (target_month BETWEEN 1 AND 12),
    name                VARCHAR(255) NOT NULL,
    category            VARCHAR(100) NOT NULL DEFAULT 'Outros',
    category_id         UUID         REFERENCES categories(id) ON DELETE SET NULL,
    expense_type        VARCHAR(20)  NOT NULL DEFAULT 'variable',
    responsavel         VARCHAR(20)  NOT NULL DEFAULT 'conjunto',
    amount              NUMERIC(12,2) NOT NULL DEFAULT 0,
    is_paid             BOOLEAN      NOT NULL DEFAULT FALSE,
    installment_current INTEGER,
    installment_total   INTEGER,
    display_order       INTEGER      NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_scheduled_expenses_target
    ON scheduled_expenses (user_id, target_year, target_month);

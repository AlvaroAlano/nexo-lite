-- ============================================================
-- Migration 017 — Sincronização de Preferências e Configurações de Usuário
-- Project : Nexo Lite
-- Date    : 2026-06-22
-- Run in  : Supabase SQL Editor
-- ============================================================

CREATE TABLE IF NOT EXISTS public.user_settings (
    user_id     UUID PRIMARY KEY,
    settings    JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Trigger para atualizar updated_at automaticamente
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_user_settings_updated') THEN
        CREATE TRIGGER trg_user_settings_updated
            BEFORE UPDATE ON public.user_settings
            FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    END IF;
END $$;

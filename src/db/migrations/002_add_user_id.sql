-- Migration 002: multi-user isolation
-- Safe for existing data: backfill with sentinel 0, no DROP.
-- Idempotent: indexes use IF NOT EXISTS.
-- Run once: sqlite3 data/thdora.db < src/db/migrations/002_add_user_id.sql

PRAGMA journal_mode=WAL;

-- appointments
ALTER TABLE appointments ADD COLUMN telegram_user_id INTEGER NOT NULL DEFAULT 0;
CREATE INDEX IF NOT EXISTS ix_appointments_user ON appointments(telegram_user_id);
CREATE INDEX IF NOT EXISTS ix_appointments_user_date ON appointments(telegram_user_id, date);

-- habits
ALTER TABLE habits ADD COLUMN telegram_user_id INTEGER NOT NULL DEFAULT 0;
CREATE INDEX IF NOT EXISTS ix_habits_user ON habits(telegram_user_id);
CREATE INDEX IF NOT EXISTS ix_habits_user_date ON habits(telegram_user_id, date);

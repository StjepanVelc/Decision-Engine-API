-- ============================================================
-- Migration: Add risk scoring + DSL expression support
-- Run against the 'decision_engine' database.
-- Safe to run multiple times (uses IF NOT EXISTS / IF EXISTS).
-- ============================================================

-- ── rules table ─────────────────────────────────────────────────────────────

-- Make legacy condition columns nullable (expression-only rules don't need them)
ALTER TABLE rules ALTER COLUMN field     DROP NOT NULL;
ALTER TABLE rules ALTER COLUMN operator  DROP NOT NULL;
ALTER TABLE rules ALTER COLUMN value     DROP NOT NULL;

-- Add DSL expression column
ALTER TABLE rules ADD COLUMN
IF NOT EXISTS expression TEXT;

-- Add risk-score weight column (default 10 for existing rules)
ALTER TABLE rules ADD COLUMN
IF NOT EXISTS weight INTEGER NOT NULL DEFAULT 10;

-- Update operator check constraint to allow NULL (expression-only rules)
ALTER TABLE rules DROP CONSTRAINT IF EXISTS ck_rules_operator;
ALTER TABLE rules ADD CONSTRAINT ck_rules_operator CHECK (
    operator IS NULL
    OR operator IN ('gt','lt','gte','lte','eq','neq','in','not_in','contains','not_contains')
);

-- Enforce: every rule must have either an expression OR the legacy triple
ALTER TABLE rules DROP CONSTRAINT IF EXISTS ck_rules_expression_or_legacy;
ALTER TABLE rules ADD CONSTRAINT ck_rules_expression_or_legacy CHECK (
    expression IS NOT NULL
    OR (field IS NOT NULL AND operator IS NOT NULL AND value IS NOT NULL)
);

-- Weight must be non-negative
ALTER TABLE rules DROP CONSTRAINT IF EXISTS ck_rules_weight_positive;
ALTER TABLE rules ADD CONSTRAINT ck_rules_weight_positive CHECK (weight >= 0);

-- ── decisions table ──────────────────────────────────────────────────────────

-- Add cumulative risk score column (default 0 for historical decisions)
ALTER TABLE decisions ADD COLUMN
IF NOT EXISTS risk_score INTEGER NOT NULL DEFAULT 0;

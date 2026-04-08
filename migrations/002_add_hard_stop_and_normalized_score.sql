-- Migration 002: Add hard_stop to rules, normalized_score to decisions
-- Run this after migration 001

ALTER TABLE rules ADD COLUMN hard_stop BOOLEAN NOT NULL DEFAULT false;

ALTER TABLE decisions ADD COLUMN normalized_score INTEGER NOT NULL DEFAULT 0;

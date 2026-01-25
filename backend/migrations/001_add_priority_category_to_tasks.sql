-- Migration: Add priority and category fields to tasks table
-- Date: 2026-01-18
-- Description: Adds priority (high/medium/low) and category (personal/work/shopping) fields

-- Add priority column with default value 'medium'
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'medium';

-- Add category column (nullable)
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS category VARCHAR(50);

-- Update existing tasks to have default priority if NULL
UPDATE tasks
SET priority = 'medium'
WHERE priority IS NULL;

-- Add comment to document the columns
COMMENT ON COLUMN tasks.priority IS 'Task priority: high, medium, or low';
COMMENT ON COLUMN tasks.category IS 'Task category: personal, work, shopping, etc.';

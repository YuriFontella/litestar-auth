-- Add refresh_token column to sessions table
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS refresh_token text UNIQUE;

-- Add index for faster lookup
CREATE INDEX IF NOT EXISTS idx_sessions_refresh_token ON sessions(refresh_token) WHERE refresh_token IS NOT NULL;


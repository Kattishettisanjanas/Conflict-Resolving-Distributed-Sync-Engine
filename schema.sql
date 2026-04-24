CREATE TABLE IF NOT EXISTS items (
    id TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    site_id TEXT NOT NULL,
    vector_clock JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_updated_at ON items(updated_at);

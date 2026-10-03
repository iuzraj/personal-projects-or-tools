CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT,
    password_hash TEXT,
    profile_picture TEXT DEFAULT 'default',
    base_content TEXT DEFAULT '',
    creation_dt INTEGER
);
CREATE TABLE IF NOT EXISTS entries(
    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_name TEXT,
    content TEXT,
    author_id INTEGER,
    creation_dt INTEGER
);
CREATE INDEX IF NOT EXISTS idx_entries_name ON entries(entry_name);
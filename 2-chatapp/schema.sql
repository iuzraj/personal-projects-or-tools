CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    namecolor TEXT DEFAULT 'blue',
    profile_picture TEXT DEFAULT 'default',
    hashed_password TEXT,
    creation_dt INTEGER
);
CREATE TABLE IF NOT EXISTS groups (
    group_id INTEGER PRIMARY KEY AUTOINCREMENT,
    groupname TEXT,
    creator_id INTEGER,
    read_only INTEGER,
    creation_dt INTEGER
);
CREATE TABLE IF NOT EXISTS group_memberships (
    group_id INTEGER,
    member_id INTEGER,
    last_seen INTEGER
);
CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER,
    group_id INTEGER,
    content TEXT,
    creation_dt INTEGER
);
CREATE TABLE IF NOT EXISTS attachments (
    attachment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER,
    filename TEXT,
    filetype TEXT
);
CREATE TABLE IF NOT EXISTS group_invites (
    invite_id INTEGER PRIMARY KEY AUTOINCREMENT,
    invite_to INTEGER,
    invited_by INTEGER,
    user_id INTEGER,
    invite_dt INTEGER
);
CREATE INDEX IF NOT EXISTS idx_attachments ON attachments(message_id);
CREATE INDEX IF NOT EXISTS idx_messages ON messages(group_id);
CREATE INDEX IF NOT EXISTS idx_group_invites ON group_invites(user_id);
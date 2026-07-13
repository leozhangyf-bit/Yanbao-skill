PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS inbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT NOT NULL UNIQUE,
    chat_id TEXT NOT NULL,
    sender_id TEXT NOT NULL,
    message_type TEXT NOT NULL CHECK(message_type IN ('text','image')),
    content TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending','processing','staged','done','failed')),
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT
);

CREATE TABLE IF NOT EXISTS outbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inbound_id INTEGER NOT NULL UNIQUE REFERENCES inbox(id),
    reply_text TEXT NOT NULL,
    candidate_events_json TEXT NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK(status IN ('pending','sending','failed','delivered')),
    attempts INTEGER NOT NULL DEFAULT 0,
    provider_message_id TEXT,
    last_error TEXT
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inbound_id INTEGER NOT NULL REFERENCES inbox(id),
    outbox_id INTEGER NOT NULL REFERENCES outbox(id),
    content TEXT NOT NULL,
    visibility TEXT NOT NULL DEFAULT 'bilateral',
    UNIQUE(outbox_id, content)
);

CREATE TABLE IF NOT EXISTS media_jobs (
    id TEXT PRIMARY KEY,
    direction TEXT NOT NULL CHECK(direction IN ('inbound','outbound')),
    status TEXT NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,
    resource_receipt TEXT,
    channel_receipt TEXT,
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT
);


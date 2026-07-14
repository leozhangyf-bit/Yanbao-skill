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

CREATE TABLE IF NOT EXISTS life_roles (
    role_id TEXT PRIMARY KEY,
    invariant_digest TEXT NOT NULL,
    timezone TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('draft','enabled','paused')) DEFAULT 'draft',
    max_proactive_per_day INTEGER NOT NULL DEFAULT 2 CHECK(max_proactive_per_day BETWEEN 0 AND 8),
    proactive_unanswered INTEGER NOT NULL DEFAULT 0 CHECK(proactive_unanswered IN (0,1)),
    last_proactive_event_id TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS life_threads (
    thread_id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL REFERENCES life_roles(role_id),
    goal TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('active','paused','resolved')) DEFAULT 'active',
    pressure INTEGER NOT NULL CHECK(pressure BETWEEN 0 AND 5),
    next_decision_at TEXT NOT NULL,
    allowed_severity TEXT NOT NULL CHECK(allowed_severity IN ('ordinary','major')) DEFAULT 'ordinary',
    last_event_id TEXT,
    last_event_at TEXT,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS life_actors (
    actor_id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL REFERENCES life_roles(role_id),
    display_name TEXT NOT NULL,
    relationship TEXT NOT NULL,
    motivation TEXT NOT NULL,
    stance TEXT NOT NULL,
    next_action TEXT,
    next_action_at TEXT,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS life_thread_actors (
    thread_id TEXT NOT NULL REFERENCES life_threads(thread_id),
    actor_id TEXT NOT NULL REFERENCES life_actors(actor_id),
    PRIMARY KEY(thread_id, actor_id)
);

CREATE TABLE IF NOT EXISTS life_wakes (
    wake_id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL REFERENCES life_roles(role_id),
    due_at TEXT NOT NULL,
    reason TEXT NOT NULL CHECK(reason IN ('scheduled','reconnect','deadline','inquiry','external')),
    source_event_id TEXT,
    status TEXT NOT NULL CHECK(status IN ('pending','processing','done','skipped','failed')) DEFAULT 'pending',
    attempts INTEGER NOT NULL DEFAULT 0,
    eligibility_reason TEXT,
    last_error TEXT
);

CREATE TABLE IF NOT EXISTS life_events (
    event_id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL REFERENCES life_roles(role_id),
    wake_id TEXT NOT NULL UNIQUE REFERENCES life_wakes(wake_id),
    thread_id TEXT NOT NULL REFERENCES life_threads(thread_id),
    occurred_at TEXT NOT NULL,
    event_kind TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('ordinary','major')),
    causal_basis TEXT NOT NULL,
    role_action TEXT NOT NULL,
    summary TEXT NOT NULL,
    consequence TEXT NOT NULL,
    actor_ids_json TEXT NOT NULL,
    cause_event_ids_json TEXT NOT NULL,
    disclosure TEXT NOT NULL CHECK(disclosure IN ('private','shareable','should_contact')),
    deception_json TEXT,
    canon_status TEXT NOT NULL CHECK(canon_status IN ('private_committed','superseded')) DEFAULT 'private_committed'
);

CREATE TABLE IF NOT EXISTS proactive_intents (
    intent_id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL REFERENCES life_roles(role_id),
    source_event_id TEXT NOT NULL UNIQUE REFERENCES life_events(event_id),
    local_date TEXT NOT NULL,
    reason TEXT NOT NULL,
    disclosure_hint TEXT NOT NULL,
    material_change INTEGER NOT NULL CHECK(material_change IN (0,1)),
    status TEXT NOT NULL CHECK(status IN ('pending','staged','delivered','suppressed')) DEFAULT 'pending',
    suppressed_reason TEXT
);

CREATE TABLE IF NOT EXISTS proactive_outbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intent_id TEXT NOT NULL UNIQUE REFERENCES proactive_intents(intent_id),
    chat_id TEXT NOT NULL,
    reply_text TEXT NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK(status IN ('pending','sending','failed','delivered')),
    attempts INTEGER NOT NULL DEFAULT 0,
    provider_message_id TEXT,
    last_error TEXT
);

CREATE TABLE IF NOT EXISTS life_disclosures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_event_id TEXT NOT NULL REFERENCES life_events(event_id),
    proactive_outbox_id INTEGER NOT NULL UNIQUE REFERENCES proactive_outbox(id),
    provider_message_id TEXT NOT NULL,
    disclosed_at TEXT NOT NULL
);

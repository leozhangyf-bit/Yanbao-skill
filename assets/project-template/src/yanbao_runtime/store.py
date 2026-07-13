from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from pathlib import Path
from typing import Any

from .contracts import DeliveryReceipt, InboundMessage, TurnProposal


class StoreError(RuntimeError):
    pass


class StateStore:
    def __init__(self, database: str | Path) -> None:
        self.database = Path(database)
        self.database.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.database)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA foreign_keys=ON")

    def close(self) -> None:
        self.connection.close()

    def initialize(self) -> None:
        schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
        self.connection.executescript(schema)
        self.connection.execute(
            "INSERT OR IGNORE INTO settings(key,value) VALUES('armed','0')"
        )
        self.connection.commit()

    def integrity(self) -> str:
        return str(self.connection.execute("PRAGMA integrity_check").fetchone()[0])

    def is_armed(self) -> bool:
        row = self.connection.execute(
            "SELECT value FROM settings WHERE key='armed'"
        ).fetchone()
        return row is not None and row["value"] == "1"

    def set_armed(self, armed: bool) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO settings(key,value) VALUES('armed',?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                ("1" if armed else "0",),
            )

    def ingest(self, message: InboundMessage) -> int:
        with self.connection:
            self.connection.execute(
                "INSERT OR IGNORE INTO inbox(message_id,chat_id,sender_id,message_type,content,status) "
                "VALUES(?,?,?,?,?,'pending')",
                (message.message_id, message.chat_id, message.sender_id, message.message_type, message.content),
            )
            row = self.connection.execute(
                "SELECT id FROM inbox WHERE message_id=?", (message.message_id,)
            ).fetchone()
        return int(row["id"])

    def claim_next(self) -> dict[str, Any] | None:
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            row = self.connection.execute(
                "SELECT * FROM inbox WHERE status IN ('pending','failed') ORDER BY id LIMIT 1"
            ).fetchone()
            if row is None:
                self.connection.commit()
                return None
            changed = self.connection.execute(
                "UPDATE inbox SET status='processing',attempts=attempts+1,last_error=NULL "
                "WHERE id=? AND status=?",
                (row["id"], row["status"]),
            ).rowcount
            if changed != 1:
                raise StoreError("stale inbox claim")
            self.connection.commit()
            return dict(self.connection.execute("SELECT * FROM inbox WHERE id=?", (row["id"],)).fetchone())
        except Exception:
            self.connection.rollback()
            raise

    def fail_inbox(self, inbound_id: int, error: str) -> None:
        with self.connection:
            changed = self.connection.execute(
                "UPDATE inbox SET status='failed',last_error=? WHERE id=? AND status='processing'",
                (error[:128], inbound_id),
            ).rowcount
            if changed != 1:
                raise StoreError("stale inbox failure")

    def stage(self, inbound_id: int, proposal: TurnProposal) -> int:
        key = f"reply-{inbound_id}"
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            changed = self.connection.execute(
                "UPDATE inbox SET status='staged',last_error=NULL WHERE id=? AND status='processing'",
                (inbound_id,),
            ).rowcount
            if changed != 1:
                raise StoreError("stale inbox stage")
            self.connection.execute(
                "INSERT INTO outbox(inbound_id,reply_text,candidate_events_json,idempotency_key,status) "
                "VALUES(?,?,?,?,'pending')",
                (inbound_id, proposal.reply_text, json.dumps(proposal.candidate_events, ensure_ascii=False), key),
            )
            outbox_id = int(self.connection.execute("SELECT last_insert_rowid()").fetchone()[0])
            self.connection.commit()
            return outbox_id
        except Exception:
            self.connection.rollback()
            raise

    def claim_outbox(self) -> dict[str, Any] | None:
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            row = self.connection.execute(
                "SELECT o.*,i.chat_id FROM outbox o JOIN inbox i ON i.id=o.inbound_id "
                "WHERE o.status IN ('pending','failed') ORDER BY o.id LIMIT 1"
            ).fetchone()
            if row is None:
                self.connection.commit()
                return None
            changed = self.connection.execute(
                "UPDATE outbox SET status='sending',attempts=attempts+1,last_error=NULL "
                "WHERE id=? AND status=?",
                (row["id"], row["status"]),
            ).rowcount
            if changed != 1:
                raise StoreError("stale outbox claim")
            self.connection.commit()
            return dict(self.connection.execute(
                "SELECT o.*,i.chat_id FROM outbox o JOIN inbox i ON i.id=o.inbound_id WHERE o.id=?",
                (row["id"],),
            ).fetchone())
        except Exception:
            self.connection.rollback()
            raise

    def fail_outbox(self, outbox_id: int, error: str) -> None:
        with self.connection:
            changed = self.connection.execute(
                "UPDATE outbox SET status='failed',last_error=? WHERE id=? AND status='sending'",
                (error[:128], outbox_id),
            ).rowcount
            if changed != 1:
                raise StoreError("stale outbox failure")

    def commit_delivery(self, outbox_id: int, receipt: DeliveryReceipt) -> None:
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            row = self.connection.execute("SELECT * FROM outbox WHERE id=?", (outbox_id,)).fetchone()
            if row is None or row["status"] != "sending":
                raise StoreError("stale delivery commit")
            if row["idempotency_key"] != receipt.idempotency_key:
                raise StoreError("receipt idempotency mismatch")
            changed = self.connection.execute(
                "UPDATE outbox SET status='delivered',provider_message_id=?,last_error=NULL "
                "WHERE id=? AND status='sending'",
                (receipt.provider_message_id, outbox_id),
            ).rowcount
            if changed != 1:
                raise StoreError("stale delivery commit")
            events = json.loads(row["candidate_events_json"])
            for content in events:
                self.connection.execute(
                    "INSERT OR IGNORE INTO events(inbound_id,outbox_id,content) VALUES(?,?,?)",
                    (row["inbound_id"], outbox_id, content),
                )
            self.connection.execute(
                "UPDATE inbox SET status='done',last_error=NULL WHERE id=? AND status='staged'",
                (row["inbound_id"],),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def recover(self) -> None:
        with self.connection:
            self.connection.execute(
                "UPDATE inbox SET status='pending',last_error='recovered' WHERE status='processing'"
            )
            self.connection.execute(
                "UPDATE outbox SET status='pending',last_error='recovered' WHERE status='sending'"
            )

    def counts(self) -> dict[str, int]:
        return {
            "inbox": int(self.connection.execute("SELECT count(*) FROM inbox").fetchone()[0]),
            "outbox": int(self.connection.execute("SELECT count(*) FROM outbox").fetchone()[0]),
            "events": int(self.connection.execute("SELECT count(*) FROM events").fetchone()[0]),
        }

    def backup(self, destination: str | Path) -> Path:
        target = Path(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(target) as output:
            self.connection.backup(output)
        if sqlite3.connect(target).execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            target.unlink(missing_ok=True)
            raise StoreError("backup integrity failed")
        return target

    def transition_media(self, job_id: str, old: str, new: str) -> None:
        with self.connection:
            changed = self.connection.execute(
                "UPDATE media_jobs SET status=? WHERE id=? AND status=?",
                (new, job_id, old),
            ).rowcount
            if changed != 1:
                raise StoreError("stale media transition")


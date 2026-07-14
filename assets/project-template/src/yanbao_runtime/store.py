from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from .contracts import (
    DeliveryReceipt,
    InboundMessage,
    LifeActorSnapshot,
    LifeAdvanceProposal,
    LifeAdvanceRequest,
    LifeThreadSnapshot,
    LifeWake,
    TurnProposal,
)


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
        self.connection.execute(
            "INSERT OR IGNORE INTO settings(key,value) VALUES('schema_version','2')"
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
            self.connection.execute(
                "UPDATE life_wakes SET status='pending',last_error='recovered' WHERE status='processing'"
            )
            self.connection.execute(
                "UPDATE proactive_outbox SET status='pending',last_error='recovered' WHERE status='sending'"
            )

    def counts(self) -> dict[str, int]:
        return {
            "inbox": int(self.connection.execute("SELECT count(*) FROM inbox").fetchone()[0]),
            "outbox": int(self.connection.execute("SELECT count(*) FROM outbox").fetchone()[0]),
            "events": int(self.connection.execute("SELECT count(*) FROM events").fetchone()[0]),
            "life_roles": int(self.connection.execute("SELECT count(*) FROM life_roles").fetchone()[0]),
            "life_threads": int(self.connection.execute("SELECT count(*) FROM life_threads").fetchone()[0]),
            "life_events": int(self.connection.execute("SELECT count(*) FROM life_events").fetchone()[0]),
            "pending_proactive": int(self.connection.execute(
                "SELECT count(*) FROM proactive_intents WHERE status='pending'"
            ).fetchone()[0]),
        }

    def backup(self, destination: str | Path) -> Path:
        target = Path(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        output = sqlite3.connect(target)
        try:
            self.connection.backup(output)
        finally:
            output.close()
        check = sqlite3.connect(target)
        try:
            integrity = check.execute("PRAGMA integrity_check").fetchone()[0]
        finally:
            check.close()
        if integrity != "ok":
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

    def bootstrap_life(
        self,
        role_id: str,
        invariant_digest: str,
        timezone_name: str,
        threads: list[dict[str, Any]],
        actors: list[dict[str, Any]],
        confirmed: bool = False,
    ) -> None:
        ZoneInfo(timezone_name)
        if not threads:
            raise StoreError("life bootstrap requires at least one thread")
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            self.connection.execute(
                "INSERT INTO life_roles(role_id,invariant_digest,timezone,status,created_at) VALUES(?,?,?,?,?)",
                (role_id, invariant_digest, timezone_name, "enabled" if confirmed else "draft", now),
            )
            for actor in actors:
                self.connection.execute(
                    "INSERT INTO life_actors(actor_id,role_id,display_name,relationship,motivation,stance,next_action,next_action_at) "
                    "VALUES(?,?,?,?,?,?,?,?)",
                    (
                        actor["actor_id"], role_id, actor["name"], actor["relationship"],
                        actor["motivation"], actor["stance"], actor.get("next_action") or None,
                        actor.get("next_action_at") or None,
                    ),
                )
            actor_ids = {str(actor["actor_id"]) for actor in actors}
            for thread in threads:
                linked = tuple(str(value) for value in thread.get("actor_ids") or ())
                if not set(linked).issubset(actor_ids):
                    raise StoreError("thread references an unknown actor")
                self.connection.execute(
                    "INSERT INTO life_threads(thread_id,role_id,goal,pressure,next_decision_at,allowed_severity) "
                    "VALUES(?,?,?,?,?,?)",
                    (
                        thread["thread_id"], role_id, thread["goal"], int(thread.get("pressure", 0)),
                        thread["next_decision_at"], thread.get("allowed_severity", "ordinary"),
                    ),
                )
                for actor_id in linked:
                    self.connection.execute(
                        "INSERT INTO life_thread_actors(thread_id,actor_id) VALUES(?,?)",
                        (thread["thread_id"], actor_id),
                    )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def confirm_life(self, role_id: str) -> None:
        with self.connection:
            changed = self.connection.execute(
                "UPDATE life_roles SET status='enabled' WHERE role_id=? AND status='draft'",
                (role_id,),
            ).rowcount
            if changed != 1:
                raise StoreError("life role is missing or already confirmed")

    def enqueue_life_wake(self, wake: LifeWake) -> None:
        role = self.connection.execute(
            "SELECT status FROM life_roles WHERE role_id=?", (wake.role_id,)
        ).fetchone()
        if role is None or role["status"] != "enabled":
            raise StoreError("life role is not enabled")
        with self.connection:
            self.connection.execute(
                "INSERT OR IGNORE INTO life_wakes(wake_id,role_id,due_at,reason,source_event_id) VALUES(?,?,?,?,?)",
                (wake.wake_id, wake.role_id, wake.due_at, wake.reason, wake.source_event_id or None),
            )

    def ensure_daily_wakes(self, role_id: str, local_date: str, due_times: tuple[str, str]) -> None:
        if len(due_times) != 2:
            raise StoreError("exactly two daily wake times are required")
        for index, due_at in enumerate(due_times, 1):
            self.enqueue_life_wake(
                LifeWake(f"daily:{role_id}:{local_date}:{index}", role_id, due_at, "scheduled")
            )

    def coalesce_overdue_wakes(self, role_id: str, now: str) -> int:
        rows = self.connection.execute(
            "SELECT wake_id FROM life_wakes WHERE role_id=? AND status='pending' AND due_at<=? "
            "ORDER BY due_at DESC",
            (role_id, now),
        ).fetchall()
        if len(rows) <= 1:
            return 0
        keep = rows[0]["wake_id"]
        with self.connection:
            changed = self.connection.execute(
                "UPDATE life_wakes SET status='skipped',eligibility_reason='coalesced_long_gap' "
                "WHERE role_id=? AND status='pending' AND due_at<=? AND wake_id<>?",
                (role_id, now, keep),
            ).rowcount
        return int(changed)

    def claim_life_wake(self, now: str) -> dict[str, Any] | None:
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            row = self.connection.execute(
                "SELECT w.* FROM life_wakes w JOIN life_roles r ON r.role_id=w.role_id "
                "WHERE w.status IN ('pending','failed') AND w.due_at<=? AND r.status='enabled' "
                "ORDER BY w.due_at,w.wake_id LIMIT 1",
                (now,),
            ).fetchone()
            if row is None:
                self.connection.commit()
                return None
            changed = self.connection.execute(
                "UPDATE life_wakes SET status='processing',attempts=attempts+1,last_error=NULL "
                "WHERE wake_id=? AND status=?",
                (row["wake_id"], row["status"]),
            ).rowcount
            if changed != 1:
                raise StoreError("stale life wake claim")
            self.connection.commit()
            return dict(self.connection.execute(
                "SELECT * FROM life_wakes WHERE wake_id=?", (row["wake_id"],)
            ).fetchone())
        except Exception:
            self.connection.rollback()
            raise

    def life_request(self, wake_row: dict[str, Any]) -> LifeAdvanceRequest:
        role = self.connection.execute(
            "SELECT * FROM life_roles WHERE role_id=?", (wake_row["role_id"],)
        ).fetchone()
        if role is None:
            raise StoreError("life role is missing")
        thread_rows = self.connection.execute(
            "SELECT * FROM life_threads WHERE role_id=? AND status='active' ORDER BY pressure DESC,thread_id LIMIT 8",
            (wake_row["role_id"],),
        ).fetchall()
        threads: list[LifeThreadSnapshot] = []
        actor_ids: set[str] = set()
        for row in thread_rows:
            linked = tuple(item["actor_id"] for item in self.connection.execute(
                "SELECT actor_id FROM life_thread_actors WHERE thread_id=? ORDER BY actor_id", (row["thread_id"],)
            ).fetchall())
            actor_ids.update(linked)
            recent = tuple(item["event_id"] for item in self.connection.execute(
                "SELECT event_id FROM life_events WHERE thread_id=? AND canon_status='private_committed' "
                "ORDER BY occurred_at DESC LIMIT 4", (row["thread_id"],)
            ).fetchall())
            threads.append(LifeThreadSnapshot(
                row["thread_id"], row["goal"], int(row["pressure"]), row["next_decision_at"],
                linked, recent, row["last_event_at"] or "", row["allowed_severity"],
            ))
        actors: list[LifeActorSnapshot] = []
        for actor_id in sorted(actor_ids):
            row = self.connection.execute(
                "SELECT * FROM life_actors WHERE actor_id=? AND role_id=?", (actor_id, wake_row["role_id"])
            ).fetchone()
            if row:
                actors.append(LifeActorSnapshot(
                    row["actor_id"], row["display_name"], row["relationship"], row["motivation"],
                    row["stance"], row["next_action"] or "", row["next_action_at"] or "",
                ))
        recent_events = tuple(item["summary"] for item in self.connection.execute(
            "SELECT summary FROM life_events WHERE role_id=? AND canon_status='private_committed' "
            "ORDER BY occurred_at DESC LIMIT 6", (wake_row["role_id"],)
        ).fetchall())
        wake = LifeWake(
            wake_row["wake_id"], wake_row["role_id"], wake_row["due_at"], wake_row["reason"],
            wake_row.get("source_event_id") or "",
        )
        return LifeAdvanceRequest(wake, role["invariant_digest"], tuple(threads), tuple(actors), recent_events, ())

    def skip_life_wake(self, wake_id: str, reason: str) -> None:
        with self.connection:
            changed = self.connection.execute(
                "UPDATE life_wakes SET status='skipped',eligibility_reason=? WHERE wake_id=? AND status='processing'",
                (reason[:128], wake_id),
            ).rowcount
            if changed != 1:
                raise StoreError("stale life wake skip")

    def fail_life_wake(self, wake_id: str, error: str) -> None:
        with self.connection:
            changed = self.connection.execute(
                "UPDATE life_wakes SET status='failed',last_error=? WHERE wake_id=? AND status='processing'",
                (error[:128], wake_id),
            ).rowcount
            if changed != 1:
                raise StoreError("stale life wake failure")

    @staticmethod
    def _normalized_event(text: str) -> str:
        return "".join(text.lower().split())

    def commit_life_advance(
        self, wake_id: str, proposal: LifeAdvanceProposal, eligibility_reason: str
    ) -> None:
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            wake = self.connection.execute(
                "SELECT * FROM life_wakes WHERE wake_id=?", (wake_id,)
            ).fetchone()
            if wake is None or wake["status"] != "processing":
                raise StoreError("stale life advance commit")
            thread = self.connection.execute(
                "SELECT * FROM life_threads WHERE thread_id=? AND role_id=?",
                (proposal.thread_id, wake["role_id"]),
            ).fetchone()
            if thread is None:
                raise StoreError("life proposal references an unknown thread")
            if proposal.severity == "major" and thread["allowed_severity"] != "major":
                raise StoreError("major event exceeds the thread envelope")
            known_actors = {row["actor_id"] for row in self.connection.execute(
                "SELECT actor_id FROM life_actors WHERE role_id=?", (wake["role_id"],)
            ).fetchall()}
            if not set(proposal.actor_ids).issubset(known_actors):
                raise StoreError("life proposal references an unknown actor")
            if any(update.actor_id not in known_actors for update in proposal.actor_updates):
                raise StoreError("actor update references an unknown actor")
            known_causes = {row["event_id"] for row in self.connection.execute(
                "SELECT event_id FROM life_events WHERE role_id=?", (wake["role_id"],)
            ).fetchall()}
            if not set(proposal.cause_event_ids).issubset(known_causes):
                raise StoreError("life proposal references an unknown cause")
            recent = self.connection.execute(
                "SELECT summary FROM life_events WHERE role_id=? ORDER BY occurred_at DESC LIMIT 20",
                (wake["role_id"],),
            ).fetchall()
            normalized = self._normalized_event(proposal.event_summary)
            if any(self._normalized_event(row["summary"]) == normalized for row in recent):
                raise StoreError("duplicate life event")
            if proposal.thread_status == "active" and proposal.next_decision_at <= proposal.occurred_at:
                raise StoreError("active thread requires a future decision time")
            deception_json = None
            if proposal.deception:
                deception_json = json.dumps(proposal.deception.__dict__, ensure_ascii=False)
            self.connection.execute(
                "INSERT INTO life_events(event_id,role_id,wake_id,thread_id,occurred_at,event_kind,severity,"
                "causal_basis,role_action,summary,consequence,actor_ids_json,cause_event_ids_json,disclosure,deception_json) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    proposal.event_id, wake["role_id"], wake_id, proposal.thread_id, proposal.occurred_at,
                    proposal.event_kind, proposal.severity, proposal.causal_basis, proposal.role_action,
                    proposal.event_summary, proposal.consequence, json.dumps(proposal.actor_ids),
                    json.dumps(proposal.cause_event_ids), proposal.disclosure, deception_json,
                ),
            )
            self.connection.execute(
                "UPDATE life_threads SET status=?,pressure=?,next_decision_at=?,last_event_id=?,last_event_at=?,"
                "version=version+1 WHERE thread_id=?",
                (
                    proposal.thread_status, proposal.thread_pressure, proposal.next_decision_at,
                    proposal.event_id, proposal.occurred_at, proposal.thread_id,
                ),
            )
            for update in proposal.actor_updates:
                self.connection.execute(
                    "UPDATE life_actors SET stance=?,next_action=?,next_action_at=?,version=version+1 "
                    "WHERE actor_id=? AND role_id=?",
                    (update.stance, update.next_action, update.next_action_at, update.actor_id, wake["role_id"]),
                )
            if proposal.proactive_intent:
                role = self.connection.execute(
                    "SELECT timezone FROM life_roles WHERE role_id=?", (wake["role_id"],)
                ).fetchone()
                local_date = datetime.fromisoformat(proposal.occurred_at.replace("Z", "+00:00")).astimezone(
                    ZoneInfo(role["timezone"])
                ).date().isoformat()
                self.connection.execute(
                    "INSERT INTO proactive_intents(intent_id,role_id,source_event_id,local_date,reason,"
                    "disclosure_hint,material_change) VALUES(?,?,?,?,?,?,1)",
                    (
                        "intent:" + proposal.event_id, wake["role_id"], proposal.event_id, local_date,
                        proposal.proactive_intent.reason, proposal.proactive_intent.disclosure_hint,
                    ),
                )
            self.connection.execute(
                "UPDATE life_wakes SET status='done',eligibility_reason=?,last_error=NULL "
                "WHERE wake_id=? AND status='processing'",
                (eligibility_reason[:128], wake_id),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def stage_proactive_text(self, intent_id: str, chat_id: str, text: str) -> int | None:
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            intent = self.connection.execute(
                "SELECT i.*,r.max_proactive_per_day,r.proactive_unanswered,r.last_proactive_event_id "
                "FROM proactive_intents i JOIN life_roles r ON r.role_id=i.role_id WHERE i.intent_id=?",
                (intent_id,),
            ).fetchone()
            if intent is None or intent["status"] != "pending":
                raise StoreError("proactive intent is not pending")
            sent_count = int(self.connection.execute(
                "SELECT count(*) FROM proactive_intents WHERE role_id=? AND local_date=? "
                "AND status IN ('staged','delivered')",
                (intent["role_id"], intent["local_date"]),
            ).fetchone()[0])
            event = self.connection.execute(
                "SELECT cause_event_ids_json FROM life_events WHERE event_id=?", (intent["source_event_id"],)
            ).fetchone()
            causes = set(json.loads(event["cause_event_ids_json"]))
            suppression = ""
            if sent_count >= int(intent["max_proactive_per_day"]):
                suppression = "daily_limit"
            elif intent["proactive_unanswered"] and intent["last_proactive_event_id"] not in causes:
                suppression = "unanswered_without_material_progress"
            if suppression:
                self.connection.execute(
                    "UPDATE proactive_intents SET status='suppressed',suppressed_reason=? WHERE intent_id=?",
                    (suppression, intent_id),
                )
                self.connection.commit()
                return None
            key = "proactive:" + intent_id
            self.connection.execute(
                "INSERT INTO proactive_outbox(intent_id,chat_id,reply_text,idempotency_key,status) "
                "VALUES(?,?,?,?,'pending')", (intent_id, chat_id, text, key),
            )
            outbox_id = int(self.connection.execute("SELECT last_insert_rowid()").fetchone()[0])
            self.connection.execute(
                "UPDATE proactive_intents SET status='staged' WHERE intent_id=?", (intent_id,)
            )
            self.connection.commit()
            return outbox_id
        except Exception:
            self.connection.rollback()
            raise

    def claim_proactive_outbox(self) -> dict[str, Any] | None:
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            row = self.connection.execute(
                "SELECT * FROM proactive_outbox WHERE status IN ('pending','failed') ORDER BY id LIMIT 1"
            ).fetchone()
            if row is None:
                self.connection.commit()
                return None
            changed = self.connection.execute(
                "UPDATE proactive_outbox SET status='sending',attempts=attempts+1,last_error=NULL "
                "WHERE id=? AND status=?", (row["id"], row["status"]),
            ).rowcount
            if changed != 1:
                raise StoreError("stale proactive outbox claim")
            self.connection.commit()
            return dict(self.connection.execute(
                "SELECT * FROM proactive_outbox WHERE id=?", (row["id"],)
            ).fetchone())
        except Exception:
            self.connection.rollback()
            raise

    def fail_proactive_outbox(self, outbox_id: int, error: str) -> None:
        with self.connection:
            changed = self.connection.execute(
                "UPDATE proactive_outbox SET status='failed',last_error=? WHERE id=? AND status='sending'",
                (error[:128], outbox_id),
            ).rowcount
            if changed != 1:
                raise StoreError("stale proactive outbox failure")

    def commit_proactive_delivery(self, outbox_id: int, receipt: DeliveryReceipt) -> None:
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            row = self.connection.execute(
                "SELECT o.*,i.role_id,i.source_event_id FROM proactive_outbox o "
                "JOIN proactive_intents i ON i.intent_id=o.intent_id WHERE o.id=?", (outbox_id,)
            ).fetchone()
            if row is None or row["status"] != "sending":
                raise StoreError("stale proactive delivery commit")
            if row["idempotency_key"] != receipt.idempotency_key:
                raise StoreError("proactive receipt idempotency mismatch")
            self.connection.execute(
                "UPDATE proactive_outbox SET status='delivered',provider_message_id=? WHERE id=?",
                (receipt.provider_message_id, outbox_id),
            )
            self.connection.execute(
                "UPDATE proactive_intents SET status='delivered' WHERE intent_id=?", (row["intent_id"],)
            )
            self.connection.execute(
                "UPDATE life_roles SET proactive_unanswered=1,last_proactive_event_id=? WHERE role_id=?",
                (row["source_event_id"], row["role_id"]),
            )
            self.connection.execute(
                "INSERT INTO life_disclosures(source_event_id,proactive_outbox_id,provider_message_id,disclosed_at) "
                "VALUES(?,?,?,?)",
                (row["source_event_id"], outbox_id, receipt.provider_message_id,
                 datetime.now(timezone.utc).isoformat(timespec="seconds")),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def note_user_activity(self, role_id: str) -> None:
        with self.connection:
            self.connection.execute(
                "UPDATE life_roles SET proactive_unanswered=0 WHERE role_id=?", (role_id,)
            )

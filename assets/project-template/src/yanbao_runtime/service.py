from __future__ import annotations

from datetime import datetime, timezone

from .contracts import InboundMessage
from .life import WakePolicy
from .ports import ChannelPort, LifePort, ModelPort
from .store import StateStore


class RuntimeService:
    def __init__(self, store: StateStore, model: ModelPort, channel: ChannelPort) -> None:
        self.store = store
        self.model = model
        self.channel = channel

    async def process_one(self) -> bool:
        if not self.store.is_armed():
            return False

        outbox = self.store.claim_outbox()
        if outbox is not None:
            try:
                receipt = await self.channel.send_text(
                    outbox["chat_id"],
                    outbox["reply_text"],
                    outbox["idempotency_key"],
                )
            except Exception as exc:
                self.store.fail_outbox(int(outbox["id"]), type(exc).__name__)
                return True
            self.store.commit_delivery(int(outbox["id"]), receipt)
            return True

        row = self.store.claim_next()
        if row is None:
            proactive = self.store.claim_proactive_outbox()
            if proactive is None:
                return False
            try:
                receipt = await self.channel.send_text(
                    proactive["chat_id"], proactive["reply_text"], proactive["idempotency_key"]
                )
            except Exception as exc:
                self.store.fail_proactive_outbox(int(proactive["id"]), type(exc).__name__)
                return True
            self.store.commit_proactive_delivery(int(proactive["id"]), receipt)
            return True
        message = InboundMessage(
            row["message_id"],
            row["chat_id"],
            row["sender_id"],
            row["message_type"],
            row["content"],
        )
        try:
            proposal = await self.model.generate(message)
        except Exception as exc:
            self.store.fail_inbox(int(row["id"]), type(exc).__name__)
            return True
        self.store.stage(int(row["id"]), proposal)
        return True


class LifeRuntimeService:
    """Advance at most one private life slice for one durable wake."""

    def __init__(self, store: StateStore, life: LifePort, policy: WakePolicy | None = None) -> None:
        self.store = store
        self.life = life
        self.policy = policy or WakePolicy()

    async def process_one(self, now: datetime | None = None) -> bool:
        if not self.store.is_armed():
            return False
        current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        row = self.store.claim_life_wake(current.isoformat(timespec="seconds"))
        if row is None:
            return False
        request = self.store.life_request(row)
        decision = self.policy.evaluate(request, current)
        if not decision.eligible:
            self.store.skip_life_wake(request.wake.wake_id, decision.reason)
            return True
        focused = tuple(
            thread for thread in request.threads if thread.thread_id == decision.thread_id
        )
        if focused:
            request = request.__class__(
                request.wake,
                request.invariant_digest,
                focused,
                request.actors,
                request.recent_private_events,
                request.external_stimuli,
            )
        try:
            proposal = await self.life.advance(request)
            if proposal is None:
                self.store.skip_life_wake(request.wake.wake_id, "no_material_change")
                return True
            if proposal.thread_id != decision.thread_id:
                raise ValueError("life proposal changed the selected thread")
            self.store.commit_life_advance(request.wake.wake_id, proposal, decision.reason)
        except Exception as exc:
            self.store.fail_life_wake(request.wake.wake_id, type(exc).__name__)
        return True

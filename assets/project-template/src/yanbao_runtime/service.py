from __future__ import annotations

from .contracts import InboundMessage
from .ports import ChannelPort, ModelPort
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
            return False
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


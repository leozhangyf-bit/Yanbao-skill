from __future__ import annotations

from typing import Protocol

from .contracts import (
    DeliveryReceipt,
    InboundMessage,
    LifeAdvanceProposal,
    LifeAdvanceRequest,
    TurnProposal,
)


class ModelPort(Protocol):
    async def generate(self, message: InboundMessage) -> TurnProposal: ...


class ChannelPort(Protocol):
    async def send_text(
        self, chat_id: str, text: str, idempotency_key: str
    ) -> DeliveryReceipt: ...


class LifePort(Protocol):
    async def advance(self, request: LifeAdvanceRequest) -> LifeAdvanceProposal | None: ...

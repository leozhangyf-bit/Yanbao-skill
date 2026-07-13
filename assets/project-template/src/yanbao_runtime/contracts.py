from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


class ContractError(ValueError):
    pass


def _required_text(name: str, value: object, *, limit: int = 4000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ContractError(f"{name} must be non-empty text within {limit} characters")
    return value


@dataclass(frozen=True)
class InboundMessage:
    message_id: str
    chat_id: str
    sender_id: str
    message_type: str
    content: str

    def __post_init__(self) -> None:
        _required_text("message_id", self.message_id, limit=256)
        _required_text("chat_id", self.chat_id, limit=256)
        _required_text("sender_id", self.sender_id, limit=256)
        if self.message_type not in {"text", "image"}:
            raise ContractError("message_type must be text or image")
        _required_text("content", self.content)


@dataclass(frozen=True)
class TurnProposal:
    reply_text: str
    candidate_events: tuple[str, ...]

    def __post_init__(self) -> None:
        _required_text("reply_text", self.reply_text)
        if len(self.candidate_events) > 8:
            raise ContractError("candidate_events exceeds 8")
        for event in self.candidate_events:
            _required_text("candidate_event", event, limit=1000)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "TurnProposal":
        if set(value) != {"reply_text", "candidate_events"}:
            raise ContractError("turn proposal fields are invalid")
        events = value["candidate_events"]
        if not isinstance(events, list) or not all(isinstance(item, str) for item in events):
            raise ContractError("candidate_events must be a string array")
        return cls(reply_text=value["reply_text"], candidate_events=tuple(events))


@dataclass(frozen=True)
class DeliveryReceipt:
    provider_message_id: str
    idempotency_key: str

    def __post_init__(self) -> None:
        _required_text("provider_message_id", self.provider_message_id, limit=256)
        _required_text("idempotency_key", self.idempotency_key, limit=256)


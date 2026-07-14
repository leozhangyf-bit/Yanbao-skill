from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
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


def _iso_timestamp(name: str, value: object) -> str:
    text = _required_text(name, value, limit=64)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError(f"{name} must be an ISO timestamp") from exc
    if parsed.tzinfo is None:
        raise ContractError(f"{name} must include a timezone")
    return text


@dataclass(frozen=True)
class LifeWake:
    wake_id: str
    role_id: str
    due_at: str
    reason: str
    source_event_id: str = ""

    def __post_init__(self) -> None:
        _required_text("wake_id", self.wake_id, limit=256)
        _required_text("role_id", self.role_id, limit=256)
        _iso_timestamp("due_at", self.due_at)
        if self.reason not in {"scheduled", "reconnect", "deadline", "inquiry", "external"}:
            raise ContractError("life wake reason is invalid")
        if self.source_event_id:
            _required_text("source_event_id", self.source_event_id, limit=256)


@dataclass(frozen=True)
class LifeThreadSnapshot:
    thread_id: str
    goal: str
    pressure: int
    next_decision_at: str
    actor_ids: tuple[str, ...] = ()
    recent_event_ids: tuple[str, ...] = ()
    last_event_at: str = ""
    allowed_severity: str = "ordinary"

    def __post_init__(self) -> None:
        _required_text("thread_id", self.thread_id, limit=256)
        _required_text("goal", self.goal, limit=1000)
        if not isinstance(self.pressure, int) or not 0 <= self.pressure <= 5:
            raise ContractError("thread pressure must be between 0 and 5")
        _iso_timestamp("next_decision_at", self.next_decision_at)
        if self.last_event_at:
            _iso_timestamp("last_event_at", self.last_event_at)
        if self.allowed_severity not in {"ordinary", "major"}:
            raise ContractError("allowed severity is invalid")
        for actor_id in self.actor_ids:
            _required_text("actor_id", actor_id, limit=256)
        for event_id in self.recent_event_ids:
            _required_text("recent_event_id", event_id, limit=256)


@dataclass(frozen=True)
class LifeActorSnapshot:
    actor_id: str
    name: str
    relationship: str
    motivation: str
    stance: str
    next_action: str = ""
    next_action_at: str = ""

    def __post_init__(self) -> None:
        _required_text("actor_id", self.actor_id, limit=256)
        _required_text("actor_name", self.name, limit=160)
        _required_text("actor_relationship", self.relationship, limit=500)
        _required_text("actor_motivation", self.motivation, limit=1000)
        _required_text("actor_stance", self.stance, limit=500)
        if self.next_action:
            _required_text("next_action", self.next_action, limit=1000)
            _iso_timestamp("next_action_at", self.next_action_at)


@dataclass(frozen=True)
class LifeAdvanceRequest:
    wake: LifeWake
    invariant_digest: str
    threads: tuple[LifeThreadSnapshot, ...]
    actors: tuple[LifeActorSnapshot, ...]
    recent_private_events: tuple[str, ...] = ()
    external_stimuli: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _required_text("invariant_digest", self.invariant_digest, limit=256)
        if len(self.threads) > 8 or len(self.actors) > 16:
            raise ContractError("life advance request exceeds its bounded snapshot")
        for text in self.recent_private_events:
            _required_text("recent_private_event", text, limit=1000)
        for text in self.external_stimuli:
            _required_text("external_stimulus", text, limit=1000)


@dataclass(frozen=True)
class ActorUpdate:
    actor_id: str
    stance: str
    next_action: str
    next_action_at: str

    def __post_init__(self) -> None:
        _required_text("actor_id", self.actor_id, limit=256)
        _required_text("actor_stance", self.stance, limit=500)
        _required_text("actor_next_action", self.next_action, limit=1000)
        _iso_timestamp("actor_next_action_at", self.next_action_at)


@dataclass(frozen=True)
class BoundedDeception:
    truth: str
    cover_story: str
    motive: str
    exposure_pressure: int

    def __post_init__(self) -> None:
        _required_text("deception_truth", self.truth, limit=1000)
        _required_text("deception_cover_story", self.cover_story, limit=1000)
        _required_text("deception_motive", self.motive, limit=500)
        if not isinstance(self.exposure_pressure, int) or not 1 <= self.exposure_pressure <= 5:
            raise ContractError("exposure pressure must be between 1 and 5")


@dataclass(frozen=True)
class ProactiveIntentProposal:
    reason: str
    disclosure_hint: str
    material_change: bool = True

    def __post_init__(self) -> None:
        _required_text("proactive_reason", self.reason, limit=500)
        _required_text("disclosure_hint", self.disclosure_hint, limit=1000)
        if self.material_change is not True:
            raise ContractError("proactive intent must represent a material change")


@dataclass(frozen=True)
class LifeAdvanceProposal:
    event_id: str
    occurred_at: str
    thread_id: str
    event_kind: str
    severity: str
    causal_basis: str
    role_action: str
    event_summary: str
    consequence: str
    actor_ids: tuple[str, ...]
    cause_event_ids: tuple[str, ...]
    thread_status: str
    thread_pressure: int
    next_decision_at: str
    disclosure: str
    actor_updates: tuple[ActorUpdate, ...] = ()
    deception: BoundedDeception | None = None
    proactive_intent: ProactiveIntentProposal | None = None

    def __post_init__(self) -> None:
        _required_text("event_id", self.event_id, limit=256)
        _iso_timestamp("occurred_at", self.occurred_at)
        _required_text("thread_id", self.thread_id, limit=256)
        if self.event_kind not in {
            "choice", "actor_action", "consequence", "opportunity", "conflict", "reversal"
        }:
            raise ContractError("life event kind is invalid")
        if self.severity not in {"ordinary", "major"}:
            raise ContractError("life event severity is invalid")
        _required_text("causal_basis", self.causal_basis, limit=1000)
        _required_text("role_action", self.role_action, limit=1000)
        _required_text("event_summary", self.event_summary, limit=1000)
        _required_text("consequence", self.consequence, limit=1000)
        if self.thread_status not in {"active", "paused", "resolved"}:
            raise ContractError("thread status is invalid")
        if not isinstance(self.thread_pressure, int) or not 0 <= self.thread_pressure <= 5:
            raise ContractError("thread pressure must be between 0 and 5")
        _iso_timestamp("next_decision_at", self.next_decision_at)
        if self.disclosure not in {"private", "shareable", "should_contact"}:
            raise ContractError("disclosure posture is invalid")
        if len(self.actor_ids) > 8 or len(self.cause_event_ids) > 8 or len(self.actor_updates) > 8:
            raise ContractError("life proposal exceeds bounded references")
        if self.disclosure == "should_contact" and self.proactive_intent is None:
            raise ContractError("should_contact requires a proactive intent")
        if self.disclosure != "should_contact" and self.proactive_intent is not None:
            raise ContractError("proactive intent requires should_contact disclosure")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "LifeAdvanceProposal":
        expected = {
            "event_id", "occurred_at", "thread_id", "event_kind", "severity",
            "causal_basis", "role_action", "event_summary", "consequence",
            "actor_ids", "cause_event_ids", "thread_status", "thread_pressure",
            "next_decision_at", "disclosure", "actor_updates", "deception",
            "proactive_intent",
        }
        if set(value) != expected:
            raise ContractError("life advance proposal fields are invalid")
        actor_ids = value["actor_ids"]
        cause_ids = value["cause_event_ids"]
        updates = value["actor_updates"]
        if not isinstance(actor_ids, list) or not all(isinstance(item, str) for item in actor_ids):
            raise ContractError("actor_ids must be a string array")
        if not isinstance(cause_ids, list) or not all(isinstance(item, str) for item in cause_ids):
            raise ContractError("cause_event_ids must be a string array")
        if not isinstance(updates, list) or not all(isinstance(item, Mapping) for item in updates):
            raise ContractError("actor_updates must be an object array")
        actor_updates: list[ActorUpdate] = []
        for item in updates:
            if set(item) != {"actor_id", "stance", "next_action", "next_action_at"}:
                raise ContractError("actor update fields are invalid")
            actor_updates.append(ActorUpdate(**item))
        deception_value = value["deception"]
        deception = None
        if deception_value is not None:
            if not isinstance(deception_value, Mapping) or set(deception_value) != {
                "truth", "cover_story", "motive", "exposure_pressure"
            }:
                raise ContractError("deception fields are invalid")
            deception = BoundedDeception(**deception_value)
        proactive_value = value["proactive_intent"]
        proactive = None
        if proactive_value is not None:
            if not isinstance(proactive_value, Mapping) or set(proactive_value) != {
                "reason", "disclosure_hint", "material_change"
            }:
                raise ContractError("proactive intent fields are invalid")
            proactive = ProactiveIntentProposal(**proactive_value)
        return cls(
            event_id=value["event_id"], occurred_at=value["occurred_at"],
            thread_id=value["thread_id"], event_kind=value["event_kind"],
            severity=value["severity"], causal_basis=value["causal_basis"],
            role_action=value["role_action"], event_summary=value["event_summary"],
            consequence=value["consequence"], actor_ids=tuple(actor_ids),
            cause_event_ids=tuple(cause_ids), thread_status=value["thread_status"],
            thread_pressure=value["thread_pressure"], next_decision_at=value["next_decision_at"],
            disclosure=value["disclosure"], actor_updates=tuple(actor_updates),
            deception=deception, proactive_intent=proactive,
        )

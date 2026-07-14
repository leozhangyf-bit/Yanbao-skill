from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .contracts import LifeAdvanceRequest, LifeThreadSnapshot


def _parse(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class WakeDecision:
    eligible: bool
    reason: str
    thread_id: str = ""


class WakePolicy:
    """Choose whether a wake deserves one background model call."""

    def __init__(self, pressure_threshold: int = 3, agency_floor_hours: int = 36) -> None:
        self.pressure_threshold = pressure_threshold
        self.agency_floor = timedelta(hours=agency_floor_hours)

    def evaluate(self, request: LifeAdvanceRequest, now: datetime) -> WakeDecision:
        current = now.astimezone(timezone.utc)
        active = list(request.threads)
        if not active:
            return WakeDecision(False, "no_active_threads")
        due = [thread for thread in active if _parse(thread.next_decision_at) <= current]
        if due:
            selected = max(due, key=lambda item: (item.pressure, item.next_decision_at))
            return WakeDecision(True, "decision_due", selected.thread_id)
        pressured = [thread for thread in active if thread.pressure >= self.pressure_threshold]
        if pressured:
            selected = max(pressured, key=lambda item: item.pressure)
            return WakeDecision(True, "pressure_threshold", selected.thread_id)
        stalled = [thread for thread in active if self._stalled(thread, current)]
        if stalled:
            selected = max(stalled, key=lambda item: item.pressure)
            return WakeDecision(True, "agency_floor", selected.thread_id)
        return WakeDecision(False, "no_material_pressure")

    def _stalled(self, thread: LifeThreadSnapshot, now: datetime) -> bool:
        if not thread.last_event_at:
            return False
        return now - _parse(thread.last_event_at) >= self.agency_floor

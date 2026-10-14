"""Friction radar — combines overdue journey events, past-SLA requests and
(opt-in, consent-gated) pulse dips into one explainable risk score.

Deterministic weights, stated openly:
  +0.25 per overdue journey event   (the journey engine's blockers)
  +0.15 per open request past SLA
  +0.10 single pulse dip            (only with explicit consent; tie-breaker)
Capped at 1.0.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.services.data import DataStore
from app.core.journey_engine import journey_state


@dataclass
class Flag:
    kind: str            # overdue_event | overdue_request | pulse_dip
    detail: str
    weight: float
    owner: str | None = None
    event: str | None = None


@dataclass
class FrictionReport:
    employee_id: str
    day: int
    risk: float
    flags: list[Flag] = field(default_factory=list)

    @property
    def worst(self) -> Flag | None:
        return max(self.flags, key=lambda f: f.weight) if self.flags else None


def pulse_dip(pulse_rows: list[tuple], consented: bool) -> bool:
    """Any consented score <= 2 within the last two journey days."""
    if not consented:
        return False
    recent = [int(score) for _day, score, consent in pulse_rows
              if consent and int(score) <= 2]
    return bool(recent)


def scan(store: DataStore, employee_id: str, today: int | None = None,
         consented: bool | None = None) -> FrictionReport:
    from app.core.consent import ConsentStore  # local import avoids a cycle at module load

    settings_day = today
    day = store.journey_day(employee_id) if settings_day is None else settings_day
    if consented is None:
        consented = ConsentStore.default().is_opted_in(employee_id)

    flags: list[Flag] = []

    state = journey_state(store, employee_id, today=day)
    for b in state.blockers:
        flags.append(Flag(kind="overdue_event", weight=0.25, event=b.event,
                          detail=f"{b.label}: due day {b.due_day}, {b.days_overdue} day(s) overdue",
                          owner=b.owner.name))

    reqs = store.requests_for(employee_id)
    for _, r in reqs.iterrows():
        if str(r.get("status", "open")).lower() != "open":
            continue
        days_open = day - int(r.get("created_day", 0))
        sla = int(r.get("sla_days", 0))
        if days_open > sla:
            flags.append(Flag(kind="overdue_request", weight=0.15,
                              detail=f"{r.get('type', 'request')} open {days_open}d vs SLA {sla}d",
                              owner=str(r.get("owner", "")) or None))

    pulse = store.pulse_for(employee_id)
    if consented and not pulse.empty:
        rows = [(int(r["day"]), int(r["score"]), bool(r.get("consent", False))) for _, r in pulse.iterrows()]
        if pulse_dip(rows, consented):
            flags.append(Flag(kind="pulse_dip", weight=0.1,
                              detail="Consented pulse dipped to 2/5 or lower — gentle check-in suggested"))

    risk = min(1.0, sum(f.weight for f in flags))
    return FrictionReport(employee_id=employee_id, day=day, risk=risk, flags=flags)

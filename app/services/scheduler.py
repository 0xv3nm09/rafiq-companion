"""Proactive sweeps — the engine that acts before the employee has to ask.

Employee-first rule: every blocker is noticed to the employee before any human
is involved; only persistent stalls (>= ESCALATE_AFTER days overdue) produce a
handoff card to the named owner. Fully idempotent per (employee, event, day).
"""
from __future__ import annotations

import asyncio
import logging

from app.config import get_settings
from app.core.consent import AuditLog
from app.core.friction import scan
from app.services.data import DataStore
from app.services.notify import HandoffStore, NoticeStore

log = logging.getLogger("rafiq.sweep")


def sweep_once(store: DataStore) -> dict:
    settings = get_settings()
    notices, notices_deduped, escalations = 0, 0, 0
    notice_store, handoff_store = NoticeStore(), HandoffStore()

    for employee_id in store.employees["employee_id"]:
        report = scan(store, str(employee_id))
        for flag in report.flags:
            if flag.kind != "overdue_event":
                continue
            event_key = flag.event or flag.detail.split(":")[0]
            display = flag.detail.split(":")[0]
            day = report.day
            if notice_store.add_deduped(
                str(employee_id), f"{event_key}@{day}", day,
                kind="blocker", title=f"Still waiting: {display}",
                detail=f"{flag.detail} — I can chase {flag.owner or 'the owner'} for you.",
            ) is not None:
                notices += 1
                AuditLog().append(str(employee_id), "sweep_notice", {"flag": flag.detail})
            else:
                notices_deduped += 1
            if flag.owner and (report.risk >= 0.25):
                blocker_days = _days_overdue(flag.detail)
                if blocker_days is not None and blocker_days >= settings.escalate_after:
                    existing = handoff_store.open_for(str(employee_id), event_key)
                    if existing is None:
                        card = handoff_store.create(_build_card(store, str(employee_id), event_key,
                                                                flag, day, report.risk))
                        if card:
                            escalations += 1
                            AuditLog().append(str(employee_id), "escalated_handoff",
                                              {"handoff_id": card.handoff_id, "owner": flag.owner})
    return {"employees_scanned": int(len(store.employees)), "notices_new": notices,
            "notices_deduped": notices_deduped, "escalations": escalations}


def _days_overdue(detail: str) -> int | None:
    import re
    m = re.search(r"(\d+) day\(s\) overdue", detail)
    return int(m.group(1)) if m else None


def _build_card(store: DataStore, employee_id: str, event_key: str, flag, day: int, risk: float):
    from app.schemas.handoff import HandoffCard
    from app.schemas.common import Owner
    reqs = store.requests_for(employee_id)
    tried = [f"Auto-reminder to {r.get('owner', 'owner')} on day {day - 1}"
             for _, r in reqs.iterrows() if str(r.get("status")) == "open"] or ["Employee self-check"]
    return HandoffCard(
        employee_id=employee_id,
        event_key=event_key,
        stage=f"day-{day}",
        blocker=f"{flag.detail}",
        tried=tried[:3],
        suggested_owner=Owner(name=flag.owner or "HR Service Desk", role=flag.owner or "HR Service Desk"),
        summary=(f"{employee_id} is stuck: {flag.detail}. "
                 f"Journey-day {day}, friction risk {risk:.2f}. Please advise."),
        created_day=day,
    )


async def run_sweep(store: DataStore) -> dict:
    return await asyncio.to_thread(sweep_once, store)


async def start_background_sweep(store: DataStore) -> asyncio.Task:
    """Periodic sweep independent of any incoming request."""
    settings = get_settings()

    async def _loop() -> None:
        while True:
            try:
                await run_sweep(store)
            except Exception:  # never let the sweep die the app
                log.exception("sweep failed")
            await asyncio.sleep(settings.sweep_interval_hours * 3600)

    return asyncio.create_task(_loop())

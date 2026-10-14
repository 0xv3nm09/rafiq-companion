"""Employee-first notifications and handoff-card stores (file-backed)."""
from __future__ import annotations

import uuid

from app.config import get_settings
from app.core.storage import load_json, save_json
from app.schemas.handoff import HandoffCard


class NoticeStore:
    """Proactive notices the EMPLOYEE sees first — never a manager view."""

    def __init__(self) -> None:
        self.path = get_settings().runtime_dir / "notices.json"

    def add(self, employee_id: str, kind: str, title: str, detail: str, day: int | None = None) -> dict:
        notices = load_json(self.path, [])
        notice = {"id": uuid.uuid4().hex[:8], "employee_id": employee_id, "kind": kind,
                  "title": title, "detail": detail, "day": day,
                  "created_at": _now(), "read": False}
        notices.append(notice)
        save_json(self.path, notices[-2000:])
        return notice

    def already_today(self, employee_id: str, key: str, day: int) -> bool:
        notices = load_json(self.path, [])
        return any(n["employee_id"] == employee_id and n.get("dedupe_key") == key
                   and n.get("day") == day for n in notices)

    def add_deduped(self, employee_id: str, key: str, day: int, **kw) -> dict | None:
        if self.already_today(employee_id, key, day):
            return None
        notice = self.add(employee_id, **kw)
        notices = load_json(self.path, [])
        for n in notices:
            if n["id"] == notice["id"]:
                n["dedupe_key"] = key
        save_json(self.path, notices)
        return notice

    def for_employee(self, employee_id: str, limit: int = 20) -> list[dict]:
        notices = [n for n in load_json(self.path, []) if n["employee_id"] == employee_id]
        return list(reversed(notices[-limit:]))

    def mark_read(self, employee_id: str) -> None:
        notices = load_json(self.path, [])
        for n in notices:
            if n["employee_id"] == employee_id:
                n["read"] = True
        save_json(self.path, notices)


class RequestStore:
    """Requests raised through the companion (runtime; the pack stays read-only)."""

    def __init__(self) -> None:
        self.path = get_settings().runtime_dir / "requests_created.json"

    def create(self, employee_id: str, rtype: str, owner: str, day: int) -> str:
        rows = load_json(self.path, [])
        rid = f"REQ-C{len(rows) + 1:04d}"
        rows.append({"request_id": rid, "employee_id": employee_id, "type": rtype,
                     "created_day": day, "sla_days": 3, "status": "open", "owner": owner,
                     "chased_day": None, "created_at": _now()})
        save_json(self.path, rows)
        return rid

    def chase(self, request_id: str, employee_id: str) -> bool:
        rows = load_json(self.path, [])
        hit = False
        for r in rows:
            if r["request_id"] == request_id and r["employee_id"] == employee_id:
                r["chased_day"] = r.get("created_day")
                hit = True
        save_json(self.path, rows)
        return hit

    def for_employee(self, employee_id: str) -> list[dict]:
        return [r for r in load_json(self.path, []) if r["employee_id"] == employee_id]


class HandoffStore:
    def __init__(self) -> None:
        self.path = get_settings().runtime_dir / "handoffs.json"

    def create(self, card: HandoffCard) -> HandoffCard:
        cards = load_json(self.path, [])
        data = card.model_dump()
        data["handoff_id"] = data.get("handoff_id") or f"H-{uuid.uuid4().hex[:6].upper()}"
        cards.append(data)
        save_json(self.path, cards[-1000:])
        return HandoffCard.model_validate(data)

    def open_for(self, employee_id: str, event: str) -> HandoffCard | None:
        for c in load_json(self.path, []):
            if c["employee_id"] == employee_id and c.get("event_key") == event and c["status"] == "open":
                return HandoffCard.model_validate(c)
        return None

    def get(self, handoff_id: str) -> HandoffCard | None:
        for c in load_json(self.path, []):
            if c["handoff_id"] == handoff_id:
                return HandoffCard.model_validate(c)
        return None

    def for_employee(self, employee_id: str) -> list[HandoffCard]:
        cards = [c for c in load_json(self.path, []) if c["employee_id"] == employee_id]
        return [HandoffCard.model_validate(c) for c in reversed(cards)]

    def open_all(self) -> list[HandoffCard]:
        return [HandoffCard.model_validate(c) for c in load_json(self.path, []) if c["status"] == "open"]

    def update_status(self, handoff_id: str, status: str) -> HandoffCard | None:
        cards = load_json(self.path, [])
        out = None
        for c in cards:
            if c["handoff_id"] == handoff_id:
                c["status"] = status
                out = HandoffCard.model_validate(c)
        save_json(self.path, cards)
        return out


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()

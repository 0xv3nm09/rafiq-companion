"""Employee-owned trust primitives: consent toggles, the audit log, and the
"what we hold about you" view. File-backed under data/runtime/ (gitignored)."""
from __future__ import annotations

from datetime import datetime, timezone

from app.config import get_settings
from app.core.storage import load_json, save_json


class ConsentStore:
    def __init__(self, runtime_dir: Path | None = None) -> None:
        self.path = (runtime_dir or get_settings().runtime_dir) / "consent.json"

    @classmethod
    def default(cls) -> "ConsentStore":
        return cls()

    def _all(self) -> dict:
        return load_json(self.path, {})

    def is_opted_in(self, employee_id: str, kind: str = "pulse") -> bool:
        return bool(self._all().get(employee_id, {}).get(kind, False))

    def set(self, employee_id: str, kind: str, value: bool, day: int | None = None) -> None:
        data = self._all()
        rec = data.setdefault(employee_id, {})
        rec[kind] = bool(value)
        rec[f"{kind}_updated"] = {"value": bool(value), "at": datetime.now(timezone.utc).isoformat(),
                                  "day": day}
        save_json(self.path, data)
        AuditLog().append(employee_id, "consent_changed",
                          {"consent": kind, "value": bool(value)})

    def revoke_and_confirm(self, employee_id: str, kind: str) -> dict:
        self.set(employee_id, kind, False)
        return {"revoked": kind, "message": f"{kind} consent revoked; its signal is excluded from all processing."}


class AuditLog:
    def __init__(self) -> None:
        self.path = get_settings().runtime_dir / "audit.json"

    def append(self, employee_id: str, action: str, detail: dict | None = None) -> None:
        entries = load_json(self.path, [])
        entries.append({
            "ts": datetime.now(timezone.utc).isoformat(),
            "employee_id": employee_id,
            "action": action,
            "detail": detail or {},
        })
        save_json(self.path, entries[-2000:])  # bound the file

    def for_employee(self, employee_id: str, limit: int = 50) -> list[dict]:
        entries = load_json(self.path, [])
        mine = [e for e in entries if e.get("employee_id") == employee_id]
        return list(reversed(mine[-limit:]))


def held_data(store, employee_id: str) -> dict:
    """The employee-visible 'what we hold about you' payload."""
    from app.core.journey_engine import journey_state  # local import: engine imports data, not trust

    emp = store.employee(employee_id) or {}
    state = journey_state(store, employee_id)
    consented = ConsentStore().is_opted_in(employee_id)
    pulse = store.pulse_for(employee_id)
    pulse_rows = [] if pulse.empty else [
        {"day": int(r["day"]), "score": int(r["score"])} for _, r in pulse.iterrows()
    ]
    reqs = store.requests_for(employee_id)
    return {
        "employee": {k: emp.get(k) for k in ("employee_id", "name", "role", "department", "journey", "lang_pref")},
        "journey": {"stage": state.stage, "day": state.day, "blockers": len(state.blockers)},
        "service_requests": 0 if reqs.empty else len(reqs),
        "pulse_entries": len(pulse_rows),
        "pulse_used_for_signals": consented,
        "pulse_note": ("Pulse scores are used in friction signals only while consent is ON."
                       if consented else
                       "Pulse scores are stored but excluded from every signal while consent is OFF."),
        "not_used_for": "performance evaluation or disciplinary decisions — by design and by policy.",
    }

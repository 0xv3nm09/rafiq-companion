"""Rafiq API — every endpoint the UI needs, plus the trust surfaces."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.agents.orchestrator import handle
from app.config import get_settings
from app.core.consent import AuditLog, ConsentStore, held_data
from app.core.journey_engine import journey_state, timeline
from app.services.data import load_store
from app.state import get_store
from app.services.notify import HandoffStore, NoticeStore
from app.services.scheduler import run_sweep, seed_runtime, start_background_sweep

settings = get_settings()

ml = None  # set in lifespan; keeps startup lazy and testable


@asynccontextmanager
async def lifespan(app: FastAPI):
    store = get_store()
    seed_runtime(store)
    task = await start_background_sweep(store)
    yield
    task.cancel()


app = FastAPI(title="Rafiq — Employee AI Companion", version="0.1.0", lifespan=lifespan)


class PulseBody(BaseModel):
    employee_id: str
    score: int
    consent: bool


class ConsentBody(BaseModel):
    employee_id: str
    consent_pulse: bool


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "source": get_store().source, "chunks": len(get_store().policy_chunks)}


@app.post("/ask")
async def ask(body: dict) -> dict:
    from app.schemas.ask import AskRequest
    req = AskRequest(**body)
    resp = await handle(req, get_store())
    return resp.model_dump()


@app.get("/journey/{employee_id}")
async def get_journey(employee_id: str) -> dict:
    store = get_store()
    if store.employee(employee_id) is None:
        raise HTTPException(404, "employee not found")
    return {"state": journey_state(store, employee_id).model_dump(),
            "timeline": [s.model_dump() for s in timeline(store, employee_id)]}


@app.get("/handoff/{handoff_id}")
async def get_handoff(handoff_id: str) -> dict:
    card = HandoffStore().get(handoff_id)
    if card is None:
        raise HTTPException(404, "handoff not found")
    return card.model_dump()


@app.get("/employees")
async def list_employees() -> list[dict]:
    """Demo switcher: the two scenario stars first, then a sample of the cohort.
    Line managers / HRBPs are people rows but not companion users — excluded here."""
    import pandas as pd
    store = get_store()
    df = store.employees
    staff = df[df["journey"].isin(["onboarding", "mobility"])]
    stars = staff[staff["employee_id"].isin(["E0421", "E0422"])]
    rest = staff[~staff["employee_id"].isin(["E0421", "E0422"])].head(40)
    out = []
    for _, r in pd.concat([stars, rest]).iterrows():
        out.append({"employee_id": str(r["employee_id"]),
                    "label": f"{r['employee_id']} · {r['name']} ({r['journey']})"})
    return out


@app.get("/people/managers")
async def list_managers() -> list[dict]:
    store = get_store()
    out = []
    for _, m in store.employees[store.employees["role"] == "Line Manager"].iterrows():
        out.append({"id": str(m["employee_id"]), "name": str(m["name"]),
                    "department": str(m["department"]),
                    "team_size": int(len(store.team_of(str(m["employee_id"]))))})
    return out


@app.get("/people/hrbps")
async def list_hrbps() -> list[dict]:
    store = get_store()
    out = []
    for _, h in store.employees[store.employees["role"] == "HR Business Partner"].iterrows():
        out.append({"id": str(h["employee_id"]), "name": str(h["name"]),
                    "caseload": int(len(store.hrbp_caseload(str(h["employee_id"]))))})
    return out


@app.get("/people/owners")
async def list_owners() -> list[dict]:
    from app.agents.action_agent import SERVICE_OWNERS
    return [{"name": o} for o in SERVICE_OWNERS]


@app.get("/team/{manager_id}")
async def get_team(manager_id: str) -> dict:
    """Manager view — read-only help, never surveillance: NO pulse data here."""
    from app.core.friction import scan
    from app.core.journey_engine import journey_state
    store = get_store()
    mgr = store.person(manager_id)
    if mgr is None or str(mgr.get("role")) != "Line Manager":
        raise HTTPException(404, "manager not found")
    reports = []
    for _, r in store.team_of(manager_id).iterrows():
        eid = str(r["employee_id"])
        state = journey_state(store, eid)
        report = scan(store, eid, consented=False)   # consent-independent: no pulse signal
        reports.append({
            "employee_id": eid, "name": str(r["name"]), "role": str(r["role"]),
            "journey": state.journey.value, "stage": state.stage, "day": state.day,
            "risk": round(report.risk, 2),
            "blockers": [{"label": b.label, "days_overdue": b.days_overdue,
                          "owner": b.owner.name} for b in state.blockers],
        })
    reports.sort(key=lambda x: (-x["risk"], x["name"]))
    return {"manager": {"id": manager_id, "name": str(mgr["name"]),
                        "department": str(mgr["department"])},
            "team_size": len(reports),
            "privacy": "Pulse content is never visible to managers — blockers shown are journey facts.",
            "reports": reports}


@app.get("/queue/{hrbp_id}")
async def get_queue(hrbp_id: str) -> dict:
    """HRBP early-warning queue: only real stalls, each with a summary."""
    from app.core.friction import scan
    from app.core.journey_engine import journey_state
    from app.services.notify import HandoffStore, NoticeStore
    store = get_store()
    hrbp = store.person(hrbp_id)
    if hrbp is None or str(hrbp.get("role")) != "HR Business Partner":
        raise HTTPException(404, "hrbp not found")
    handoffs = HandoffStore()
    flagged = []
    for _, r in store.hrbp_caseload(hrbp_id).iterrows():
        eid = str(r["employee_id"])
        report = scan(store, eid, consented=False)
        if report.risk < 0.25:
            continue
        state = journey_state(store, eid)
        open_card = next((c for c in handoffs.for_employee(eid) if c.status == "open"), None)
        notices = NoticeStore().for_employee(eid, limit=1)
        flagged.append({
            "employee_id": eid, "name": str(r["name"]), "journey": state.journey.value,
            "stage": state.stage, "day": state.day, "risk": round(report.risk, 2),
            "blockers": [{"label": b.label, "days_overdue": b.days_overdue,
                          "owner": b.owner.name} for b in state.blockers],
            "employee_notified": bool(notices),
            "open_handoff_id": open_card.handoff_id if open_card else None,
        })
    flagged.sort(key=lambda x: -x["risk"])
    by_owner: dict[str, int] = {}
    for f in flagged:
        for b in f["blockers"]:
            by_owner[b["owner"]] = by_owner.get(b["owner"], 0) + 1
    return {"hrbp": {"id": hrbp_id, "name": str(hrbp["name"])},
            "caseload": int(len(store.hrbp_caseload(hrbp_id))),
            "flagged": flagged, "blocked_total": len(flagged),
            "stalls_by_owner": by_owner}


@app.post("/handoff/{handoff_id}/status")
async def update_handoff(handoff_id: str, body: dict) -> dict:
    card = HandoffStore().update_status(handoff_id, str(body.get("status", "acknowledged")))
    if card is None:
        raise HTTPException(404, "handoff not found")
    AuditLog().append(card.employee_id, "handoff_status",
                      {"handoff_id": handoff_id, "status": card.status})
    return card.model_dump()


@app.get("/policy/{policy_id}")
async def get_policy(policy_id: str, lang: str = Query("en")) -> list[dict]:
    """Citation drill-down: the exact sections behind an answer."""
    store = get_store()
    chunks = [c for c in store.policy_chunks if c.policy_id == policy_id.upper() and c.lang == lang]
    if not chunks:
        chunks = [c for c in store.policy_chunks if c.policy_id == policy_id.upper()]
    if not chunks:
        raise HTTPException(404, "policy not found")
    return [{"section": c.section, "text": c.text, "title": c.title, "lang": c.lang} for c in chunks]


@app.get("/handoffs")
async def open_handoffs() -> list[dict]:
    return [c.model_dump() for c in HandoffStore().open_all()]


@app.get("/me/data")
async def me_data(employee_id: str = Query(...)) -> dict:
    store = get_store()
    if store.employee(employee_id) is None:
        raise HTTPException(404, "employee not found")
    data = held_data(store, employee_id)
    data["consent"] = {"pulse": ConsentStore().is_opted_in(employee_id)}
    return data


@app.get("/me/audit")
async def me_audit(employee_id: str = Query(...), limit: int = 50) -> list[dict]:
    return AuditLog().for_employee(employee_id, limit)


@app.get("/me/notices")
async def me_notices(employee_id: str = Query(...)) -> list[dict]:
    return NoticeStore().for_employee(employee_id)


@app.post("/me/notices/read")
async def notices_read(body: dict) -> dict:
    NoticeStore().mark_read(str(body.get("employee_id", "")))
    return {"read": True}


@app.post("/pulse")
async def pulse(body: PulseBody) -> dict:
    store = get_store()
    if body.employee_id not in set(store.employees["employee_id"]):
        raise HTTPException(404, "employee not found")
    consent = ConsentStore()
    if body.consent and not consent.is_opted_in(body.employee_id):
        consent.set(body.employee_id, "pulse", True)
    AuditLog().append(body.employee_id, "pulse_submitted",
                      {"score": body.score, "consent": body.consent})
    if not body.consent:
        return {"stored": False,
                "message": "Noted without using it — pulse only influences signals with your consent ON."}
    return {"stored": True, "message": "Thanks — recorded with your consent on file."}


@app.post("/consent")
async def consent(body: ConsentBody) -> dict:
    consent = ConsentStore()
    old = consent.is_opted_in(body.employee_id)
    consent.set(body.employee_id, "pulse", body.consent_pulse)
    if old and not body.consent_pulse:
        return {"consent_pulse": False,
                "message": "Consent revoked. Pulse data is now excluded from every signal."}
    return {"consent_pulse": body.consent_pulse, "message": "Preference saved and logged in your audit log."}


@app.post("/sweep")
async def sweep() -> dict:
    return await run_sweep(get_store())


@app.get("/stalls")
async def stalls() -> dict:
    """Where journeys stall most — aggregate and privacy-safe (no individuals)."""
    from app.core.journey_engine import journey_state
    store = get_store()
    companion_users = store.employees[store.employees["journey"].isin(["onboarding", "mobility"])]
    by_stage: dict[str, int] = {}
    by_owner: dict[str, int] = {}
    by_type: dict[str, int] = {}
    blocked = 0
    for _, r in companion_users.iterrows():
        state = journey_state(store, str(r["employee_id"]))
        if not state.blockers:
            continue
        blocked += 1
        for b in state.blockers:
            by_stage[b.event] = by_stage.get(b.event, 0) + 1
            by_owner[b.owner.name] = by_owner.get(b.owner.name, 0) + 1
    reqs = store.requests
    if not reqs.empty:
        open_reqs = reqs[reqs["status"].astype(str).str.lower() == "open"]
        day = int(get_settings().sim_day)
        for _, req in open_reqs.iterrows():
            if day - int(req.get("created_day", 0)) > int(req.get("sla_days", 0)):
                t = str(req.get("type", "other"))
                by_type[t] = by_type.get(t, 0) + 1
    top_stages = sorted(by_stage.items(), key=lambda x: -x[1])[:10]
    top_owners = sorted(by_owner.items(), key=lambda x: -x[1])[:10]
    top_types = sorted(by_type.items(), key=lambda x: -x[1])[:10]
    from app.core.journey_engine import _label as event_label
    return {"blocked_total": blocked, "journeys_scanned": int(len(companion_users)),
            "by_stage": [{"event": k, "label": event_label(k), "count": v} for k, v in top_stages],
            "by_owner": [{"owner": k, "count": v} for k, v in top_owners],
            "overdue_requests_by_type": [{"type": k, "count": v} for k, v in top_types]}


@app.post("/reset-demo")
async def reset_demo() -> dict:
    """Clear runtime state (notices, handoffs, audit, consent) for a clean demo run."""
    import shutil
    for f in ("notices.json", "handoffs.json", "audit.json", "consent.json", "requests_created.json"):
        p = settings.runtime_dir / f
        if p.exists():
            p.unlink()
    return {"reset": True}


# --- UI ---------------------------------------------------------------------
STATIC = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")

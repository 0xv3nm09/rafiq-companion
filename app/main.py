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
from app.services.scheduler import run_sweep, start_background_sweep

settings = get_settings()

ml = None  # set in lifespan; keeps startup lazy and testable


@asynccontextmanager
async def lifespan(app: FastAPI):
    store = get_store()
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
    """Demo switcher: the two scenario stars first, then a sample of the cohort."""
    import pandas as pd
    store = get_store()
    df = store.employees
    stars = df[df["employee_id"].isin(["E0421", "E0422"])]
    rest = df[~df["employee_id"].isin(["E0421", "E0422"])].head(40)
    out = []
    for _, r in pd.concat([stars, rest]).iterrows():
        out.append({"employee_id": str(r["employee_id"]),
                    "label": f"{r['employee_id']} · {r['name']} ({r['journey']})"})
    return out


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

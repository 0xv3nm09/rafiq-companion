import asyncio

from app.main import get_queue, get_team


def test_org_spine_exists(store):
    """Every companion user has a line manager and an HRBP; managers exist as people."""
    mgr = store.person("E9901")
    assert mgr and mgr["role"] == "Line Manager"
    emp = store.employee("E0421")
    assert emp["line_manager_id"] == "E9901" and emp["hrbp_id"] == "E9911"
    cohort = store.employees[store.employees["journey"].isin(["onboarding", "mobility"])]
    assert cohort["line_manager_id"].notna().all() and (cohort["line_manager_id"] != "").all()
    assert cohort["hrbp_id"].notna().all() and (cohort["hrbp_id"] != "").all()


def test_team_view_groups_reports(store):
    team = asyncio.run(get_team("E9901"))
    assert team["manager"]["name"] == "Khalid Al Suwaidi"
    assert team["team_size"] >= 20
    ids = {r["employee_id"] for r in team["reports"]}
    assert "E0421" in ids
    aisha = next(r for r in team["reports"] if r["employee_id"] == "E0421")
    assert aisha["stage"] == "IT Setup" and aisha["blockers"][0]["label"] == "Laptop issued"
    assert all("pulse" not in r for r in team["reports"])   # privacy: no pulse fields at all


def test_hrbp_queue_flags_stalls(store):
    q = asyncio.run(get_queue("E9911"))
    assert q["caseload"] >= 60
    assert q["flagged"], "the caseload must contain the seeded stalls"
    assert all(f["risk"] >= 0.25 for f in q["flagged"])
    assert q["stalls_by_owner"], "stalls aggregate by named owner"


def test_handoff_status_transition(store):
    from app.agents.action_agent import chase
    from app.schemas.ask import AskRequest
    from app.services.notify import HandoffStore
    resp = chase(AskRequest(employee_id="E0421", message="chase my laptop"), store, "laptop")
    card = HandoffStore().update_status(resp.handoff_id, "acknowledged")
    assert card.status == "acknowledged"
    card = HandoffStore().update_status(resp.handoff_id, "resolved")
    assert card.status == "resolved"


def test_stalls_aggregate(store):
    from app.main import stalls
    d = asyncio.run(stalls())
    assert d["journeys_scanned"] == int((store.employees["journey"].isin(["onboarding", "mobility"])).sum())
    assert d["blocked_total"] > 0
    assert d["by_stage"] and d["by_owner"]
    assert all("employee_id" not in x for x in d["by_stage"])  # aggregate, no individuals


def test_learning_and_facilities_routing(store):
    from app.agents.action_agent import start_request
    from app.schemas.ask import AskRequest
    from app.services.notify import RequestStore
    r1 = start_request(AskRequest(employee_id="E0421", message="Book my induction training"), store, "training")
    assert "Learning & Development" in r1.answer
    r2 = start_request(AskRequest(employee_id="E0421", message="I need a parking desk"), store, "desk")
    assert "Facilities" in r2.answer
    assert len(RequestStore().for_employee("E0421")) >= 2


def test_runtime_seed_fills_audit_and_notices(store):
    from app.services.scheduler import seed_runtime
    from app.core.consent import AuditLog
    from app.services.notify import NoticeStore
    result = seed_runtime(store)
    assert result in ({"seeded": True}, {"seeded": False})
    for emp in ("E0421", "E0422"):
        assert NoticeStore().for_employee(emp), f"no notice for {emp}"
    audit = AuditLog().for_employee("E0421")
    assert any(e["action"] == "companion_enabled" for e in audit)

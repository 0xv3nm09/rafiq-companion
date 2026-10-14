import asyncio

from app.agents.action_agent import chase, sensitive_response
from app.agents.orchestrator import handle
from app.core.consent import AuditLog, ConsentStore, held_data
from app.core.guardrails import redact_pii
from app.schemas.ask import AskRequest
from app.services.notify import HandoffStore, NoticeStore
from app.services.scheduler import sweep_once


def test_pii_redaction():
    text = "email me at a.x@company.com or +971501234567, EID 784-1990-1234567-1"
    out = redact_pii(text)
    assert "a.x@company.com" not in out and "[email]" in out
    assert "971501234567" not in out and "[phone]" in out
    assert "784" not in out and "[emirates-id]" in out


def test_chase_creates_handoff_to_named_owner(store):
    req = AskRequest(employee_id="E0421", message="chase my laptop")
    resp = chase(req, store, "laptop")
    assert resp.escalated and resp.handoff_id
    card = HandoffStore().get(resp.handoff_id)
    assert card.suggested_owner.name == "IT Service Desk"
    assert card.employee_id == "E0421"
    assert card.summary and card.tried
    # second chase dedupes to the open card
    resp2 = chase(req, store, "laptop")
    assert resp2.handoff_id == resp.handoff_id
    assert "already" in resp2.answer


def test_sensitive_handoff_names_a_human(store):
    req = AskRequest(employee_id="E0422", message="I want to file a grievance")
    resp = sensitive_response(req, "grievance")
    assert resp.kind == "handoff" and resp.escalated
    card = HandoffStore().get(resp.handoff_id)
    assert card.suggested_owner.name == "HR Business Partner"
    assert "grievance" in card.summary


def test_sweep_notifies_employee_first_then_escalates(store):
    result = sweep_once(store)
    assert result["employees_scanned"] == len(store.employees)
    assert result["notices_new"] >= 2          # E0421 + E0422 at minimum
    assert result["escalations"] >= 2
    for emp in ("E0421", "E0422"):
        notices = NoticeStore().for_employee(emp)
        assert notices, f"no employee-first notice for {emp}"
        cards = HandoffStore().for_employee(emp)
        assert cards, f"no escalated handoff for {emp}"
        audit = AuditLog().for_employee(emp)
        assert any(e["action"] == "sweep_notice" for e in audit)


def test_my_data_view_and_consent(store):
    data = held_data(store, "E0421")
    assert data["employee"]["name"] == "Aisha Al Mansoori"
    assert data["journey"]["blockers"] == 1
    assert "not_used_for" in data
    consent = ConsentStore()
    consent.set("E0421", "pulse", False)
    assert consent.is_opted_in("E0421") is False
    consent.set("E0421", "pulse", True)
    assert consent.is_opted_in("E0421") is True
    audit = AuditLog().for_employee("E0421")
    assert any(e["action"] == "consent_changed" for e in audit)


def test_full_demo_flow_via_orchestrator(store):
    # 1. status question
    r1 = asyncio.run(handle(AskRequest(employee_id="E0421", message="Where is my laptop?"), store))
    assert r1.kind == "journey"
    # 2. chase action
    r2 = asyncio.run(handle(AskRequest(employee_id="E0421", message="please chase it"), store))
    assert r2.kind == "action" and r2.escalated
    # 3. policy question
    r3 = asyncio.run(handle(AskRequest(employee_id="E0421",
                                       message="How does the end of service gratuity work?"), store))
    assert r3.kind == "policy" and r3.citations
    # 4. sensitive
    r4 = asyncio.run(handle(AskRequest(employee_id="E0421",
                                       message="I need to report harassment"), store))
    assert r4.kind == "handoff" and r4.escalated
    # 5. low confidence
    r5 = asyncio.run(handle(AskRequest(employee_id="E0421",
                                       message="flurbo zazzle quixotic vermillion"), store))
    assert r5.kind == "handoff" and r5.low_confidence is not None

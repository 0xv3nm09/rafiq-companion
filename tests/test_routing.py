import asyncio

from app.agents.orchestrator import classify, handle
from app.schemas.ask import AskRequest


def test_sensitive_routes_to_human():
    assert classify("I want to file a grievance about my manager")[0] == "sensitive"
    assert classify("my visa is stuck and urgent")[0] == "sensitive"


def test_medical_booking_is_not_sensitive():
    assert classify("Book my medical fitness test")[0] != "sensitive"


def test_status_marker_routes_to_journey():
    assert classify("It is day 5 and I still have no laptop")[0] == "journey"
    assert classify("Where is my laptop?")[0] == "journey"


def test_request_verb_routes_to_action():
    assert classify("Book my medical fitness test")[0] == "action"
    assert classify("chase my laptop request")[0] == "action"


def test_policy_question_is_default():
    assert classify("How many annual leave days do I get?")[0] == "policy"


def test_day5_laptop_end_to_end(store):
    req = AskRequest(employee_id="E0421", message="It is day 5 and I still have no laptop")
    resp = asyncio.run(handle(req, store))
    assert resp.kind == "journey"
    assert "IT Service Desk" in resp.answer and "overdue" in resp.answer
    assert any(c.policy_id == "ONB-07" for c in resp.citations)
    assert any(a.startswith("offer_chase") for a in resp.actions)


def test_stalled_transfer_end_to_end(store):
    req = AskRequest(employee_id="E0422", message="What's the status of my transfer?")
    resp = asyncio.run(handle(req, store))
    assert resp.kind == "journey"
    assert "Receiving Manager" in resp.answer
    assert any(c.policy_id == "MOB-01" for c in resp.citations)


def test_arabic_journey_reply(store):
    req = AskRequest(employee_id="E0421", message="وين حاسوبي؟", lang="ar")
    resp = asyncio.run(handle(req, store))
    assert resp.kind == "journey"
    assert "IT Service Desk" in resp.answer

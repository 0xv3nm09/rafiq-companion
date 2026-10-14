import asyncio

import pytest

from app.agents.policy_agent import answer_policy
from app.core.rag import PolicyIndex, extractive_answer
from app.schemas.ask import AskRequest

# one session-scoped index over the synthetic corpus
@pytest.fixture(scope="module")
def index(store):
    return PolicyIndex(store.policy_chunks)


def test_retrieval_finds_leave_policy(index):
    hits = index.search("How many days of annual leave do I get?", lang="en")
    assert hits and hits[0].chunk.policy_id == "HR-01"
    assert hits[0].confidence >= 0.5


def test_retrieval_finds_laptop_sla(index):
    hits = index.search("when should I receive my laptop", lang="en")
    assert hits and hits[0].chunk.policy_id == "ONB-07"


def test_arabic_retrieval(index):
    hits = index.search("كم عدد أيام الإجازة السنوية", lang="ar")
    assert hits and hits[0].chunk.lang == "ar" and hits[0].chunk.policy_id == "HR-01"


def test_gibberish_stays_below_threshold(index):
    hits = index.search("zzz qqq wxyz flurbo", lang="en")
    assert (not hits) or hits[0].confidence < 0.5


def test_extractive_answer_stays_inside_source(index):
    hits = index.search("when should I receive my laptop", lang="en")
    text = extractive_answer("when should I receive my laptop", hits, "en")
    assert "ONB-07" in text and "day 3" in text


def test_policy_answer_is_cited(store):
    req = AskRequest(employee_id="E0421", message="How many days of annual leave do I get?")
    resp = asyncio.run(answer_policy(req, store))
    assert resp.kind in ("policy", "handoff")
    if resp.kind == "policy":
        assert resp.citations and any(c.policy_id == "HR-01" for c in resp.citations)
        assert resp.confidence >= 0.5


def test_low_confidence_becomes_handoff(store):
    req = AskRequest(employee_id="E0421", message="zzz qqq wxyz flurbo bamboozle")
    resp = asyncio.run(answer_policy(req, store))
    assert resp.kind == "handoff"
    assert resp.escalated and resp.handoff_id
    assert "not sure" in resp.answer.lower() or "لست متأكد" in resp.answer

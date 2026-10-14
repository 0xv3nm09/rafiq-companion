"""Orchestrator — classify intent, route to a specialist.

Rules-first (explainable, demo-safe): sensitive topics go straight to a human;
status/delay phrasing goes to the journey agent; request verbs go to the action
agent; everything else gets a grounded, cited policy answer.
"""
from __future__ import annotations

from app.agents.action_agent import handle_action, sensitive_response
from app.agents.journey_agent import journey_reply
from app.agents.policy_agent import answer_policy
from app.core.guardrails import is_sensitive
from app.schemas.ask import AskRequest, AskResponse

_STATUS_MARKERS = [
    "where is", "where's", "when will", "when do i get", "still", "not arrived", "hasn't",
    "haven't received", "haven t", "missing", "overdue", "delayed", "late", "stuck",
    "what's next", "whats next", "next step", "status", "waiting", "any update",
    "وين", "متى", "ما زال", "لم يصل", "لم يتم", "لم يصلك", "متأخر", "متأخرة", "الحالة",
    "حالة", "الخطوة التالية", "التالي", "متعثر", "انتظر", "اين",
]
_CHASE_WORDS = ["chase", "follow up", "followup", "nudge", "escalate", "تابع", "متابعة", "استعجل"]


def classify(message: str) -> tuple[str, str]:
    m = message.lower()
    topic = is_sensitive(m)
    if topic:
        return ("sensitive", topic)
    if any(k in m for k in _STATUS_MARKERS):
        return ("journey", "status")
    if "chase" in m or "تابع" in m or "متابعة" in m:
        return ("action", "chase")
    if any(k in m for k in ("book", "schedule", "request ", "apply", "replace", "order",
                            "احجز", "اطلب", "استبدال", "جدول")):
        return ("action", "start")
    return ("policy", "qa")


async def handle(req: AskRequest, store) -> AskResponse:
    intent, detail = classify(req.message)
    if intent == "sensitive":
        return sensitive_response(req, detail)
    if intent == "journey":
        return await journey_reply(req, store)
    if intent == "action":
        return await handle_action(req, store, detail)
    return await answer_policy(req, store)

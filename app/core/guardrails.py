"""Trust gate — input rails (PII redaction, sensitive-topic routing) shared by
every agent. One decorator wraps agent outputs so citations, consent and
confidence checks are never skipped."""
from __future__ import annotations

import re
from functools import wraps

from app.config import get_settings
from app.schemas.ask import AskRequest, AskResponse

# --- PII redaction ----------------------------------------------------------
_RE_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
_RE_PHONE = re.compile(r"(?:\+?971|0)5\d[- ]?\d{3}[- ]?\d{4}")
_RE_EID = re.compile(r"\b784[- ]?\d{4}[- ]?\d{7}[- ]?\d\b")


def redact_pii(text: str) -> str:
    text = _RE_EID.sub("[emirates-id]", text)
    text = _RE_EMAIL.sub("[email]", text)
    return _RE_PHONE.sub("[phone]", text)


# --- sensitive-topic routing -------------------------------------------------
# Direct hits always route to a human.
_SENSITIVE_DIRECT = [
    "grievance", "complaint", "harassment", "discrimination", "disciplinary",
    "resignation", "termination", "dismissed", "lawsuit", "legal action",
    "mental health", "suicide", "self-harm", "unfit for work",
    "شكوى", "تحرش", "تمييز", "انضباط", "استقالة", "فصل", "صحتي النفسية",
]
# Combination hits: these topics are only sensitive when they describe an
# individual problem, not when they name a trackable journey step.
_SENSITIVE_COMBOS = [
    ("visa", ["problem", "issue", "stuck", "denied", "rejected", "delayed too long", "urgent", "emergency"]),
    ("medical", ["condition", "diagnosis", "chronic", "unfit", "report", "mental"]),
    ("تأشيرة", ["مشكلة", "متعثر", "مرفوض", "عاجل"]),
]
_REQUEST_WORDS = ["book", "schedule", "request", "apply", "chase", "raise", "order", "replace",
                  "احجز", "اطلب", "تابع"]


def is_sensitive(message: str) -> str | None:
    """Return the sensitive topic name if the message must go to a human."""
    m = message.lower()
    for kw in _SENSITIVE_DIRECT:
        if kw in m:
            return kw
    for topic, triggers in _SENSITIVE_COMBOS:
        if topic in m and any(t in m for t in triggers):
            return topic
    return None


def has_request_intent(message: str) -> bool:
    return any(w in message.lower() for w in _REQUEST_WORDS)


def trust_gate(fn):
    """Wrap an async agent handler: redact PII; below the confidence floor or
    without a citation, convert to a low-confidence handoff instead of answering."""
    @wraps(fn)
    async def wrapped(req: AskRequest, *args, **kwargs) -> AskResponse:
        resp: AskResponse = redact_pii_response(await fn(req, *args, **kwargs))
        settings = get_settings()
        if resp.kind in ("policy",) and (resp.confidence < settings.min_confidence or not resp.citations):
            from app.agents.action_agent import low_confidence_response
            fallback = low_confidence_response(req)
            fallback.low_confidence = resp.low_confidence or None
            return fallback
        from app.core.consent import AuditLog
        AuditLog().append(req.employee_id, "answered", {"kind": resp.kind, "confidence": resp.confidence,
                                                        "actions": resp.actions})
        return resp
    return wrapped


def redact_pii_response(resp: AskResponse) -> AskResponse:
    resp.answer = redact_pii(resp.answer)
    return resp

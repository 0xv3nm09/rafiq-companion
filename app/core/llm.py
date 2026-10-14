"""The ONLY place a model is called. Optional: with no API key configured the
companion answers extractively from retrieved policy (still cited, still safe).

Production path (described in the solution note): Falcon-H1 Arabic / JAIS
served on-premise, in-region. The demo may use a hosted model for convenience.
"""
from __future__ import annotations

import logging

import httpx

from app.config import get_settings

log = logging.getLogger("rafiq.llm")

_SYSTEM = (
    "You are Rafiq, an employee companion. Answer ONLY from the provided policy context. "
    "Cite the policy id and section inline like [ONB-07 §3.2]. If the context does not "
    "contain the answer, reply exactly: I am not sure. Answer in the requested language. "
    "Be concise (max 4 sentences), calm and supportive. Never invent policy facts."
)


def available() -> bool:
    s = get_settings()
    return bool(s.openrouter_api_key or s.groq_api_key)


def complete(question: str, context: str, lang: str) -> str | None:
    """Return a grounded answer or None (caller falls back to extractive)."""
    s = get_settings()
    try:
        if s.openrouter_api_key:
            return _openrouter(s, question, context, lang)
        if s.groq_api_key:
            return _groq(s, question, context, lang)
    except Exception:
        log.exception("llm call failed — falling back to extractive answer")
    return None


def _openrouter(s, question: str, context: str, lang: str) -> str | None:
    with httpx.Client(timeout=s.llm_timeout_s) as client:
        r = client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {s.openrouter_api_key}"},
            json={
                "model": s.openrouter_model,
                "temperature": 0,
                "max_tokens": 512,
                "messages": [
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user", "content": f"Language: {lang}\n\nContext:\n{context}\n\nQuestion: {question}"},
                ],
            },
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()


def _groq(s, question: str, context: str, lang: str) -> str | None:
    with httpx.Client(timeout=s.llm_timeout_s) as client:
        r = client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {s.groq_api_key}"},
            json={
                "model": s.groq_model,
                "temperature": 0,
                "max_tokens": 512,
                "messages": [
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user", "content": f"Language: {lang}\n\nContext:\n{context}\n\nQuestion: {question}"},
                ],
            },
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()

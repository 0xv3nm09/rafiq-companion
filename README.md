# Rafiq — Employee AI Companion

An employee-owned AI companion that carries a person across **both** the onboarding and the
internal-mobility journey, answers policy questions with inline citations, and quietly catches
friction *before* it becomes a complaint — on a consent-first, UAE-sovereign footing.

Unlike support bots that only answer and marketplaces that only match, Rafiq knows where you are
in your journey, cites the policy behind every answer, and flags a stall to the right named owner
before you have to chase it yourself.

> Built for the Ignyte × Emirates "Employee AI Companion" challenge.

## Quick start

```bash
uv sync                      # or: pip install -e ".[dev]"
uv run uvicorn app.main:app --port 8000
open http://localhost:8000
```

Tests: `uv run pytest` (30 tests: engine, friction, RAG grounding, routing, sweep, trust).

No API keys are required — without one, answers are composed **extractively from retrieved policy
text** (still cited, zero hallucination). To add generative polish, copy `.env.example` → `.env`
and set `OPENROUTER_API_KEY` or `GROQ_API_KEY`.

## The demo in 90 seconds

Two scenario employees are seeded (`SIM_DAY=5`):

1. **Day-5 laptop (E0421 · Aisha, onboarding).** Rafiq opens with the blocker proactively:
   laptop due day 3, 2 days overdue, owner IT Service Desk. Ask *"Where is my laptop?"* →
   deterministic journey answer citing **ONB-07** → tap **Chase** → a structured handoff card
   (blocker, what's been tried, named owner) is raised and logged.
2. **Stalled transfer (E0422 · Omar, mobility).** Switch employee → his receiving-team sign-off
   is 3 days past its day-15 SLA. Ask *"What's the status of my transfer?"* → cites **MOB-01**,
   names the Receiving Manager.

Then show the trust surfaces — the 25% Responsible-AI criterion, made clickable:

- **My data** — what we hold, with the line *"not used for performance or discipline — ever"*.
- **Pulse consent toggle** — off ⇒ pulse data is excluded from every signal (tested).
- **Audit log** — everything Rafiq did, timestamped, employee-visible.
- **Simulate sweep** — the proactive engine re-scans all 200 employees, notifies the employee
  first, and escalates persistent stalls to named owners (idempotent per employee/event/day).
- **EN / ع** — full RTL flip (layout mirrors, Arabic answers, Arabic timeline labels).

## Architecture (four parts + a trust layer)

| Part | What it does | Where |
| --- | --- | --- |
| Journey-state engine | Deterministic: joins journey events against `journey_maps.md` target days → stage, blockers, timeline. A rule a judge can verify by hand. | `app/core/journey_engine.py` |
| Grounded answer layer | BM25 retrieval with Arabic-aware normalization + heading anchors over a bilingual policy corpus; every answer cited (`policy_id · section`); below threshold ⇒ "I'm not sure" + handoff. | `app/core/rag.py`, `app/agents/policy_agent.py` |
| Action & routing | Rules-first orchestrator (sensitive → human, status → journey, verbs → action, else policy); chases and request creation produce structured handoff cards. | `app/agents/orchestrator.py`, `action_agent.py` |
| Friction radar | Explainable weights: +0.25/overdue event, +0.15/past-SLA request, +0.10 consented pulse dip. Employee sees it first; only persistent stalls escalate. | `app/core/friction.py`, `app/services/scheduler.py` |
| Trust layer | Consent store, employee-visible audit log, PII redaction, sensitive-topic guard, one `trust_gate` wrapping every answer. | `app/core/consent.py`, `guardrails.py` |

LLM calls live in exactly one file (`app/core/llm.py`) — swap in Falcon-H1 Arabic / JAIS
on-premise for the sovereign production path without touching anything else.

## Data

`app/services/data.py` loads from **`data/pack/`** (the official challenge pack) and falls back to
`data/synthetic/`, which mirrors the documented schema — `journey_events.csv`,
`service_requests.csv`, `pulse_feedback.csv`, `employees.csv`, `journey_maps.md` and
`policies/{en,ar}/*.md` (17 bilingual policies). Column aliases make the loader tolerant of a
differently-named official pack. Regenerate the synthetic pack:

```bash
uv run python scripts/make_synthetic_data.py --employees 200 --sim-day 5
```

To plug in the official pack: create `data/pack/`, drop the files in, restart. Nothing else
changes — the same engine, thresholds and surfaces run on it.

## Judging criteria → what's built

- **Scenario performance (30%)** — deterministic SLA engine nails day-5-laptop and stalled
  transfer/visa; grounded answers cite; low confidence never guesses (tested).
- **Employee experience (25%)** — one companion for both journeys, bilingual RTL, proactive
  cold-open, calm status colours, journey timeline with one-tap chase.
- **Responsible AI & privacy (25%)** — opt-in consent, employee-visible data panel, audit log,
  named human owner on every escalation, sensitive topics routed to humans, PII redaction —
  all live in the demo, not a slide.
- **Deployability & reuse (10%)** — in-region sovereign model path, policy-agnostic design,
  schema-tolerant loader ready for other government entities' packs.
- **Team & pilot readiness (10%)** — scoped: ~1,300 LOC Python, zero heavy infra (no vector DB /
  queue needed at this corpus size), 30 green tests, thresholds configurable in `.env`.

## Production notes (described, not needed for the demo)

Hybrid retrieval + cross-encoder rerankers, NeMo/Presidio guardrail stack, Docker compose with
Qdrant/Redis/Ollama, ISO 42001 / NIST AI RMF governance mapping, and the UAE PDPL data-residency
posture are covered in `docs/Employee AI Engineering Workbook.md`, which this build follows.

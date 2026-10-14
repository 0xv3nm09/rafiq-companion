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

- **My data** — what we hold, your named line manager and HRBP, and the line *"not used for
  performance or discipline — ever"*.
- **Pulse consent toggle** — off ⇒ pulse data is excluded from every signal (tested).
- **Audit log** — everything Rafiq did, timestamped, employee-visible.
- **Simulate sweep** — the proactive engine re-scans all 200 employees, notifies the employee
  first, and escalates persistent stalls to named owners (idempotent per employee/event/day).
- **EN / ع** — full RTL flip (layout mirrors, Arabic answers, Arabic timeline labels).

Then switch **Viewing as** to the other side of the org — the flows run on the same synthetic data:

- **Line manager · Grace Okonkwo (IT)** — a risk-sorted team of 34 with each report's blockers
  and named owners. Read-only help, not surveillance: pulse content is never visible to managers.
- **HRBP · Fatima Al Hashimi** — an early-warning queue (only real stalls, each already seen by
  the employee first) aggregated by owner, plus the **Handoff inbox**: complete cards (stage,
  blocker, what's been tried, named owner) that the owner can acknowledge and resolve — which the
  employee sees in their own audit log.

**Brief coverage** (What to Build → where it lives):

| Brief requirement | Where it is |
| --- | --- |
| Knows the journey stage and what's next (day 5, laptop not issued) | Journey engine + timeline + proactive check-ins |
| Answers policy questions, citing the source policy | Grounded RAG answer cards with `policy_id · section` chips |
| Completes/starts routine requests, handing to HR, IT, learning workflows | Request routing to Payroll, IT Service Desk, Learning & Development, Facilities, HR — with handoff cards |
| Spots friction early (events, request delays, opt-in pulse) | Friction radar + idempotent sweep |
| Escalates to the right human owner with a summary | Handoff inbox with named owner, acknowledge/resolve |
| Nice to have: Arabic + English | Full RTL flip, Arabic corpus, Arabic answers/timeline |
| Nice to have: manager view for new joiners | Team view, risk-sorted, pulse never visible |
| Nice to have: where journeys stall most often | **Stall map** — aggregate bars by stage + owner chips, never an individual |

Employee-side quality-of-life: a **notification bell** in the top bar (unread count + tray),
**search** in the View-as switcher, **filters** on the team/queue lists, and seeded history so
the audit log and notices are never empty on a fresh open.

> **Out of scope (per brief):** the full employee lifecycle, connection to live Emirates
> systems, and any use in performance or disciplinary decisions — enforced by design (pack
> files read-only, synthetic adapters, pulse excluded from every signal without consent).

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

## Architecture

Two views of the same system. Both SVGs are self-adapting: GitHub's dark and light
readers each get the right colours from one file.

<p align="center">
  <img src="docs/diagrams/architecture-overview.svg" alt="Overview: a proactive, agentic companion — employee asks by text or voice in Arabic or English, the orchestrator routes to the journey-state, policy (RAG) and action agents, a friction radar watches events, SLAs and pulse dips, a trust gate checks consent, citations, confidence and applies a human gate, and grounding comes from the journey-state store, cited policy store, HRIS/ITSM connectors, consent and pulse records, with named human owners (HRBP, IT, Facilities) for escalations" width="700">
</p>

**Overview — a proactive, agentic companion: grounded, gated, human-owned.** The left flow is
the answer path (orchestrator → journey-state / policy / action agents); the friction radar
watches events, SLAs and consented pulse dips and pushes in *before* the employee asks. Every
answer and action passes the trust gate; grounding comes from the journey-state store, the cited
policy store and (in a pilot) read-only HRIS/ITSM connectors; escalations always land with a
named human owner.

<p align="center">
  <img src="docs/diagrams/architecture-zoned.svg" alt="Zoned architecture: zone 1 employee + channels (web or mobile, text or voice, AR + EN), zone 2 the AI companion (orchestrator router, journey-state events vs SLA, policy RAG cited answers, action + route, friction radar sweep, and a trust gate band of consent, citations, confidence, PII redaction and human gate on every answer and action), zone 3 data + people (journey and consent store, policy vector store, append-only audit log, HRIS/ITSM connectors synthetic now and live read-only in pilot, Emirates systems)" width="620">
</p>

**Zoned view — where data lives and where it may go.** Zone 1 is the employee and their
channels; zone 2 is the companion with the trust gate drawn as a band because *every* answer and
action crosses it; zone 3 is data + people: journey and consent stores, the cited policy corpus,
an append-only audit log, and the Emirates systems reached through connectors that are synthetic
in the build and read-only in a pilot. The posture in the subtitle — employee-owned, grounded +
gated, in-region (PDPL), human-owned escalations — is enforced in code, not aspiration.

## What the judge sees

Three screens carry the demo; each maps to the criteria it serves.

| Screen | What it shows | What was achieved |
| --- | --- | --- |
| ![Home — proactive cold-open](docs/screenshots/home.png) | **Home — the proactive cold-open.** Aisha, day 5 of onboarding: her stage, her open blocker and a one-tap chase are on screen *before she asks*. The trust line is plain text, not a footnote. | Friction caught before the complaint (30% scenario weight); employee-owned trust made visible (25% Responsible-AI weight). |
| ![Chat — grounded, cited answer](docs/screenshots/chat-cited-answer.png) | **Chat — grounded and cited.** "Where is my laptop?" gets a deterministic journey answer citing policy **ONB-07** with the named owner (IT Service Desk); *Chase* raises a structured handoff card that lands in the owner's inbox. | Hidden-scenario reliability: cited answers, no hallucinated policy, complete correctly-routed handoffs (30% + 25%). |
| ![Manager view — read-only team help](docs/screenshots/manager-team.png) | **Manager view — read-only team help.** Grace Okonkwo (IT) sees her 34 reports risk-sorted with journey facts only. Two notes say it outright: help, not surveillance — pulse content is never visible to managers. | The companion works in *both* directions without becoming a monitoring tool — the Responsible-AI line judges probe hardest (25%). |

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
- **Employee experience (25%)** — one companion for both journeys, bilingual RTL, a Home landing
  with the employee's live stage and blocker, corner navigation (Home / Chat / Journey / My data /
  Audit log / Notices), "Viewing as" switcher, calm status colours, timeline with one-tap chase —
  and journey steps that complete early at the visa window read like the real process, not a checklist.
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

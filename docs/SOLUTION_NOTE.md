# Solution note — Rafiq, the Employee AI Companion

**Muhammad Omaid — Magnus Mage (dev team)**
*Entry for the Ignyte × Emirates "Employee AI Companion" challenge*

## 1. Problem & scope

An employee's experience at Emirates spans many teams, systems, approvals and policies. The
warning signals exist — a journey event that never happened, a request sitting past its SLA, a
dip in an opt-in pulse — but they are scattered across systems and surface only after a complaint
or escalation. At 131,000 employees and ~9,700 UAE joiners a year, even a small per-journey
friction rate is thousands of stuck employees.

**Scope:** two journeys — onboarding and internal mobility. Out of scope: the full employee
lifecycle, connection to live Emirates systems, any use in performance or disciplinary decisions.

## 2. What we built

A working prototype over the synthetic data pack: FastAPI + pandas + a dependency-free BM25
retrieval index, a single-page bilingual UI, and four deterministic-first parts:

1. **Journey-state engine** — journey events joined against `journey_maps.md` target days;
   `day > target` with no completion ⇒ blocker with the map's named owner. Deterministic, so
   "day 5, laptop not issued" — and any hidden stall scenario — falls out of one rule.
2. **Grounded answer layer** — BM25 with Arabic-aware normalization and heading anchors over 17
   bilingual policies; every answer cites `policy_id · section`; below the retrieval floor the
   companion says *"I'm not sure"* and hands off. No API key needed: answers are extractive from
   retrieved policy; with a key, temperature-0 generation strictly inside the retrieved context.
3. **Action & routing layer** — rules-first orchestrator (sensitive → human; status → journey;
   request verbs → action; else policy). Chases and requests produce **structured handoff cards**
   routed to named owners, who acknowledge and resolve them.
4. **Friction radar + sweep** — explainable weights (+0.25 overdue event, +0.15 past-SLA
   request, +0.10 consented pulse dip); the employee always sees the blocker first; only
   persistent stalls escalate. Idempotent per employee/event/day.

## 3. Consent, privacy and human oversight (as required)

- **Opt-in consent, enforced at the signal level.** Pulse feedback contributes to friction only
  while `ConsentStore` records opt-in; revocation excludes the signal immediately and is confirmed
  to the employee. Answering a pulse without consent is acknowledged but explicitly not used.
- **The employee sees their own data.** A "what we hold about you" panel (profile, line manager,
  HRBP, journey state, request count, pulse count) plus an append-only audit log of every action
  the companion took, employee-visible at all times.
- **Human handoffs.** Every intervention that affects an employee carries a named human owner.
  Sensitive topics (grievance, medical circumstances, visa problems) route to a person before any
  answer is attempted. Owners work a complete inbox; their acknowledge/resolve actions appear in
  the employee's audit log.
- **Not a monitoring tool.** The manager view structurally contains no pulse data — the endpoint
  never reads it (asserted by tests). HRBP and analytics views are aggregate-only, never
  individual. Scores are never used for performance or discipline.
- **Data stays home.** Everything runs self-hosted; the pack is never uploaded to services that
  retain or train on data. The sovereign path (Falcon-H1 Arabic / JAIS on-premise, in-region)
  is a one-file swap (`app/core/llm.py`).

## 4. Why it wins the criteria (summary)

- **Scenario performance:** deterministic engine + grounded retrieval + safe degradation
  (unsure ⇒ handoff, never a guess); 39 tests assert the guardrails.
- **Employee experience:** proactive cold-open, cited answer cards, SLA timeline with real-process
  hints, notification bell, Arabic/English with a true RTL flip.
- **Responsible AI & privacy:** the four mechanisms above, all clickable in the live demo.
- **Deployability & reuse:** schema-alias loader accepts the official pack unchanged; runs fully
  offline; policy-agnostic corpus packaged for other government entities.
- **Pilot readiness:** thresholds in configuration; pilot swap is data + read-only connectors;
  the deterministic core does not change.

## 5. Limitations & next steps

Read-only pack (writes go to runtime stores until connectors exist); BM25-scale retrieval
(hybrid + reranker before ~50+ documents); rules-first routing (small learned router once real
phrasings exist); voice designed but not built; Arabic corpus pending UAE HR counsel review.

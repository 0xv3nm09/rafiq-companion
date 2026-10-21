# Engineering Workbook

A build reference for the companion: recommended Python and AI stack, free models, project structure, schemas, code snippets, Docker, latency, UI, and best practices. Pairs with the strategy analysis in the main tab. All free/open-source unless noted.

## Recommended stack (Python, AI libraries)

All open-source and runnable offline for the synthetic-data guardrail. Pick one per layer; alternatives in brackets.

| Layer | Library (free/OSS) | Why |
| --- | --- | --- |
| API framework | FastAPI + Uvicorn | Async, typed, auto OpenAPI docs |
| Schemas / validation | Pydantic v2 | Typed request/response, strict validation |
| Agent orchestration | LangGraph (or CrewAI, Pydantic-AI) | Multi-agent graph, shared state, human-in-loop gates |
| RAG framework | LlamaIndex (or LangChain) | Retrieval, query engines, source citations |
| Embeddings | BGE-M3 (or multilingual-e5-large) | Strong multilingual incl. Arabic |
| Reranker | bge-reranker-v2-m3 | Lifts retrieval precision before the LLM |
| Vector DB | Qdrant (or Chroma, pgvector) | Fast, OSS, metadata filters per employee/policy |
| LLM runtime | Ollama (dev) / vLLM (prod) | Serve open models locally / on-prem |
| Data + analytics | pandas + DuckDB | Load and query the CSV data pack fast |
| Scheduling (proactive) | APScheduler (or Celery + Redis) | SLA sweeps, event checks, reminders |
| Cache | Redis | Semantic + response cache for latency |
| Guardrails | NeMo Guardrails (or Guardrails-AI) | Input/output rails, PII, topic limits |
| Observability | Langfuse + OpenTelemetry | Tracing, latency, token cost |
| RAG eval | Ragas | Retrieval + answer quality in CI |
| STT (voice) | faster-whisper (large-v3) | Arabic/English speech-to-text |
| TTS (voice) | Piper (or Coqui XTTS) | Arabic/English text-to-speech |
| Frontend | Next.js + React (or Streamlit for speed) | UI with RTL support |
| Auth / SSO | Authlib (or Keycloak) | Sign-in, consent capture |

## Free AI models

All open-weight and self-hostable, which keeps inference in-region (PDPL-friendly) and costs near zero for the demo.

| Model | Use | Notes |
| --- | --- | --- |
| [Falcon-H1 Arabic](https://www.businesswire.com/news/home/20260105343577/en) (TII, Abu Dhabi) | Primary bilingual LLM | Leads the Open Arabic LLM Leaderboard; open, on-prem, UAE-sovereign |
| [JAIS](https://enterpriseam.com/uae/issues/uae-launches-new-ai-model-to-rival-big-tech/) (Core42 / G42) | Arabic-English LLM alternative | Arabic-first bilingual |
| Llama 3.3 (Meta) or Qwen2.5 | General reasoning; small variant for cheap routing | Open weights; run 7B-8B for the router, larger for answers |
| BGE-M3 (BAAI) | Embeddings | Multilingual incl. Arabic; dense + sparse retrieval |
| bge-reranker-v2-m3 | Reranker | Multilingual precision boost |
| faster-whisper large-v3 | Speech-to-text | Arabic + English |
| Piper / Coqui XTTS-v2 | Text-to-speech | Arabic + English voices |

**Routing tip:** use a small model (Qwen2.5-7B / Llama-3.1-8B) for the orchestrator's intent routing and a larger one only for grounded answers. Cheaper and faster, same quality where it matters.

## Project structure (modular, DRY)

One repo, clear layers. Pure logic in `core/`, orchestration in `agents/`, I/O shapes in `schemas/` as the single source of truth.

```text
companion/
  app/
    main.py              # FastAPI app + routes
    config.py            # settings via pydantic-settings (.env)
    schemas/             # Pydantic models = single source of truth
      common.py          # Lang, Stage, Citation, Confidence
      ask.py             # AskRequest / AskResponse
      journey.py         # JourneyState, Blocker
      handoff.py         # HandoffCard
      errors.py          # ErrorResponse
    agents/
      orchestrator.py    # classify intent -> route to a specialist
      journey_agent.py   # stage vs SLA (deterministic)
      policy_agent.py    # RAG, cited answers
      action_agent.py    # start/route requests, build handoff
    core/                # pure, framework-free, unit-tested
      llm.py             # the ONLY place models are called
      rag.py             # retrieve -> rerank -> cite
      journey_engine.py  # SLA rules from journey_maps.md
      friction.py        # events + SLAs + pulse -> flags
      guardrails.py      # trust gate (consent, cite, confidence, PII)
      consent.py         # opt-in checks + audit log
    services/
      data.py            # load CSV pack (pandas / duckdb)
      scheduler.py       # APScheduler proactive sweeps
      notify.py          # employee first, then named owner
    data/                # synthetic pack (gitignored)
    tests/
  ui/                    # Next.js app (or streamlit_app.py)
  Dockerfile
  docker-compose.yml
  pyproject.toml
  .env.example
```

**DRY / modular rules that keep it clean:**

- `schemas/` is imported by the API, agents and tests alike — a shape is defined once.
- `core/` has no framework imports, so the same functions serve the API, the scheduler and a CLI, and are trivially unit-testable.
- Agents only orchestrate; they call `core/` functions and never re-implement logic.
- `llm.py` is the single model boundary — swap Falcon / JAIS / Llama in one file.
- `guardrails.py` wraps every agent output in one decorator, so citations, consent and confidence checks are never skipped.
- Config via `pydantic-settings` + `.env` — no hard-coded secrets or paths.

## Schemas: request, response, error

The Pydantic models are the contract — the API, agents and tests all import them, so a shape is defined once.

```python
# schemas/common.py
from enum import Enum
from pydantic import BaseModel, Field

class Lang(str, Enum):
    EN = 'en'
    AR = 'ar'

class Journey(str, Enum):
    ONBOARDING = 'onboarding'
    MOBILITY = 'mobility'

class Citation(BaseModel):
    policy_id: str
    title: str
    section: str | None = None
    url: str | None = None

# schemas/ask.py
class AskRequest(BaseModel):
    employee_id: str
    message: str
    lang: Lang = Lang.EN
    consent_pulse: bool = False

class AskResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)
    citations: list[Citation] = []
    actions: list[str] = []          # tool calls taken, e.g. chase_it_ticket
    escalated: bool = False
    handoff_id: str | None = None

# schemas/journey.py
class Blocker(BaseModel):
    event: str
    due_day: int
    days_overdue: int
    owner: str

class JourneyState(BaseModel):
    employee_id: str
    journey: Journey
    stage: str
    day: int
    blockers: list[Blocker] = []
    risk: float = 0.0

# schemas/handoff.py
class HandoffCard(BaseModel):
    employee_id: str
    stage: str
    blocker: str
    tried: list[str] = []
    suggested_owner: str
    summary: str

# schemas/errors.py
class ErrorResponse(BaseModel):
    error: str                 # machine code, e.g. low_confidence
    message: str               # human-readable
    detail: dict | None = None
    request_id: str
```

### JSON on the wire

`POST /ask` request:

```json
{
  "employee_id": "E0421",
  "message": "It is day 5 and I still have no laptop",
  "lang": "en",
  "consent_pulse": true
}
```

`200 OK` response (grounded, cited, escalated):

```json
{
  "answer": "Your laptop was due on day 3. I have opened a chase with IT and flagged it to the owner.",
  "confidence": 0.88,
  "citations": [
    { "policy_id": "ONB-07", "title": "IT Provisioning", "section": "3.2" }
  ],
  "actions": ["chase_it_ticket"],
  "escalated": true,
  "handoff_id": "H-5591"
}
```

Handoff card sent to the named owner:

```json
{
  "employee_id": "E0421",
  "stage": "onboarding/day-5",
  "blocker": "Laptop not issued (SLA day 3, 2 days overdue)",
  "tried": ["auto-reminder to IT on day 4"],
  "suggested_owner": "IT Service Desk",
  "summary": "New joiner E0421 has no laptop on day 5; IT provisioning overdue by 2 days."
}
```

Standard error envelope (every 4xx / 5xx):

```json
{
  "error": "low_confidence",
  "message": "I am not sure, so I have routed this to a person.",
  "detail": { "retrieval_score": 0.34, "threshold": 0.5 },
  "request_id": "req_8c12"
}
```

## Core code snippets

The proactive core is deterministic on purpose — explainable and demo-safe. These are illustrative, not full files.

```python
# core/journey_engine.py  --  deterministic, explainable
import pandas as pd

def journey_state(emp_id: str, events: pd.DataFrame,
                  targets: dict[str, int], today: int) -> JourneyState:
    done = set(events[events.employee_id == emp_id].event)
    blockers = []
    for event, due_day in targets.items():
        if event not in done and today > due_day:
            blockers.append(Blocker(event=event, due_day=due_day,
                                    days_overdue=today - due_day,
                                    owner=OWNERS[event]))
    risk = min(1.0, 0.25 * len(blockers))
    return JourneyState(employee_id=emp_id, journey=Journey.ONBOARDING,
                        stage=stage_for(today), day=today,
                        blockers=blockers, risk=risk)
```

```python
# core/friction.py  --  events + open requests + opt-in pulse
def scan(emp_id, events, requests, pulse, targets, today, consented: bool) -> float:
    state = journey_state(emp_id, events, targets, today)
    overdue = requests[(requests.employee_id == emp_id) &
                       (requests.days_open > requests.sla_days)]
    risk = state.risk + 0.15 * len(overdue)
    if consented and pulse_dip(pulse, emp_id):   # pulse = tie-breaker, with consent
        risk += 0.1
    return min(1.0, risk)
```

```python
# services/scheduler.py  --  proactive sweeps
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', hours=6)
async def sweep():
    for emp_id in active_employees():
        state = journey_state(emp_id, EVENTS, TARGETS, day_of(emp_id))
        for b in state.blockers:
            await notify_employee_first(emp_id, b)        # employee sees it first
            if b.days_overdue >= ESCALATE_AFTER:
                await escalate(build_handoff(emp_id, b))  # then a named owner
```

The answer path is grounded and gated. The RAG agent answers only from retrieved policy and hands off when it is not confident; one `trust_gate` decorator wraps every response.

```python
# core/rag.py  --  retrieve, rerank, answer only from sources
def answer_policy(question: str, lang: Lang) -> AskResponse:
    hits = vector.search(embed(question), top_k=8, filter={'lang': lang})
    hits = rerank(question, hits)[:4]
    if not hits or hits[0].score < MIN_SCORE:       # not confident -> hand off
        return low_confidence_handoff(question)
    ctx = '\n'.join(h.text for h in hits)
    text = llm(PROMPT_ANSWER_ONLY_FROM_CONTEXT,
               question=question, context=ctx, lang=lang)
    return AskResponse(answer=text, confidence=hits[0].score,
                       citations=[to_citation(h) for h in hits])
```

```python
# agents/orchestrator.py  --  classify intent, route to a specialist
async def handle(req: AskRequest) -> AskResponse:
    intent = classify(req.message)                 # small, fast model
    if is_sensitive(intent):                        # visa, medical, grievance
        return route_to_human(req)
    if intent == 'status':
        return journey_reply(req.employee_id)
    if intent == 'request':
        return action_agent(req)
    return answer_policy(req.message, req.lang)     # safe default = grounded answer
```

```python
# core/guardrails.py  --  one trust gate wraps every answer
def trust_gate(fn):
    async def wrapped(req: AskRequest) -> AskResponse:
        resp = redact_pii(await fn(req))
        if resp.confidence < MIN_CONFIDENCE or not resp.citations:
            return low_confidence_handoff(req.message)   # no source -> no claim
        log_action(req.employee_id, resp)                # audit log for the employee
        return resp
    return wrapped
```

```python
# app/main.py  --  FastAPI, typed, streaming-ready
from fastapi import FastAPI

app = FastAPI()

@app.post('/ask', response_model=AskResponse,
          responses={422: {'model': ErrorResponse}})
@trust_gate
async def ask(req: AskRequest) -> AskResponse:
    return await orchestrator.handle(req)
```

## Docker

Everything self-hosted, so no data leaves the box — PDPL-friendly and demo-portable. `docker compose up` starts the API, vector DB, cache and model runtime.

```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .
COPY app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports:
      - 8000:8000
    env_file: .env
    depends_on: [qdrant, redis, ollama]
  qdrant:            # vector DB
    image: qdrant/qdrant
    ports:
      - 6333:6333
    volumes:
      - ./data/qdrant:/qdrant/storage
  redis:             # cache
    image: redis:7
  ollama:            # local model runtime (Falcon / JAIS / Llama)
    image: ollama/ollama
    ports:
      - 11434:11434
    volumes:
      - ./data/ollama:/root/.ollama
```

## Latency

Target a grounded answer in roughly 2 seconds to first token. Budget per stage (p50):

| Stage | Budget | How to hold it |
| --- | --- | --- |
| Intent routing | \~150 ms | Tiny model or rules, not the big LLM |
| Embed query | \~40 ms | Cache + batch |
| Vector search | \~30 ms | Qdrant HNSW index |
| Rerank (top 4) | \~120 ms | Small cross-encoder, few candidates |
| LLM answer (streamed) | \~1.5–2 s | Stream tokens; keep context to 4 chunks |
| Guardrail + audit log | \~50 ms | Async, non-blocking |

**Techniques that matter most:**

- Stream the answer — time-to-first-token beats total time for perceived speed.
- Semantic cache in Redis for repeat questions (huge hit rate on policy FAQs).
- Small model for routing, large model only for the final answer.
- Parallelize independent tool calls with `asyncio.gather`.
- Precompute journey-state on the nightly sweep; serve it from the store at request time.
- Keep the model warm (keep-alive) to avoid cold starts.
- Hard timeouts with graceful fallback: if anything stalls, hand off to a human rather than hang.

## Best AI practices

Most of these map straight to the judging guardrails, so they are not optional polish — they are points.

- **Ground first:** answer only from retrieved policy; never free-generate a policy fact.
- **Always cite:** every answer carries a source (`policy_id` + section); no citation means no claim — hand off instead.
- **Confidence gate:** below threshold, say you are unsure and route to a human (the brief's exact rule).
- **Sensitive-topic routing:** visa, medical, disciplinary, grievance go to a person, never answered by the bot.
- **Consent-gated sentiment:** pulse/sentiment used only with opt-in; the employee can view and revoke it.
- **Human-in-the-loop:** every action that affects an employee carries a named owner.
- **Audit everything:** log each action the companion takes; the employee can see their own log.
- **PII minimization:** redact in logs; store only what is needed, in-region.
- **Prompt-injection safe:** treat retrieved text and user input as data, not instructions.
- **Eval in CI:** Ragas for faithfulness and answer-relevance; block merges that regress citation accuracy.
- **Deterministic where possible:** journey/SLA logic as rules; the LLM only handles language.
- **Keep scores out of performance/discipline:** any predictive signal is for help, never evaluation (brief guardrail).
- **Versioned policy corpus:** re-index on change; stale policy is a known, tested failure mode.
- **Observability + fallbacks:** trace every step (Langfuse); timeouts, retries with backoff, graceful degradation to handoff.

## UI suggestions

Mobile-first (deskless staff), bilingual with a real RTL flip, calm and trustworthy, and visibly employee-owned. The trust surfaces are what judges will click, so make them first-class.

**Key screens / components:**

- **Chat home (the companion):** message thread, voice button, EN/AR toggle that flips the whole layout to RTL, and quick-action chips (My status, Book medical, Where is my laptop).
- **Journey timeline:** visual stage tracker — each step shows status (done / in progress / overdue), target date, what is next and who owns it; overdue items highlighted with a one-tap "chase" action.
- **My data panel:** what we hold about you — profile, journey data, pulse history — with consent toggles, download/export, and a "correct this" action. (This is the Responsible-AI criterion, made clickable.)
- **Activity / audit log:** every action the companion took on your behalf, timestamped.
- **Answer card (cited):** answer text + a source policy chip (tap to open the exact section), a confidence indicator, and a "talk to a person" button when confidence is low.
- **Handoff view:** on escalation, shows the named owner, the summary that was sent, and live status.
- **Pulse check:** opt-in, single question, clearly optional and dismissible.
- **Manager / HRBP view (nice-to-have):** new joiners' progress and blockers, and an early-warning queue — read-only help, not surveillance.

**UX notes:**

- **RTL done properly:** logical CSS properties and `dir=auto`; mirror the layout for Arabic, don't just translate strings.
- **Accessibility:** large tap targets, voice in/out, captions, WCAG contrast.
- **Trust affordances everywhere:** source chips, visible consent toggles, short "why am I seeing this" explainers.
- **Calm microcopy:** supportive, never alarmist on a blocker; semantic status colours (good / warning / critical) used consistently.
- **Suggested stack:** Next.js + React + Tailwind (RTL plugin) + shadcn/ui; or Streamlit for a fast hackathon demo (less RTL polish).

## Request lifecycle (workflow detail)

One `POST /ask` from the employee runs this path:

1. Receive `AskRequest` (employee\_id, message, lang, consent).
2. Orchestrator classifies intent with a small, fast model.
3. **If sensitive** (visa, medical, grievance) — route straight to a human and return a handoff. Stops here.
4. Otherwise route: *status* to the journey agent, *request* to the action agent, else to policy RAG.
5. Policy RAG: embed the question, vector search, rerank; if the top score is below threshold, return a low-confidence handoff.
6. The LLM answers only from the retrieved context, attaching citations and a confidence score.
7. Trust gate: redact PII; if confidence is low or there are no citations, hand off; log the action to the audit trail.
8. Return `AskResponse` (streamed) — the employee sees the answer, its source, and any action taken.

Running in the background, independent of any request: the scheduler sweep (every 6 h) computes journey-state, raises blockers, notifies the employee first, and escalates persistent stalls to the named owner with a handoff card.

## API endpoints (use case to route)

| Endpoint | Purpose / use case | Backed by |
| --- | --- | --- |
| `POST /ask` | Main Q&A + action (policy, status, request) | orchestrator |
| `GET /journey/{id}` | Journey state, stage, blockers | journey\_engine |
| `POST /request` | Start/route a service request | action\_agent |
| `GET /handoff/{id}` | Escalation status + named owner | action\_agent |
| `GET /me/data` | What we hold about you (consent view) | consent |
| `GET /me/audit` | Action/audit log | audit |
| `POST /pulse` | Submit opt-in pulse feedback | friction |
| `POST /voice` | Speech in -> /ask -> speech out | STT + TTS |

## Failure cases & handling

The rule across all of them: never a confident wrong answer and never a hang — degrade to "I'm not sure, here's a person" instead. This is also where the Responsible-AI points are won.

| Category | Failure case | How the companion handles it |
| --- | --- | --- |
| Answers | Retrieval finds nothing or scores low | Say unsure, cite nothing, hand off — never guess |
| Answers | Policy is stale or self-contradictory | Flag it, answer from the dated source, route to the policy owner |
| Answers | Question is ambiguous | Ask one clarifying question before acting |
| Answers | Mixed or wrong language | Detect language, reply in it, fall back to English if unsure |
| Journey/data | Event data missing or late | Degrade to "I can't verify your status, here's who to ask" |
| Journey/data | No SLA target for an event | Skip the check, log the gap, invent no deadline |
| Journey/data | Employee not found | Clean error + route to HR, no partial guesses |
| Journey/data | Conflicting events | Flag the conflict to a human, don't auto-resolve |
| Actions | Downstream system (IT/ITSM) down | Queue, retry with backoff, tell the employee it's queued |
| Actions | Owner unknown or wrong | Default to the HRBP, flag for correction |
| Actions | Duplicate request | Dedupe before creating |
| Proactive | False-positive stall (data lag) | Employee sees it first, soft tone, grace window before escalation |
| Proactive | Alert fatigue / over-escalation | Escalate only past the threshold; dedupe and summarize |
| Proactive | Missed stall (false negative) | Full periodic sweep + document-expiry checks as a backstop |
| Sensitive | Topic slips the classifier | Secondary keyword guard, then human; never auto-answer visa/medical/grievance |
| Sensitive | Employee in distress | Route to a person immediately, don't auto-handle |
| Privacy | No consent for pulse | Sentiment excluded entirely from any signal |
| Privacy | Consent revoked mid-journey | Stop using it, purge, confirm to the employee |
| Privacy | Manager requests private pulse | Blocked by design, not exposed |
| Voice | STT mishears (esp. Arabic dialect) | Show the transcript, confirm intent before any high-stakes action |
| Infra | LLM or vector DB times out / down | Fall back to cached answer or a human handoff, never hang |
| Adversarial | Prompt injection in a doc or input | Treat retrieved text and input as data, not instructions |
| Adversarial | Attempt to read someone else's data | Row-level scoping by employee\_id; refuse and log |

**Graceful degradation ladder** (each step only if the one above fails):

1. Grounded, cited answer.
2. Low confidence or no source -> say unsure, offer a handoff.
3. A system is down -> serve a cached answer, or queue the action and say so.
4. Last resort -> clean handoff to a named human with a summary.

**Hidden-scenario readiness:** the two tests judges are most likely to run are already covered. A *stalled visa* is caught by overdue-event detection, answered with the cited relocation policy, and routed to the named owner. An *employee with incomplete data* hits the "I can't verify, here's who to ask" path — a safe handoff, not a confident wrong answer.

## Architecture & agentic design (deep dive)

The pattern is **agentic RAG**: an orchestrator controls retrieval as a [reasoning loop, not a fixed retrieve-then-generate line](https://www.lyzr.ai/blog/agentic-rag/). This matters because employee questions are often underspecified or multi-step, and a single lookup [turns weak retrieval into confident guessing](https://computer-agents.com/blog/how-to-get-started-with-ai-agents).

**The control loop:** plan -> route -> retrieve -> score the retrieved chunks -> re-query or hand off if weak -> answer. The agent [validates each chunk before using it](https://mastra.ai/articles/agentic-rag) rather than passing conflict to the LLM and hoping.

**Patterns we use** (of the [six common agentic-RAG patterns](https://www.lyzr.ai/blog/agentic-rag/)):

- **Router agent** — classify intent, route to journey / policy / action (our orchestrator).
- **Corrective / Self-RAG** — score retrieved chunks; if the top score is weak, re-query once, then hand off. No confident guessing.
- **Metadata filtering** — every retrieval is filtered by employee, journey, language and policy version, so answers are scoped and current.
- We deliberately skip GraphRAG / heavy multi-hop — it [earns its cost only on cross-source synthesis](https://sumatosoft.com/blog/agentic-rag-enterprise-implementation-guide), which these journeys rarely need.

**Separation of concerns** (the key production rule): retrieval quality is kept separate from agent logic. **LlamaIndex owns retrieval; LangGraph owns orchestration, state and human-gates.** Retrieval is just one tool the orchestrator calls, alongside the journey engine and action tools. Many production teams converge on exactly this split.

**Bounded + observable:** cap the loop at two retrieval attempts, then hand off; trace every step (loop count, scores, latency, cost) so the agent never runs away. And keep journey/SLA logic deterministic — the agent loop is only for language and retrieval.

## Sequence & flow diagrams

Two views for the developer: the synchronous answer path, and the asynchronous proactive path.

### Answer path (synchronous)

Time flows down. Solid arrows are calls; dashed are returns. The escalation to a human only fires on low confidence or a sensitive topic.

&#91;embedded content: sequence · grounded, gated answer\]

### Proactive path (asynchronous)

The scheduler sweep runs independently of any request. The employee is always notified before any human escalation, and only a persistent stall (past the threshold) reaches a named owner.

&#91;embedded content: flow · proactive stall detection and escalation\]

## RAG pipeline best practices

Most agent failures are retrieval failures, so this is where to invest. The 2026 production pipeline is [hybrid retrieval -> rerank -> generate, with evals at every stage](https://dev.to/ai_builder/rag-in-production-in-2026-beyond-naive-chunk-and-embed-3803) — the naive "chunk, embed, stuff top 3" collapses in production.

- **Chunking:** split by [semantic boundaries](https://www.stack-ai.com/insights/chunking-strategies-for-rag-how-to-optimize-document-retrieval) (policy headings/sections) first; fall back to \~500-token windows with 10–20% overlap only when a section is too big. Store `policy_id`, `section`, `version`, `lang` as metadata on every chunk.
- **Hybrid search:** run BM25 (keyword) + dense vector in parallel and fuse — [pure vector misses exact identifiers](https://dev.to/ai_builder/rag-in-production-in-2026-beyond-naive-chunk-and-embed-3803) like visa codes, policy numbers, Emirates ID. Merge \~50 candidates.
- **Rerank:** score those \~50 with a cross-encoder (bge-reranker), keep the top 4–5. "Retrieving 3 and reranking 3 is theater."
- **Metadata filter:** scope every query by employee, journey, language and policy version, so answers are correct and current.
- **Generation:** temperature 0 for policy answers; the system prompt forbids answering outside the retrieved context.
- **Citation:** attach `policy_id` + `section` from chunk metadata to every answer (drives the source chip in the UI).
- **Context budget:** keep `top_k x avg_chunk_tokens + system + query + tools` under the model's context window.
- **Eval in CI:** [Ragas](https://dev.to/ai_builder/rag-in-production-in-2026-beyond-naive-chunk-and-embed-3803) for faithfulness, answer-relevancy, and context precision/recall; block merges that regress.
- **Cache + re-index:** semantic cache for repeat policy questions; re-index on every policy change (versioned corpus) — stale policy is a tracked failure mode.

## Parameters & configuration

Starting defaults for every tunable — all live in `config.py` / `.env`, none hard-coded. Tune against the eval set, not by feel.

| Group | Parameter | Default | Notes |
| --- | --- | --- | --- |
| Retrieval | `chunk_size` | 500 tokens | Semantic-first; this is the fallback window |
| Retrieval | `chunk_overlap` | 10–20% | Sentence-based overlap |
| Retrieval | `hybrid_candidates` | 50 | Merged BM25 + dense before rerank |
| Retrieval | `rerank_keep` | 4–5 | Kept after the cross-encoder |
| Retrieval | `MIN_SCORE` | 0.5 | Below this, hand off (don't answer) |
| Retrieval | `embedding_model` | BGE-M3 | Multilingual incl. Arabic |
| Generation | `temperature` | 0 | Deterministic, grounded answers |
| Generation | `max_tokens` | 512 | Answers stay short |
| Generation | `MIN_CONFIDENCE` | 0.6 | Below this, say unsure + hand off |
| Generation | `router_model` | 7–8B | Small/fast for intent routing |
| Generation | `answer_model` | Falcon-H1 Arabic / larger | Grounded answers |
| Agent loop | `max_retrieval_attempts` | 2 | Then hand off — bounded loop |
| Proactive | `sweep_interval` | 6 h | APScheduler |
| Proactive | `ESCALATE_AFTER` | 2 days overdue | Tune per journey/stage |
| Proactive | `pulse_weight` | 0.1 | Consent-gated tie-breaker only |
| Infra | `cache_ttl` | 24 h | Semantic response cache |
| Infra | `request_timeout` | 8 s | Hard timeout -> handoff |
| Infra | `llm_timeout` | 5 s | Then fallback |
| Infra | `max_retries` | 2 | Exponential backoff |
| Infra | `rate_limit` | 60 / min / user | Abuse + injection-campaign protection |

## Guardrails (defense in depth)

Guardrails are programmatic input/output controls wrapped around the model. The [OWASP Top 10 for LLM Applications 2025](https://clickhouse.com/resources/engineering/llm-guardrails) ranks **prompt injection as LLM01** (the #1 risk) and **sensitive-information disclosure as LLM02** — the two our rails most directly address. We layer rails the way [NeMo Guardrails splits them](https://bigdataboutique.com/blog/ai-guardrails-implementing-safety-production-llm-apps): input, retrieval, output, execution and dialog, each explainable and testable.

- **Input rails:** PII detection/redaction (Presidio), prompt-injection detection (Prompt Guard 2 / Lakera), language + length validation, rate limiting. Retrieved text and user input are treated as data, never instructions.
- **Retrieval rails:** row-level scoping by employee, filter by policy version; if nothing clears `MIN_SCORE`, hand off instead of answering.
- **Output rails (our `trust_gate`):** citation-required + confidence gate, PII redaction on the way out, Pydantic/Guardrails-AI schema validation, optional Llama Guard output-safety classifier.
- **Execution / action rails:** a human gate on anything that affects an employee; idempotent, audited tool calls; sensitive topics never auto-executed.
- **Dialog rails:** refuse off-scope, de-escalate, and confirm before any high-stakes voice action.

**OWASP LLM Top 10 mapping:**

| Risk | How we mitigate |
| --- | --- |
| LLM01 Prompt injection | Input rails + data-not-instructions rule; injection classifier; rate limiting |
| LLM02 Sensitive info disclosure | Presidio redaction, row-level scoping, least-data, in-region storage |
| LLM04 Data/model poisoning | Trusted, versioned policy corpus only; no open ingestion |
| LLM05 Improper output handling | Schema validation + citation gate before anything is shown or acted on |
| LLM06 Excessive agency | Human gate, bounded agent loop, idempotent tools, named owners |

**Open-source stack:** Presidio strips PII at ingress, Prompt Guard detects injection inline, NeMo Guardrails orchestrates dialog policy, Llama Guard classifies output safety, and a schema validator gates structured output. Rails add \~10–200 ms — budgeted in the latency table.

## Compliance & governance

Mapped to UAE law and the AI-governance standards a government-entity buyer will expect. This is the backbone of the 25% Responsible-AI score.

**UAE PDPL (Federal Decree-Law 45/2021) mapping:**

| Requirement | How we comply |
| --- | --- |
| Explicit, revocable consent (Art. 5) | Opt-in for pulse/sentiment; captured and revocable; no sentiment without it |
| Transparency / notice | "What we hold about you" panel; purpose stated in-product |
| Data-subject rights | Employee can view, export and correct their own data |
| Cross-border transfer (Art. 22–23) | In-region / on-prem inference; personal data never leaves the UAE |
| Proportionate security | Encryption, row-level access, least-data, full audit log |
| DPIA | High-risk processing triggers a DPIA before deployment |
| Accountability / DPO | Named owners + defined governance roles |
| Sensitive data | Visa/medical/grievance routed to humans, never auto-processed |

**Data handling:** residency — all inference and storage in-region (self-hosted models); retention — journey data kept only for the active journey plus a defined window, pulse purged on revoke, retention configurable; minimization — store only what a task needs; purpose limitation — data is used to help, never for performance or disciplinary decisions (brief guardrail).

**Human oversight:** a named human owner on every intervention, a human gate on high-stakes actions, and a firm line that the companion informs and assists but [never decides pay, scheduling or career](https://www.dayforce.com/blog/dayforce-iso42001) — those require human judgment.

**Standards alignment:** structure governance to [ISO/IEC 42001](https://arrakisconsulting.com/ISO42001.html) (the certifiable AI management system standard) and the [NIST AI RMF](https://secureprivacy.ai/blog/how-does-ai-governance-work-across-the-ai-lifecycl) (Govern / Map / Measure / Manage); run a DPIA; keep technical documentation and an audit trail. These map cleanly onto the UAE's AI-ethics direction (transparency, fairness, accountability) and make the solution auditable and reusable across other government entities.

## Scope for the hackathon (keep it simple)

Everything above is a reference library — pick from it, don't build all of it. For a 3-minute demo on \~200 synthetic employees and 10–15 short policies, the simple version wins. This is the adjustable, low-effort build.

**Build this (the five required capabilities):**

1. **Load the pack** into DuckDB or just pandas in memory — no database setup needed at this size.
2. **Journey-state:** a plain rules check of `journey_events` vs `journey_maps` targets. This alone nails "day 5, laptop not issued."
3. **Policy Q&A:** basic RAG over the \~15 docs — embeddings + top-k is plenty. Cite the source file; if unsure, say so and hand off.
4. **Requests + handoff:** update a `service_requests` status and generate a short handoff summary card.
5. **Friction + escalate:** flag overdue events/requests, show the employee first, escalate with a summary.
6. **UI:** one chat + a journey timeline + a "my data / consent" panel. Streamlit is fast and fine.

**Skip or fake for the demo (don't over-build):**

- Hybrid search + cross-encoder rerankers — overkill for 15 policies; plain top-k retrieval is enough.
- Heavy guardrail stack (NeMo / Llama Guard / Presidio) — a good system prompt + confidence threshold + a sensitive-topic keyword check demos the same behavior.
- Multi-agent frameworks — one orchestrator function with if/else routing beats a full LangGraph graph for a 3-min demo.
- Voice, Arabic RTL, manager view — nice-to-haves; add only if time is left.
- ISO 42001 / full DPIA / Docker / on-prem models — describe these in the 2-page note, don't implement them.

**What actually wins points** (match the weights):

- Nail the two scenarios end-to-end — day-5 laptop and stalled visa (30%).
- Make the consent panel, "see your data" and audit log clickable live (25%).
- Keep the chat simple, cited and trustworthy (25%).

The deeper sections above are there for the pilot and the solution note, not the demo. Build small, demo the two scenarios, point to this doc for the rest.

## UI/UX guide (for the developer)

A fuller build guide than the UI suggestions above — principles, each screen's contents, components, states and RTL/accessibility. Employee experience is 25% of the score and judged live, so the UX is a feature, not decoration.

### UX principles

- **Employee-owned:** the person always sees their own data and controls it. Nothing feels like surveillance.
- **Trust is visible:** cited answers, consent toggles, an audit log, and a named owner on every escalation — all on screen, not buried.
- **Always show the next step:** every view answers "where am I, what is next, who owns it."
- **Calm, not alarmist:** blockers are shown supportively; reserve red for truly critical.
- **Low cognitive load:** progressive disclosure, quick-action chips, short cards.
- **Mobile-first + bilingual:** works at phone width; EN/AR with a real RTL flip.

### Screens (what each contains)

1. **Chat (home)** — message thread; input box with a voice button; language toggle (EN/AR, flips to RTL); quick-action chips (My status, Where is my laptop, Book medical); answers render as cited cards.
2. **Journey timeline** — vertical stage tracker; each step shows status (done / in progress / overdue), target date, the next step and who owns it; overdue steps highlighted with a one-tap "chase" action.
3. **Answer card** — the answer, a source chip (tap opens the exact policy section), a confidence pill, and a "talk to a person" button when confidence is low.
4. **My data + consent** — what is held about you (profile, journey, pulse); consent toggles; export; "correct this"; revoke. The Responsible-AI centerpiece.
5. **Audit log** — a timestamped list of every action the companion took for you.
6. **Handoff / escalation** — the named owner, the summary that was sent, and live status.
7. **Pulse** — opt-in, single question, clearly optional and dismissible.
8. **Manager / HRBP view (nice-to-have)** — new joiners' progress and an early-warning queue; read-only help, never surveillance.

### Component inventory

Build these once, reuse everywhere: message bubble; **answer card** (text + source chip + confidence pill + optional handoff button); **quick-action chip**; **timeline step** (status icon + target date + owner + chase button); **consent toggle row**; **my-data table**; **audit row**; **handoff card**; **pulse card**; **status badge** (good / warning / critical); language toggle; voice button.

### States (handle on every screen)

- **Loading:** skeletons, not spinners, so the layout doesn't jump.
- **Empty:** a friendly prompt, never a blank screen.
- **Error:** plain message + retry, and a handoff option if it persists — never a stack trace.
- **Low confidence:** swap the answer for an "I am not sure" card with a "talk to a person" button.
- **Offline / queued:** tell the employee the request is queued and will complete.

### Visual + design tokens

- **Type:** one clean sans (Inter or system) + an Arabic face (IBM Plex Sans Arabic or Noto Sans Arabic). Modest scale: \~13/15/20/28.
- **Spacing + radius:** 4/8/16/24 spacing, 8–12px radius, generous white space.
- **Semantic colors:** success (green), warning (amber), critical (red, sparingly), info (blue). Neutral greys for everything else. Don't carry meaning by colour alone — pair with an icon or label.

### RTL + accessibility

- Use `dir=auto` and logical CSS properties (margin-inline, etc.) so Arabic mirrors the whole layout, not just the text.
- WCAG AA contrast; tap targets >= 44px; full keyboard navigation; captions for voice; ARIA labels on icons and chips.

### Screen flow (doubles as the demo path)

1. Open app -> **Chat**.
2. Ask "where is my laptop?" -> **Journey timeline** highlights the overdue step.
3. **Answer card** cites the onboarding policy; employee taps **chase**.
4. **Handoff card** is routed to the named IT owner with a summary.
5. Open **My data + consent** -> toggles, audit log, "see what we hold."

That single flow demonstrates journey-awareness, cited answers, action + handoff, and the trust surfaces — the four things judges score.

**Build tip:** Streamlit gets chat + timeline + panels working fastest for the demo; Next.js + Tailwind + shadcn/ui is the choice if you want polish and proper RTL.

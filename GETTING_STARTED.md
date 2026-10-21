# Getting started — from zero to running Rafiq

Everything needed to go from a bare machine to the full demo: prerequisites, install,
configuration, running, first tour, tests, the API, and troubleshooting.

---

## 1. Prerequisites

| Need | Version | Check with |
| --- | --- | --- |
| Python | 3.12 or 3.13 | `python3 --version` |
| uv (recommended) | latest | `uv --version` |
| Git | any recent | `git --version` |

Install Python if missing: [python.org/downloads](https://www.python.org/downloads/) or
`brew install python@3.12` (macOS) / `sudo apt install python3.12 python3.12-venv` (Debian/Ubuntu).

Install **uv** (a fast Python package manager — it creates the environment and installs the exact
dependencies in seconds):

```bash
# macOS / Linux
curl -LsS https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# or via an existing pip
pip install uv
```

If `uv` is not found after install, open a new terminal (the installer adds itself to your PATH).

---

## 2. Get the code

```bash
git clone https://github.com/0xv3nm09/rafiq-companion.git
cd rafiq-companion
```

The repository is private during review — use your invited GitHub account, or download and unzip
the repository archive if you were given one.

---

## 3. Install

```bash
uv sync          # creates .venv and installs everything (app + dev tools)
```

**No uv?** Plain pip works identically:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

What gets installed: FastAPI + Uvicorn (the API), pandas (the data layer), Pydantic (schemas),
httpx, pytest. No databases, no vector stores, no model downloads — the retrieval index is
built in-memory from the policy files at startup.

---

## 4. Configuration (optional)

```bash
cp .env.example .env
```

Everything runs with zero configuration. The knobs, all optional:

| Setting | Default | Effect |
| --- | --- | --- |
| `SIM_DAY` | `5` | The simulated "today" for the demo clock (journey days are computed from it) |
| `MIN_SCORE` | `0.5` | Retrieval floor — below it Rafiq says "I'm not sure" and hands off |
| `MIN_CONFIDENCE` | `0.6` | Trust-gate floor for policy answers |
| `ESCALATE_AFTER` | `2` | Days overdue before a blocker escalates to the named owner |
| `OPENROUTER_API_KEY` / `GROQ_API_KEY` | *(empty)* | Optional: adds generative polish to policy answers. Without a key, answers are composed extractively from the retrieved policy — still cited, zero hallucination surface |

---

## 5. Data

The **synthetic pack ships in the repo** (`data/synthetic/`) and is used automatically:
200 employees across onboarding and internal mobility, journey events, service requests,
opt-in pulse feedback, 17 bilingual policies (EN/AR), and journey maps with SLA targets
and named owners.

Two demo stars are deterministic:

- **E0421 · Aisha Al Mansoori** — onboarding day 5, laptop 2 days past its day-3 target.
- **E0422 · Omar Haddad** — internal transfer day 18, receiving-team sign-off 3 days stalled.

To run on the **official challenge pack**: create `data/pack/`, drop the pack files in
(`employees.csv`, `journey_events.csv`, `service_requests.csv`, `pulse_feedback.csv`,
`policies/`, `journey_maps.md`) and restart — the loader prefers it automatically and maps
columns through aliases. Regenerate the synthetic pack any time:

```bash
make data        # or: uv run python scripts/make_synthetic_data.py --employees 200 --sim-day 5
```

---

## 6. Run

```bash
make run         # or: uv run uvicorn app.main:app --port 8000
```

Open **http://localhost:8000**. What you'll see: a side rail with role buttons
(Employee / Manager / HR / Owner), page navigation, a notification bell, the language
toggle (EN/ع), and the Home dashboard already showing the current employee's stage and
any open blocker.

Run a **clean demo state** any time (clears notices, handoffs, audit, consent):

```bash
curl -X POST http://localhost:8000/reset-demo
```

---

## 7. First tour (2 minutes)

1. **Home** — E0421's blocker ("Laptop issued", overdue, owner IT Service Desk) is on screen before she asks.
2. **Ask Rafiq** → tap the chip *Where is my laptop?* → a computed answer citing policy **ONB-07**; tap the citation chip to read the exact policy section.
3. **Chase it for me** → a structured handoff card is raised; *View handoff* shows what was sent.
4. **My journey** — the SLA timeline with owners and real-process hints (medical at the visa window, Emirates ID biometrics at the same visit).
5. **My data** — everything held about you; toggle **pulse consent** and watch the audit log record it.
6. Role buttons — **Manager** (Grace Okonkwo, risk-sorted team of 34), **HR** (Fatima's early-warning queue + handoff inbox with acknowledge/resolve), **Owner** (IT Service Desk inbox).
7. **Where journeys stall** — the aggregate view · **ع** — the full RTL flip · **Viewing as → E0422** — the stalled-transfer scenario citing **MOB-01**.

---

## 8. Tests

```bash
make test        # or: uv run pytest -q        → 39 passed
```

Coverage: the journey engine (SLA rules, waived events, early completion), friction weights,
RAG grounding (citations, Arabic retrieval, low-confidence handoff), intent routing (sensitive
→ human, status → journey, verbs → action), the proactive sweep, consent gating, the audit log,
and the manager/HRBP views (including the privacy guarantee that manager payloads contain no
pulse data).

---

## 9. The API (all of it)

| Endpoint | What it does |
| --- | --- |
| `POST /ask` | The companion: `{employee_id, message, lang}` → routed to journey / policy / action, trust-gated. Also starts requests — phrasings like "Book my medical fitness test" create and route one |
| `GET /journey/{id}` | Journey state + full timeline |
| `GET /me/data?employee_id=` | "What we hold about you" |
| `GET /me/audit?employee_id=` | The employee-visible action log |
| `GET /me/notices?employee_id=` | Proactive notices (bell tray) |
| `POST /me/notices/read` | Mark notices read |
| `POST /pulse` | Submit an opt-in pulse score (`{employee_id, score, consent}`) |
| `POST /consent` | Set pulse consent (`{employee_id, consent_pulse}`) |
| `GET /handoff/{id}` · `POST /handoff/{id}/status` | Handoff card detail / acknowledge-resolve |
| `GET /handoffs` | All open handoff cards |
| `GET /employees` · `GET /people/managers` · `GET /people/hrbps` · `GET /people/owners` | The demo switcher data |
| `GET /team/{manager_id}` | Manager view (risk-sorted reports, no pulse data) |
| `GET /queue/{hrbp_id}` | HRBP early-warning queue + stalls by owner |
| `GET /stalls` | Where journeys stall most (aggregate only) |
| `GET /policy/{id}` | Citation drill-down (policy sections) |
| `POST /sweep` | Run the proactive sweep now |
| `POST /reset-demo` | Clean runtime state for a fresh demo |
| `GET /health` | Liveness + which data source is loaded |

Example:

```bash
curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" \
  -d '{"employee_id":"E0421","message":"Where is my laptop?","lang":"en"}'
```

---

## 10. Troubleshooting

| Symptom | Fix |
| --- | --- |
| `uv: command not found` | New terminal after install, or add `~/.local/bin` to PATH |
| Python version error | The project pins 3.12–3.13: `uv python install 3.12` then retry |
| Port already in use | `uvicorn ... --port 8001` and open that port |
| Demo looks "used" (notices read, consent on) | `curl -X POST localhost:8000/reset-demo` |
| Answer says "I'm not sure" a lot | The policy question is outside the corpus — by design; try "annual leave", "laptop", "gratuity", "visa" |
| Want the demo clock at another day | Set `SIM_DAY` in `.env` and restart |

---

## 11. Regenerating the submission artifacts

```bash
uv run python submission/video/make_video.py   # demo video (captures + narration + captions)
```

The video pipeline reads per-shot browser captures from `submission/video/shots/` — see
`docs/DEMO_SCRIPT.md` for the shot list.

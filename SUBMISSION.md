# Rafiq — Submission One-Pager

**Team:** Muhammad Omaid — **Magnus Mage** (dev team)
**Challenge:** Ignyte × Emirates — Employee AI Companion
**Repository:** https://github.com/0xv3nm09/rafiq-companion (this repo, private during review)

## Deliverables

| # | Deliverable | Where |
| --- | --- | --- |
| 1 | Working prototype (runnable repo with setup steps) | This repository — see the 60-second start below |
| 2 | Demo video, 1:46 (≤3:00) — two employee scenarios, narration + captions | [rafiq-demo.mp4 — release page](https://github.com/0xv3nm09/rafiq-companion/releases/tag/demo-video) · also uploaded with the entry |
| 3 | Solution note, 2 pages — includes consent, privacy and human oversight | [docs/rafiq-solution-note.pdf](https://github.com/0xv3nm09/rafiq-companion/blob/master/docs/rafiq-solution-note.pdf) · source: [docs/SOLUTION_NOTE.md](https://github.com/0xv3nm09/rafiq-companion/blob/master/docs/SOLUTION_NOTE.md) |

Both required scenarios are in the video and reproducible live: **E0421** (onboarding day 5, laptop overdue) and **E0422** (internal transfer with a stalled approval).

## 60-second start guide

**Prerequisites:** Python 3.12/3.13 + [uv](https://docs.astral.sh/uv/)
(`curl -LsS https://astral.sh/uv/install.sh | sh` — Windows: `irm https://astral.sh/uv/install.ps1 | iex`;
or plain pip: `pip install -e ".[dev]"` in a venv).

```bash
uv sync                                   # or: pip install -e ".[dev]"
uv run uvicorn app.main:app --port 8000   # or simply: make run
uv run pytest -q                          # 39 tests: engine, RAG grounding, consent, sweep
```

Open `http://localhost:8000` — no API keys, no cloud services; the synthetic pack ships in the
repo and no data leaves the machine.

**What to click (every step one click from the side rail):**

1. **Home** opens on E0421 with the laptop blocker already flagged — before she asks.
2. **Ask Rafiq** → *Where is my laptop?* → cited answer (ONB-07) → *Chase it for me* → handoff card.
3. **My journey** — SLA timeline with owners and real-process hints.
4. **My data** → toggle pulse consent live → the audit log records everything.
5. Role buttons: **Manager** (risk-sorted team) · **HR** (early-warning queue + handoff inbox) ·
   **Owner** (IT Service Desk inbox with acknowledge/resolve).
6. **Where journeys stall** (aggregate) · **ع** (full RTL flip) · **Viewing as → E0422** (stalled transfer).

## What was built

A deterministic-first companion in four parts — journey-state engine (events vs `journey_maps.md`
targets), grounded bilingual answer layer (BM25, every answer cited), action & routing (requests
and handoff cards to named owners), friction radar with a proactive sweep — wrapped in a trust
layer: opt-in consent enforced at the signal level, employee-visible audit log, PII redaction,
and no use in performance or disciplinary decisions, ever.

## After acceptance

If accepted, the **Magnus Mage dev team** carries this forward: the pilot swap is data and
read-only connectors (the loader accepts the official pack in `data/pack/` with zero code
change), the sovereign model path (Falcon-H1 Arabic / JAIS on-premise) is a one-file swap, and
the deterministic core stays as is. Roadmap and current limitations are stated plainly in the
README.

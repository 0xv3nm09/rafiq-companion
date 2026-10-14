#!/usr/bin/env python3
"""Rafiq submission one-pager — single A4 page, clickable links (ReportLab).
Palette: pdf.py palette.cascade monochrome seed 7 (same as the solution note).
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle)

PAGE_BG  = colors.HexColor("#f5f6f6")
STRIPE   = colors.HexColor("#edefef")
HEADER   = colors.HexColor("#455964")
BORDER   = colors.HexColor("#b7cad3")
ICON     = colors.HexColor("#3a667d")
ACCENT   = colors.HexColor("#277da8")
TEXT     = colors.HexColor("#232527")
MUTED    = colors.HexColor("#777e81")

W, H = A4
M = 15 * mm
AVAIL = W - 2 * M
REPO = "https://github.com/0xv3nm09/rafiq-companion"

S = {
    "title": ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=TEXT),
    "meta":  ParagraphStyle("m", fontName="Helvetica", fontSize=9.5, leading=13, textColor=MUTED),
    "h2":    ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=11.5, leading=14,
                            textColor=ICON, spaceBefore=8, spaceAfter=3),
    "body":  ParagraphStyle("b", fontName="Helvetica", fontSize=9.4, leading=12.8, textColor=TEXT),
    "bullet": ParagraphStyle("bl", fontName="Helvetica", fontSize=9.4, leading=12.8,
                             textColor=TEXT, leftIndent=10, bulletIndent=1, spaceAfter=1.5),
    "cell":  ParagraphStyle("c", fontName="Helvetica", fontSize=9, leading=12, textColor=TEXT),
    "cellb": ParagraphStyle("cb", fontName="Helvetica-Bold", fontSize=9, leading=12,
                            textColor=colors.white),
    "code":  ParagraphStyle("cd", fontName="Courier", fontSize=8.8, leading=13, textColor=TEXT),
}


def P(t, st="body"):
    return Paragraph(t, S[st])


def link(url, label=None):
    return f'<a href="{url}" color="#277da8"><u>{label or url}</u></a>'


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PAGE_BG)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(M, 9 * mm, "Rafiq — Employee AI Companion · submission one-pager")
    canvas.drawRightString(W - M, 9 * mm, "Muhammad Omaid — Magnus Mage (dev team)")
    canvas.restoreState()


doc = BaseDocTemplate("rafiq-submission-one-pager.pdf", pagesize=A4,
                      leftMargin=M, rightMargin=M, topMargin=13 * mm, bottomMargin=14 * mm,
                      title="Rafiq — Submission One-Pager",
                      author="Muhammad Omaid — Magnus Mage",
                      subject="Ignyte × Emirates Employee AI Companion — submission summary",
                      creator="Magnus Mage")
doc.addPageTemplates([PageTemplate(id="p", frames=[
    Frame(M, 14 * mm, AVAIL, H - 13 * mm - 14 * mm, id="f")], onPage=on_page)])

story = []
story.append(P("Rafiq — Employee AI Companion · Submission", "title"))
story.append(Spacer(1, 3))
story.append(P("<b>Team:</b> Muhammad Omaid — Magnus Mage (dev team) · "
               "<b>Challenge:</b> Ignyte × Emirates — Employee AI Companion · "
               "<b>Repository:</b> " + link(REPO) + " <i>(private during review)</i>", "meta"))
story.append(Spacer(1, 6))

story.append(P("One line", "h2"))
story.append(P("An employee-owned AI companion that carries a person through <b>both</b> required "
               "journeys — onboarding and internal mobility — knows where they are against "
               "service-level targets, answers policy questions with inline citations, starts and "
               "routes routine requests, and catches friction <b>before</b> it escalates — on a "
               "consent-first, in-region, UAE-sovereign footing."))
story.append(Spacer(1, 4))

story.append(P("What the submission contains", "h2"))
rows = [
    ["Deliverable", "Where / link"],
    ["Working prototype — runnable repo with setup steps",
     link(REPO) + " · start guide below · CI runs the 39-test suite on every push"],
    ["Demo video — 1:46 (≤3:00), both required scenarios, narration + burned captions",
     "Web link: " + link(REPO + "/releases/tag/demo-video") +
     " · also uploaded as a file with this entry"],
    ["Solution note — 2 pages incl. consent, privacy, human oversight",
     "Web link: " + link(REPO + "/blob/master/docs/rafiq-solution-note.pdf") +
     " · also uploaded as a file with this entry"],
]
t = Table([[P(c, "cellb" if r == 0 else "cell") for c in row] for r, row in enumerate(rows)],
          colWidths=[AVAIL * 0.42, AVAIL * 0.58], repeatRows=1, hAlign="CENTER")
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), HEADER),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, STRIPE]),
    ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]))
story.append(t)
story.append(Spacer(1, 4))

story.append(P("60-second start guide", "h2"))
story.append(P("Prerequisites: Python 3.12/3.13 and uv\u00a0\u2014 install with "
               '<font face="Courier" size="8.2">curl -LsS https://astral.sh/uv/install.sh | sh</font>'
               " (Windows PowerShell: <font face='Courier' size='8.2'>irm astral.sh/uv/install.ps1 | iex</font>); "
               "or plain pip in a venv: <font face='Courier' size='8.2'>pip install -e &quot;.[dev]&quot;</font>", "body"))
story.append(P("uv sync&nbsp;&nbsp;·&nbsp;&nbsp;uv run uvicorn app.main:app --port 8000"
               "&nbsp;&nbsp;(or: make run)&nbsp;&nbsp;·&nbsp;&nbsp;uv run pytest -q&nbsp;&nbsp;"
               "(39 tests)", "code"))
story.append(Spacer(1, 2))
story.append(P("Open <b>http://localhost:8000</b> — no API keys, no cloud; the synthetic pack "
               "ships in the repo and no data leaves the machine. Then, every step one click "
               "from the side rail:", "body"))
story += [
    Paragraph(t, S["bullet"], bulletText="•") for t in [
        "<b>Home</b> opens on E0421 (Aisha, onboarding day 5) with the laptop blocker already "
        "flagged — before she asks.",
        "<b>Ask Rafiq</b> → <i>Where is my laptop?</i> → computed answer citing policy ONB-07 → "
        "<i>Chase it for me</i> → a complete handoff card goes to the named owner.",
        "<b>My journey</b> — SLA timeline with real-process hints; <b>My data</b> → toggle pulse "
        "consent live; the audit log records every action.",
        "Role buttons: <b>Manager</b> (risk-sorted team, pulse-free) · <b>HR</b> (early-warning "
        "queue + handoff inbox) · <b>Owner</b> (IT Service Desk inbox, acknowledge/resolve).",
        "<b>Where journeys stall</b> — the aggregate view · <b>AR</b> — full Arabic RTL flip · "
        "<b>Viewing as → E0422</b> — the stalled-transfer scenario citing MOB-01.",
    ]]
story.append(Spacer(1, 4))

story.append(P("Guardrails, stated as built", "h2"))
story.append(P("Synthetic data only, never uploaded to services that retain or train on it · the "
               "companion works for the employee — the manager view structurally contains no pulse "
               "data · sentiment used only with opt-in consent, revocable, employee-visible ·&nbsp;"
               "every intervention routes to a named human owner ·&nbsp;every policy answer cites "
               "its source, and when unsure the companion says so and hands off.", "body"))
story.append(Spacer(1, 4))

story.append(P("If accepted", "h2"))
story.append(P("The <b>Magnus Mage dev team</b> carries Rafiq forward: the pilot swap is data and "
               "read-only connectors (the loader accepts the official pack in "
               "<font face='Courier' size='8.4'>data/pack/</font> with zero code change), the "
               "sovereign model path (Falcon-H1 Arabic / JAIS on-premise, in-region) is a one-file "
               "swap, and the deterministic core — the part a pilot can trust — stays as is.",
               "body"))

doc.build(story)
print("built rafiq-submission-one-pager.pdf")

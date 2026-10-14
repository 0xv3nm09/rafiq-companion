#!/usr/bin/env python3
"""Generate the zoned-architecture diagram (light + dark SVG).

Zones top-to-bottom: EMPLOYEE -> GUARDRAIL -> COMPANION STACK -> AI -> DATA ->
PEOPLE. The guardrail is drawn as a full-width band because every message and
every answer crosses it. A dot marks each point where personal data crosses a
zone boundary (the PDPL story, made visible).

Run:  uv run python docs/diagrams/make_zone_diagram.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent
W = 900
ZX, ZW = 40, 820
GAP = 46

LIGHT = dict(bg="#ffffff", zone="#f7f9fc", line="#d8dfeb", ink="#0b1f3a",
             sub="#5b6b81", body="#3d4a5f", chip="#fdf6e8", chip_ln="#ecd9ae",
             chip_tx="#7a5b12", ai="#e7f4f2", ai_ln="#c3e2dd", ai_tx="#0b5952",
             guard="#fdfaf0", guard_ln="#ecd9ae", dot="#b45309", arrow="#9aa7ba",
             title="#8a94a6", num="#0b1f3a")
DARK = dict(bg="#0e1417", zone="#17252a", line="#2c4046", ink="#e8f1f2",
            sub="#93abb1", body="#c3d5d9", chip="#241d0f", chip_ln="#66511a",
            chip_tx="#e6c887", ai="#0f2825", ai_ln="#2b544d", ai_tx="#8fd9cc",
            guard="#221c0e", guard_ln="#66511a", dot="#e8a13c", arrow="#54707a",
            title="#5d757c", num="#e8f1f2")

# (num, title, subtitle, chips[(text, kind n|a|g)], body, height)
ZONES = [
    ("1", "EMPLOYEE ZONE", "what the employee sees — mobile-first · EN/AR RTL",
     [("chat", "n"), ("journey timeline", "n"), ("my data + consent", "n"), ("audit log", "n"), ("notices", "n")],
     "Employee-owned surfaces: everything Rafiq holds or did is viewable and revocable here.", 128),
    ("2", "GUARDRAIL ZONE", "one trust gate — nothing bypasses it",
     [("in: PII redaction", "g"), ("in: sensitive-topic guard", "g"), ("out: citation required", "g"),
      ("out: confidence gate", "g"), ("out: audit write", "g")],
     "No source, no claim: below the confidence floor the answer becomes a human handoff.", 122),
    ("3", "COMPANION STACK ZONE", "FastAPI · rules-first orchestration",
     [("POST /ask", "n"), ("orchestrator", "n"), ("journey agent", "n"), ("policy agent", "n"),
      ("action agent", "n"), ("friction radar", "n"), ("proactive sweep", "n")],
     "Deterministic journey engine (events vs journey_maps targets) + grounded answers + chases.", 150),
    ("4", "AI ZONE", "the only place a model is called — llm.py",
     [("BM25 EN/AR", "a"), ("Arabic normalization", "a"), ("heading anchors", "a"),
      ("extractive default", "a"), ("Falcon-H1 / JAIS on-prem · prod", "a")],
     "Retrieval is local and dependency-free; the sovereign path swaps one file, nothing else.", 122),
    ("5", "DATA ZONE", "challenge pack in / synthetic pack mirrors it",
     [("journey_events", "n"), ("service_requests", "n"), ("pulse_feedback", "n"),
      ("journey_maps.md", "n"), ("policies EN/AR", "n"), ("runtime: consent·audit·handoffs", "n")],
     "Row-scoped by employee_id; pulse used only while consent is ON; pack stays read-only.", 122),
    ("6", "PEOPLE ZONE", "named owners — every escalation has one",
     [("IT Service Desk", "n"), ("HR Mobility", "n"), ("HR Business Partner", "n"),
      ("Line Manager", "n"), ("Visa & Immigration", "n")],
     "Handoff cards land complete: stage, blocker, what's been tried, named owner.", 116),
]

TITLE_H, LEGEND_H = 56, 56
TOTAL_H = TITLE_H + sum(z[5] + GAP for z in ZONES) - GAP + LEGEND_H


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def chip_w(text: str) -> float:
    return 14 + 6.05 * len(text)


def build(p: dict) -> str:
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{TOTAL_H}" viewBox="0 0 {W} {TOTAL_H}">',
           f'<rect width="{W}" height="{TOTAL_H}" fill="{p["bg"]}"/>',
           f'<text x="{W/2}" y="38" font-family="Helvetica,Arial,sans-serif" font-size="11.5" '
           f'font-weight="700" fill="{p["title"]}" text-anchor="middle" letter-spacing="2.4">'
           f'RAFIQ · ZONED ARCHITECTURE — PERSONAL DATA CROSSES A BOUNDARY AT EACH DOT</text>']

    y = TITLE_H
    for i, (num, title, sub, chips, body, h) in enumerate(ZONES):
        if i > 0:
            ay0, ay1 = y - GAP + 8, y - 8
            mx = W / 2
            out.append(f'<line x1="{mx}" y1="{ay0}" x2="{mx}" y2="{ay1}" '
                       f'stroke="{p["arrow"]}" stroke-width="1.5"/>')
            out.append(f'<polygon points="{mx-6},{ay1-1} {mx+6},{ay1-1} {mx},{ay1+9}" fill="{p["arrow"]}"/>')
            # personal-data crossing dot on every boundary
            out.append(f'<circle cx="{mx}" cy="{(ay0+ay1)/2:.1f}" r="5.5" fill="{p["dot"]}" '
                       f'stroke="{p["bg"]}" stroke-width="2"/>')
            if i == 2:  # beside the stack: cited answer (up) and proactive notice (down)
                ly0, ly1 = ay0, ay1
                out.append(f'<path d="M 128 {ly1} V {ly0}" stroke="{p["arrow"]}" stroke-width="1.5" '
                           f'fill="none" stroke-dasharray="5 4"/>'
                           f'<polygon points="122,{ly0+10} 134,{ly0+10} 128,{ly0}" fill="{p["arrow"]}"/>')
                out.append(f'<text x="140" y="{(ly0+ly1)/2+4:.1f}" font-family="Menlo,Consolas,monospace" '
                           f'font-size="10.5" fill="{p["sub"]}" text-anchor="start">cited answer</text>')
                out.append(f'<path d="M 772 {ly0} V {ly1}" stroke="{p["arrow"]}" stroke-width="1.5" '
                           f'fill="none" stroke-dasharray="5 4"/>'
                           f'<polygon points="766,{ly1-1} 778,{ly1-1} 772,{ly1+9}" fill="{p["arrow"]}"/>')
                out.append(f'<text x="760" y="{(ly0+ly1)/2+4:.1f}" font-family="Menlo,Consolas,monospace" '
                           f'font-size="10.5" fill="{p["sub"]}" text-anchor="end">proactive notice</text>')
            if i == 5:  # arrow into people carries handoff cards
                out.append(f'<text x="{mx+12}" y="{(ay0+ay1)/2+4:.1f}" font-family="Menlo,Consolas,monospace" '
                           f'font-size="10.5" fill="{p["sub"]}" text-anchor="start">handoff card</text>')

        is_guard = "GUARDRAIL" in title
        fill = p["guard"] if is_guard else p["zone"]
        stroke = p["guard_ln"] if is_guard else p["line"]
        out.append(f'<rect x="{ZX}" y="{y}" width="{ZW}" height="{h}" rx="10" '
                   f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        out.append(f'<rect x="{ZX+16}" y="{y+10}" width="24" height="22" rx="5" fill="{p["num"]}"/>')
        out.append(f'<text x="{ZX+28}" y="{y+25.5}" font-family="Helvetica,Arial,sans-serif" font-size="12" '
                   f'font-weight="700" fill="{p["bg"]}" text-anchor="middle">{num}</text>')
        out.append(f'<text x="{ZX+50}" y="{y+25.5}" font-family="Helvetica,Arial,sans-serif" font-size="15.5" '
                   f'font-weight="700" fill="{p["ink"]}" text-anchor="start">{title}</text>')
        out.append(f'<text x="{ZX+50}" y="{y+42}" font-family="Menlo,Consolas,monospace" font-size="10.5" '
                   f'fill="{p["sub"]}" text-anchor="start">{esc(sub)}</text>')

        cx, cy = ZX + 16, y + 58
        for text, kind in chips:
            w = chip_w(text)
            if cx + w > ZX + ZW - 12:
                cx, cy = ZX + 16, cy + 27
            if is_guard:
                f, ln, tx = p["bg"], p["guard_ln"], p["chip_tx"]
            elif kind == "a":
                f, ln, tx = p["ai"], p["ai_ln"], p["ai_tx"]
            elif kind == "g":
                f, ln, tx = p["chip"], p["chip_ln"], p["chip_tx"]
            else:
                f, ln, tx = p["bg"], stroke, p["sub"]
            out.append(f'<rect x="{cx}" y="{cy}" width="{w:.1f}" height="21" rx="4" fill="{f}" '
                       f'stroke="{ln}" stroke-width="1"/>')
            out.append(f'<text x="{cx+7}" y="{cy+14.5}" font-family="Menlo,Consolas,monospace" '
                       f'font-size="11" fill="{tx}" text-anchor="start">{esc(text)}</text>')
            cx += w + 8

        out.append(f'<text x="{ZX+16}" y="{y+h-14}" font-family="Helvetica,Arial,sans-serif" '
                   f'font-size="12.5" fill="{p["body"]}" text-anchor="start">{esc(body)}</text>')
        y += h + GAP

    out.append(f'<text x="{W/2}" y="{y - GAP + 34}" font-family="Helvetica,Arial,sans-serif" '
               f'font-size="11.5" fill="{p["sub"]}" text-anchor="middle">● dot = personal data crossing '
               f'a zone boundary (PDPL: consent-gated · in-region · audited)</text>')
    out.append('</svg>')
    return "\n".join(out)


for name, pal in (("zone-architecture.svg", LIGHT), ("zone-architecture-dark.svg", DARK)):
    (OUT / name).write_text(build(pal), encoding="utf-8")
    print("wrote", OUT / name, f"({TOTAL_H}px tall)")

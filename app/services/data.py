"""Data layer — loads the challenge data pack (or the synthetic fallback).

The official pack is dropped into `data/pack/`; if it is absent (or a file is
missing) we fall back to `data/synthetic/`, which mirrors the same documented
schema: journey_maps.md, journey_events.csv, service_requests.csv,
pulse_feedback.csv, employees.csv and policies/{en,ar}/*.md.

Column names are mapped through aliases so a differently-named official pack
still loads without code changes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from app.config import get_settings
from app.schemas.common import Journey, Owner

# ---------------------------------------------------------------------------
# column aliases — first match wins
# ---------------------------------------------------------------------------
_ALIASES: dict[str, list[str]] = {
    "employee_id": ["employee_id", "emp_id", "employee", "worker_id"],
    "event": ["event", "event_name", "milestone", "task"],
    "completed_day": ["completed_day", "day", "occurred_day", "event_day"],
    "day": ["day", "pulse_day", "feedback_day"],
    "request_id": ["request_id", "req_id", "ticket_id"],
    "type": ["type", "request_type", "category"],
    "created_day": ["created_day", "opened_day", "raised_day"],
    "sla_days": ["sla_days", "sla", "target_days"],
    "status": ["status", "state"],
    "owner": ["owner", "assigned_to", "service_owner"],
    "score": ["score", "pulse_score", "rating", "sentiment"],
    "consent": ["consent", "consented", "opt_in"],
    "name": ["name", "full_name", "employee_name"],
    "role": ["role", "job_title", "position"],
    "department": ["department", "team", "unit"],
    "journey": ["journey", "track"],
    "start_day": ["start_day", "join_day", "day_zero"],
    "mobility_start_day": ["mobility_start_day", "transfer_day", "move_day"],
    "lang_pref": ["lang_pref", "language", "preferred_lang"],
}


def _pick(df: pd.DataFrame, canonical: str) -> str | None:
    for name in _ALIASES[canonical]:
        if name in df.columns:
            return name
    return None


def _normalize(df: pd.DataFrame, mapping: list[str]) -> pd.DataFrame:
    out = df.rename(columns={})
    for canonical in mapping:
        src = _pick(df, canonical)
        if src is not None:
            out[canonical] = df[src]
    return out


# ---------------------------------------------------------------------------
# journey map (markdown table -> targets)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class MapRow:
    journey: Journey
    stage: str
    event: str
    target_day: int
    owner: Owner


def _clean(cell: str) -> str:
    return str(cell).strip().strip("*_").strip()


def parse_journey_maps(md_text: str) -> dict[str, MapRow]:
    """Parse the first markdown table that has an event + target-day column."""
    lines = md_text.splitlines()
    header_idx, header = None, []
    for i, line in enumerate(lines):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and i + 1 < len(lines) and set(lines[i + 1].replace("|", "").strip()) <= {"-", ":", " "}:
            lowered = [c.lower() for c in cells]
            if any("event" in c or "milestone" in c for c in lowered) and any(
                "target" in c or "day" in c for c in lowered
            ):
                header_idx, header = i, cells
                break
    if header_idx is None:
        raise ValueError("journey_maps: no parsable markdown table found")

    lowered = [c.lower() for c in header]

    def col(*needles: str) -> int:
        for n, c in enumerate(lowered):
            if all(t in c for t in needles):
                return n
        raise ValueError(f"journey_maps: column matching {needles} not found")

    j_col = next((n for n, c in enumerate(lowered) if "journey" in c or "track" in c), 0)
    s_col = next((n for n, c in enumerate(lowered) if "stage" in c or "phase" in c), 1)
    e_col = col("event") if any("event" in c for c in lowered) else col("milestone")
    t_col = col("target", "day") if any("target" in c for c in lowered) else col("day")
    o_col = next((n for n, c in enumerate(lowered) if "owner" in c or "responsible" in c), None)

    rows: dict[str, MapRow] = {}
    for line in lines[header_idx + 2:]:
        if not line.strip().startswith("|"):
            break
        cells = [_clean(c) for c in line.strip().strip("|").split("|")]
        if len(cells) <= max(e_col, t_col) or not cells[e_col]:
            continue
        try:
            target = int(float(_clean(cells[t_col]).replace("day", "").strip()))
        except ValueError:
            continue
        journey = Journey.ONBOARDING if "onboard" in cells[j_col].lower() else Journey.MOBILITY
        owner_text = cells[o_col] if o_col is not None and o_col < len(cells) else "HR Service Desk"
        rows[cells[e_col]] = MapRow(
            journey=journey,
            stage=cells[s_col] if s_col < len(cells) else "General",
            event=cells[e_col],
            target_day=target,
            owner=Owner(name=owner_text, role=owner_text),
        )
    return rows


# ---------------------------------------------------------------------------
# policy corpus
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PolicyChunk:
    policy_id: str
    title: str
    section: str
    text: str
    lang: str
    version: str = "2026.1"

    @property
    def citation_text(self) -> str:
        return f"{self.policy_id} · {self.title}" + (f" · {self.section}" if self.section else "")


def _parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    meta: dict[str, str] = {}
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            for line in parts[1].splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            text = parts[2].lstrip("\n")
    return meta, text


def load_policy_corpus(policies_dir: Path) -> list[PolicyChunk]:
    chunks: list[PolicyChunk] = []
    for lang_dir in sorted(policies_dir.iterdir()) if policies_dir.exists() else []:
        if not lang_dir.is_dir():
            continue
        lang = lang_dir.name
        for path in sorted(lang_dir.glob("*.md")):
            meta, body = _parse_front_matter(path.read_text(encoding="utf-8"))
            pid = meta.get("policy_id", path.stem.upper())
            title = meta.get("title", path.stem.replace("-", " ").title())
            sections: list[tuple[str, list[str]]] = [("Overview", [])]
            for line in body.splitlines():
                if line.startswith("## "):
                    sections.append((line[3:].strip(), []))
                elif line.startswith("# "):
                    continue  # h1 repeats the front-matter title — not content
                else:
                    sections[-1][1].append(line)
            for section, lines in sections:
                text = "\n".join(lines).strip()
                if not text:
                    continue
                chunks.append(PolicyChunk(policy_id=pid, title=title, section=section, text=text, lang=lang))
    return chunks


# ---------------------------------------------------------------------------
# the store
# ---------------------------------------------------------------------------
@dataclass
class DataStore:
    root: Path
    events: pd.DataFrame = field(default_factory=pd.DataFrame)
    requests: pd.DataFrame = field(default_factory=pd.DataFrame)
    pulse: pd.DataFrame = field(default_factory=pd.DataFrame)
    employees: pd.DataFrame = field(default_factory=pd.DataFrame)
    map_rows: dict[str, MapRow] = field(default_factory=dict)
    policy_chunks: list[PolicyChunk] = field(default_factory=list)
    source: str = "synthetic"

    # -- convenience accessors -------------------------------------------------
    def employee(self, employee_id: str) -> dict | None:
        row = self.employees[self.employees["employee_id"] == employee_id]
        return row.iloc[0].to_dict() if not row.empty else None

    def events_for(self, employee_id: str) -> pd.DataFrame:
        df = self.events
        return df[df["employee_id"] == employee_id]

    def requests_for(self, employee_id: str) -> pd.DataFrame:
        df = self.requests
        return df[df["employee_id"] == employee_id]

    def pulse_for(self, employee_id: str) -> pd.DataFrame:
        df = self.pulse
        return df[df["employee_id"] == employee_id]

    def journey_day(self, employee_id: str) -> int:
        """Day number within the employee's current journey (sim-day anchored)."""
        emp = self.employee(employee_id)
        if emp is None:
            return 0
        if str(emp.get("journey", "onboarding")) == Journey.MOBILITY.value:
            anchor = emp.get("mobility_start_day")
            anchor = 0 if pd.isna(anchor) else int(anchor)
        else:
            anchor = int(emp.get("start_day", 0) or 0)
        return int(get_settings().sim_day) - anchor


def _load_csv(directory: Path, filename: str, columns: list[str]) -> pd.DataFrame:
    path = next(
        (directory / f for f in (filename, filename.replace(".csv", ".xlsx")) if (directory / f).exists()),
        None,
    )
    if path is None:
        return pd.DataFrame(columns=columns)
    df = pd.read_excel(path) if path.suffix == ".xlsx" else pd.read_csv(path)
    return _normalize(df, columns)


def load_store(data_dir: Path | None = None) -> DataStore:
    settings = get_settings()
    root = data_dir or (settings.pack_dir if settings.pack_dir.exists() and any(settings.pack_dir.iterdir()) else settings.synthetic_dir)
    root = Path(root)

    events = _load_csv(root, "journey_events.csv",
                       ["employee_id", "event", "completed_day"])
    requests = _load_csv(root, "service_requests.csv",
                         ["request_id", "employee_id", "type", "created_day", "sla_days", "status", "owner"])
    pulse = _load_csv(root, "pulse_feedback.csv",
                      ["employee_id", "day", "score", "consent"])
    employees = _load_csv(root, "employees.csv",
                          ["employee_id", "name", "role", "department", "journey",
                           "start_day", "mobility_start_day", "lang_pref"])

    map_rows: dict[str, MapRow] = {}
    maps_path = root / "journey_maps.md"
    if maps_path.exists():
        try:
            map_rows = parse_journey_maps(maps_path.read_text(encoding="utf-8"))
        except ValueError:
            map_rows = {}
    if not map_rows:  # last-resort CSV variant
        csv_maps = root / "journey_maps.csv"
        if csv_maps.exists():
            mdf = _normalize(pd.read_csv(csv_maps), ["event"])
            for _, r in mdf.iterrows():
                owner = Owner(name=str(r.get("owner", "HR Service Desk")), role=str(r.get("owner", "HR Service Desk")))
                map_rows[str(r["event"])] = MapRow(
                    journey=Journey.ONBOARDING if "onboard" in str(r.get("journey", "")).lower() else Journey.MOBILITY,
                    stage=str(r.get("stage", "General")), event=str(r["event"]),
                    target_day=int(r.get("target_day", r.get("day", 0))), owner=owner,
                )

    chunks = load_policy_corpus(root / "policies")

    store = DataStore(root=root, events=events, requests=requests, pulse=pulse,
                      employees=employees, map_rows=map_rows, policy_chunks=chunks,
                      source="pack" if "pack" in str(root) else "synthetic")
    if not events.empty:
        events["completed_day"] = pd.to_numeric(events["completed_day"], errors="coerce")
    return store

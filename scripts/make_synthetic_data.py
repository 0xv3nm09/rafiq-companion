"""Generate the synthetic data pack (data/synthetic/) mirroring the challenge schema.

Files produced: employees.csv, journey_events.csv, service_requests.csv,
pulse_feedback.csv, journey_maps.md, policies/en/*.md, policies/ar/*.md.

Two demo stars are deterministic:
  E0421  onboarding day 5, laptop_issued overdue (the "day-5 laptop" scenario)
  E0422  mobility day 18, receiving-team sign-off stalled (the "stalled transfer" scenario)
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from policy_texts import POLICIES          # noqa: E402
from policy_texts_ar import POLICIES_AR    # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "synthetic"

# (journey, stage, event, target_day, owner)
JOURNEY_MAP = [
    ("onboarding", "Offer & Pre-boarding", "offer_accepted", 0, "Talent Acquisition"),
    ("onboarding", "Offer & Pre-boarding", "documents_submitted", 2, "HR Onboarding"),
    ("onboarding", "Offer & Pre-boarding", "photo_shared", 2, "HR Onboarding"),
    ("onboarding", "Day One", "badge_building_access", 1, "Facilities"),
    ("onboarding", "IT Setup", "it_account_created", 2, "IT Service Desk"),
    ("onboarding", "IT Setup", "laptop_issued", 3, "IT Service Desk"),
    ("onboarding", "First Week", "first_manager_1on1", 5, "Line Manager"),
    ("onboarding", "First Week", "induction_training_booked", 7, "Learning & Development"),
    ("onboarding", "Payroll & Benefits", "bank_wps_setup", 10, "Payroll"),
    ("onboarding", "Payroll & Benefits", "health_insurance_enrolled", 14, "HR Benefits"),
    ("onboarding", "Visa & Relocation", "visa_entry_permit", 10, "Visa & Immigration"),
    ("onboarding", "Visa & Relocation", "medical_fitness_test", 15, "Visa & Immigration"),
    ("onboarding", "Visa & Relocation", "emirates_id_application", 20, "Visa & Immigration"),
    ("onboarding", "Visa & Relocation", "residence_visa_stamped", 25, "Visa & Immigration"),
    ("onboarding", "Probation", "probation_review_30", 30, "Line Manager"),
    ("mobility", "Transfer Approval", "transfer_request_approved", 10, "HR Mobility"),
    ("mobility", "Transfer Approval", "receiving_team_signoff", 15, "Receiving Manager"),
    ("mobility", "Handover", "release_from_current_team", 20, "Current Manager"),
    ("mobility", "IT Setup", "access_reprovisioned", 22, "IT Service Desk"),
    ("mobility", "Relocation", "new_location_ready", 25, "Facilities"),
    ("mobility", "Landing", "first_1on1_new_team", 30, "New Line Manager"),
]

ONBOARDING_EVENTS = [r[2] for r in JOURNEY_MAP if r[0] == "onboarding"]
VISA_EVENTS = ["visa_entry_permit", "medical_fitness_test", "emirates_id_application", "residence_visa_stamped"]
MOBILITY_EVENTS = [r[2] for r in JOURNEY_MAP if r[0] == "mobility"]

TARGETS = {r[2]: r[3] for r in JOURNEY_MAP}

ROLES_DEPTS = [
    ("Cabin Crew", "Flight Operations"), ("Airport Services Agent", "Airport Services"),
    ("Aircraft Engineer", "Engineering"), ("Finance Analyst", "Finance"),
    ("IT Support Specialist", "IT"), ("HR Officer", "People & Culture"),
    ("Marketing Specialist", "Marketing"), ("Ground Operations Officer", "Ground Handling"),
    ("Cargo Agent", "Cargo"), ("Data Analyst", "Commercial"),
    ("Procurement Officer", "Supply Chain"), ("Training Coordinator", "Learning & Development"),
]

FIRST = ["Aisha", "Omar", "Fatima", "Khalid", "Mariam", "Yousef", "Sara", "Hamdan", "Noor", "Rashid",
         "Layla", "Tariq", "Zainab", "Faisal", "Hind", "Saeed", "Dana", "Abdullah", "Salma", "Majid",
         "Priya", "Rahul", "Arjun", "Meera", "Vikram", "Ananya",
         "Maria", "James", "Elena", "Marco", "Sofia", "Lucas", "Anna", "David", "Nina", "Peter",
         "Grace", "Samuel", "Chloe", "Daniel"]
LAST = ["Al Mansoori", "Haddad", "Al Suwaidi", "Al Marzouqi", "Khan", "Sharma", "Patel", "Nair",
        "Fernandez", "Rossi", "Kowalski", "Smith", "Johnson", "Brown", "Garcia", "Mueller",
        "Dubois", "Silva", "Anderson", "Okafor", "Hassan", "Ali", "Rahman", "Chowdhury", "Ibrahim",
        "Al Balushi", "Al Zaabi", "Kaur", "Tan", "Lim"]

REQUEST_TYPES = ["laptop_issue", "access_request", "visa_query", "payroll_query", "transfer_approval",
                 "insurance_query", "leave_query", "it_ticket", "relocation_support", "medical_booking"]

E0421 = dict(employee_id="E0421", name="Aisha Al Mansoori", role="Finance Analyst", department="Finance",
             journey="onboarding", start_day=0, mobility_start_day="", lang_pref="en", emirati=True)
E0422 = dict(employee_id="E0422", name="Omar Haddad", role="IT Support Specialist", department="IT",
             journey="mobility", start_day=-420, mobility_start_day=-13, lang_pref="en", emirati=False)


def make_employees(n: int, sim_day: int, rng: random.Random) -> list[dict]:
    people = [dict(E0421), dict(E0422)]
    seen = {"E0421", "E0422"}
    while len(people) < n:
        eid = f"E{rng.randint(1, 9999):04d}"
        if eid in seen:
            continue
        seen.add(eid)
        role, dept = rng.choice(ROLES_DEPTS)
        emirati = rng.random() < 0.18
        if rng.random() < 0.4:  # mobility cohort
            md = rng.randint(-5, 40)                    # mobility day now
            people.append(dict(employee_id=eid, name=f"{rng.choice(FIRST)} {rng.choice(LAST)}",
                               role=role, department=dept, journey="mobility",
                               start_day=rng.randint(-800, -200), mobility_start_day=sim_day - md,
                               lang_pref=rng.choice(["en", "en", "ar"]), emirati=emirati))
        else:
            jd = rng.choice([rng.randint(-20, -1), rng.randint(0, 35)])
            people.append(dict(employee_id=eid, name=f"{rng.choice(FIRST)} {rng.choice(LAST)}",
                               role=role, department=dept, journey="onboarding",
                               start_day=sim_day - jd, mobility_start_day="",
                               lang_pref=rng.choice(["en", "en", "ar"]), emirati=emirati))
    return people


def journey_day(person: dict, sim_day: int) -> int:
    anchor = person["mobility_start_day"] if person["journey"] == "mobility" else person["start_day"]
    return sim_day - int(anchor)


def make_events(people: list[dict], rng: random.Random) -> list[dict]:
    rows: list[dict] = []

    def rec(emp_id: str, event: str, day, status: str = "done") -> None:
        rows.append(dict(employee_id=emp_id, event=event, completed_day=day, status=status))

    for p in people:
        eid = p["employee_id"]
        jd = journey_day(p, 5)
        if eid == "E0421":
            for e, d in [("offer_accepted", 0), ("documents_submitted", 1), ("photo_shared", 1),
                         ("badge_building_access", 1), ("it_account_created", 2), ("first_manager_1on1", 4)]:
                rec(eid, e, d)
            continue
        if eid == "E0422":
            rec(eid, "transfer_request_approved", 8)
            continue
        if p["journey"] == "onboarding":
            if jd < 0:  # pre-boarding: papers + photo happen before joining
                if jd <= -10 and rng.random() < 0.8:
                    rec(eid, "offer_accepted", 0)
                    rec(eid, "documents_submitted", 0)
                    rec(eid, "photo_shared", 0)
                continue
            entry_day: int | None = None
            medical_day: int | None = None
            for e in ONBOARDING_EVENTS:
                if e in VISA_EVENTS and p["emirati"]:
                    if TARGETS[e] <= jd:
                        rec(eid, e, "", "na")
                    continue
                if e == "medical_fitness_test" and entry_day is not None and rng.random() < 0.75:
                    # expat reality: the medical is done at the visa window, well ahead of target
                    actual = entry_day + rng.randint(1, 4)
                    if actual <= jd:
                        rec(eid, e, actual)
                        medical_day = actual
                        continue
                if e == "emirates_id_application" and medical_day is not None and rng.random() < 0.8:
                    # Emirates ID biometrics usually happen at the same visit as the medical
                    actual = medical_day + rng.randint(0, 1)
                    if actual <= jd:
                        rec(eid, e, actual)
                        continue
                if TARGETS[e] <= jd and rng.random() < 0.92:
                    actual = max(0, TARGETS[e] + rng.randint(-1, 2))
                    if actual <= jd:
                        rec(eid, e, actual)
                        if e == "visa_entry_permit":
                            entry_day = actual
                        if e == "medical_fitness_test":
                            medical_day = actual
        else:  # mobility
            if jd < 0:
                continue
            for e in MOBILITY_EVENTS:
                if TARGETS[e] <= jd and rng.random() < 0.92:
                    actual = max(0, TARGETS[e] + rng.randint(-1, 2))
                    if actual <= jd:
                        rec(eid, e, actual)
    return rows


def make_requests(people: list[dict], rng: random.Random) -> list[dict]:
    rows: list[dict] = []
    counter = 0

    def add(emp_id: str, rtype: str, created: int, sla: int, status: str, owner: str) -> None:
        nonlocal counter
        counter += 1
        rows.append(dict(request_id=f"REQ-{counter:04d}", employee_id=emp_id, type=rtype,
                         created_day=created, sla_days=sla, status=status, owner=owner))

    add("E0421", "laptop_issue", 2, 2, "open", "IT Service Desk")
    add("E0422", "transfer_approval", 12, 5, "open", "Receiving Manager")
    for p in people:
        if p["employee_id"] in ("E0421", "E0422") or rng.random() > 0.12:
            continue
        jd = journey_day(p, 5)
        if jd <= 0:
            continue
        rtype = rng.choice(REQUEST_TYPES)
        created = rng.randint(0, max(1, jd - 1))
        status = "resolved" if rng.random() < 0.6 else "open"
        add(p["employee_id"], rtype, created, rng.choice([2, 3, 5]), status, rng.choice(
            ["IT Service Desk", "HR Onboarding", "Payroll", "Facilities", "HR Mobility", "HR Benefits"]))
    return rows


def make_pulse(people: list[dict], rng: random.Random) -> list[dict]:
    rows: list[dict] = [
        dict(employee_id="E0421", day=3, score=4, consent=True),
        dict(employee_id="E0421", day=4, score=2, consent=True),
        dict(employee_id="E0422", day=15, score=3, consent=True),
        dict(employee_id="E0422", day=16, score=2, consent=True),
    ]
    for p in people:
        if p["employee_id"] in ("E0421", "E0422") or rng.random() > 0.55:
            continue
        jd = journey_day(p, 5)
        for _ in range(rng.randint(1, 3)):
            day = rng.randint(0, max(0, jd))
            consent = rng.random() < 0.75
            score = rng.choice([2, 3, 3, 4, 4, 4, 5, 5]) if rng.random() > 0.1 else rng.choice([1, 2])
            rows.append(dict(employee_id=p["employee_id"], day=day, score=score, consent=consent))
    return rows


def write_journey_maps(path: Path) -> None:
    lines = [
        "# Journey maps — event targets and owners",
        "",
        "Deterministic service-level targets per journey event. `target_day` is day-number within",
        "the employee's current journey (onboarding: from start; mobility: from transfer initiation).",
        "",
        "| Journey | Stage | Event | Target Day | Owner |",
        "| --- | --- | --- | --- | --- |",
    ]
    for journey, stage, event, target, owner in JOURNEY_MAP:
        lines.append(f"| {journey} | {stage} | {event} | {target} | {owner} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_policies(policies_dir: Path) -> None:
    def slug(s: str) -> str:
        return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-")

    for lang, source in (("en", POLICIES), ("ar", POLICIES_AR)):
        d = policies_dir / lang
        d.mkdir(parents=True, exist_ok=True)
        for pid, doc in source.items():
            title = doc.get("title", doc.get("title_ar", pid))
            sections = doc["sections"]
            fm = f"---\npolicy_id: {pid}\ntitle: {title}\nversion: 2026.1\n---\n\n"
            body = f"# {title}\n\n"
            for stitle, stext in sections:
                body += f"## {stitle}\n\n{stext}\n\n"
            (d / f"{pid}-{slug(title)}.md").write_text(fm + body, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--employees", type=int, default=200)
    ap.add_argument("--sim-day", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    OUT.mkdir(parents=True, exist_ok=True)

    people = make_employees(args.employees, args.sim_day, rng)
    pd.DataFrame(people).to_csv(OUT / "employees.csv", index=False)
    pd.DataFrame(make_events(people, rng)).to_csv(OUT / "journey_events.csv", index=False)
    pd.DataFrame(make_requests(people, rng)).to_csv(OUT / "service_requests.csv", index=False)
    pd.DataFrame(make_pulse(people, rng)).to_csv(OUT / "pulse_feedback.csv", index=False)
    write_journey_maps(OUT / "journey_maps.md")
    write_policies(OUT / "policies")

    print(f"synthetic pack written to {OUT} "
          f"({len(people)} employees, sim_day={args.sim_day})")


if __name__ == "__main__":
    main()

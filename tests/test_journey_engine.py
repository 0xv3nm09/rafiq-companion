"""Demo scenarios and engine invariants — the two hidden-scenario cases first."""


def test_day5_laptop_scenario(store):
    """E0421: onboarding day 5, laptop not issued (due day 3) -> blocker, IT owner."""
    state = store and __import__("app.core.journey_engine", fromlist=["journey_state"]).journey_state(store, "E0421")
    assert state.day == 5
    assert state.journey.value == "onboarding"
    events = [b.event for b in state.blockers]
    assert events == ["laptop_issued"]
    b = state.blockers[0]
    assert b.days_overdue == 2
    assert b.owner.name == "IT Service Desk"
    assert state.risk == 0.25
    assert state.stage == "IT Setup"


def test_stalled_transfer_scenario(store):
    """E0422: mobility day 18, receiving-team sign-off stalled past day-15 SLA."""
    from app.core.journey_engine import journey_state
    state = journey_state(store, "E0422")
    assert state.day == 18
    assert state.journey.value == "mobility"
    events = [b.event for b in state.blockers]
    assert events == ["receiving_team_signoff"]
    assert state.blockers[0].days_overdue == 3
    assert state.blockers[0].owner.name == "Receiving Manager"


def test_waived_visa_events_produce_no_blockers(store):
    """Local Emirati hires have visa events marked NA -> never flagged."""
    from app.core.journey_engine import journey_state
    flagged = 0
    for _, emp in store.employees.iterrows():
        if emp["journey"] != "onboarding" or not bool(emp.get("emirati", False)):
            continue
        state = journey_state(store, str(emp["employee_id"]))
        assert not any(b.event in ("visa_entry_permit", "medical_fitness_test",
                                   "emirates_id_application", "residence_visa_stamped")
                       for b in state.blockers), emp["employee_id"]
        flagged += 1
    assert flagged > 0  # the generator does create Emirati joiners


def test_timeline_statuses(store):
    from app.core.journey_engine import timeline
    steps = {s.event: s for s in timeline(store, "E0421")}
    assert steps["laptop_issued"].status == "overdue"
    assert steps["offer_accepted"].status == "done" and steps["offer_accepted"].completed_day == 0
    assert steps["health_insurance_enrolled"].status == "upcoming"
    visa = [s for s in steps.values() if s.event == "visa_entry_permit"]
    assert visa and visa[0].status in ("upcoming", "na")


def test_employee_not_found_gives_day_zero(store):
    from app.core.journey_engine import journey_state
    state = journey_state(store, "NOPE")
    assert state.day == 0


def test_early_completion_is_honoured(store):
    """Medical/EID complete early at the visa window -> done, never a blocker."""
    from app.core.journey_engine import timeline
    ev = store.events[store.events["event"] == "medical_fitness_test"].merge(
        store.employees[["employee_id", "journey", "emirati"]], on="employee_id")
    ev = ev[(ev["journey"] == "onboarding") & (ev["emirati"] == False)]  # noqa: E712
    ev["completed_day"] = ev["completed_day"].astype(float)
    early = ev[ev["completed_day"] < 15]
    assert len(early) > 0, "generator should pair some medicals with the visa visit"
    emp = str(early.iloc[0]["employee_id"])
    step = {s.event: s for s in timeline(store, emp)}["medical_fitness_test"]
    assert step.status == "done" and step.completed_day == early.iloc[0]["completed_day"]


def test_upcoming_steps_carry_pair_hint(store):
    from app.core.journey_engine import timeline
    steps = {s.event: s for s in timeline(store, "E0421")}
    note = steps["medical_fitness_test"].note or ""
    assert "early" in note or "visit" in note
    done = {s.event: s for s in timeline(store, "E0421")}["photo_shared"]
    assert done.status == "done"

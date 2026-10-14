from app.core.friction import scan


def test_day5_laptop_full_risk(store):
    """0.25 event + 0.15 past-SLA request + 0.10 consented pulse dip = 0.50."""
    report = scan(store, "E0421", consented=True)
    kinds = {f.kind for f in report.flags}
    assert kinds == {"overdue_event", "overdue_request", "pulse_dip"}
    assert report.risk == 0.5
    assert report.worst and report.worst.owner == "IT Service Desk"


def test_consent_gates_pulse_signal(store):
    report = scan(store, "E0421", consented=False)
    assert "pulse_dip" not in {f.kind for f in report.flags}
    assert report.risk == 0.4


def test_stalled_transfer_full_risk(store):
    report = scan(store, "E0422", consented=True)
    assert report.risk == 0.5
    assert {f.kind for f in report.flags} == {"overdue_event", "overdue_request", "pulse_dip"}


def test_clean_employee_has_no_flags(store):
    """Someone with everything on track produces zero flags."""
    clean = [e for _, e in store.employees.iterrows()
             if scan(store, str(e["employee_id"]), consented=False).risk == 0.0]
    assert clean, "expected at least one fully on-track employee"

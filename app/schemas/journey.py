from pydantic import BaseModel

from app.schemas.common import Journey, Owner


class Blocker(BaseModel):
    event: str
    label: str                      # human-readable, e.g. "Laptop issued"
    due_day: int
    days_overdue: int
    owner: Owner


class JourneyState(BaseModel):
    employee_id: str
    journey: Journey
    stage: str
    day: int
    done: list[str] = []
    upcoming: list[str] = []        # next events still inside their target window
    blockers: list[Blocker] = []
    risk: float = 0.0


class TimelineStep(BaseModel):
    event: str
    label: str
    stage: str
    target_day: int
    status: str                     # done | upcoming | overdue | na
    owner: str
    completed_day: int | None = None
    days_overdue: int | None = None

from pydantic import BaseModel, Field

from app.schemas.common import Owner


class HandoffCard(BaseModel):
    handoff_id: str | None = None   # assigned by HandoffStore.create()
    event_key: str | None = None    # machine key for dedupe (e.g. laptop_issued)
    employee_id: str
    stage: str
    blocker: str
    tried: list[str] = []
    suggested_owner: Owner
    summary: str
    created_day: int
    status: str = "open"            # open | acknowledged | resolved

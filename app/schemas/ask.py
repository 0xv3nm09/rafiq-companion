from pydantic import BaseModel, Field

from app.schemas.common import Citation, Lang


class AskRequest(BaseModel):
    employee_id: str
    message: str
    lang: Lang = Lang.EN
    consent_pulse: bool = False


class LowConfidenceInfo(BaseModel):
    retrieval_score: float
    threshold: float


class AskResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)
    citations: list[Citation] = []
    actions: list[str] = []          # e.g. chase_it_ticket
    escalated: bool = False
    handoff_id: str | None = None
    kind: str = "policy"             # policy | journey | action | handoff
    low_confidence: LowConfidenceInfo | None = None

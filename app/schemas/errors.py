from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error: str                      # machine code, e.g. low_confidence
    message: str
    detail: dict | None = None
    request_id: str = Field(default_factory=lambda: "req_000000")

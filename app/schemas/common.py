from enum import Enum

from pydantic import BaseModel, Field


class Lang(str, Enum):
    EN = "en"
    AR = "ar"


class Journey(str, Enum):
    ONBOARDING = "onboarding"
    MOBILITY = "mobility"


class Owner(BaseModel):
    """A named human/service owner — every escalation carries one."""
    name: str
    role: str


class Citation(BaseModel):
    policy_id: str
    title: str
    section: str | None = None
    lang: str = "en"

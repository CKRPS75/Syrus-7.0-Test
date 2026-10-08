from pydantic import BaseModel, Field
from typing import List


class JourneyRequest(BaseModel):
    origin: str
    destination: str
    departure: str

    deadline: str | None = None

    budget: float | None = None

    max_walking: int | None = None

    accessibility_required: bool = False

    allowed_modes: List[str] = Field(default_factory=list)

    forbidden_modes: List[str] = Field(default_factory=list)

    transfer_tolerance: int | None = None

    risk_tolerance: str = "MEDIUM"
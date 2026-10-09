import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class TravellerBase(BaseModel):
    name: str = Field(..., example="Aarav Sharma")
    budget: float = Field(default=100.0, ge=0.0)
    deadline: Optional[datetime] = None
    max_walking_minutes: int = Field(default=30, ge=0)
    accessibility_required: bool = False
    risk_tolerance: float = Field(default=0.5, ge=0.0, le=1.0)
    allowed_modes: List[str] = Field(default_factory=lambda: ["BUS", "METRO", "WALK"])
    forbidden_modes: List[str] = Field(default_factory=list)
    transfer_tolerance: int = Field(default=3, ge=0)


class TravellerCreate(TravellerBase):
    pass


class TravellerResponse(TravellerBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

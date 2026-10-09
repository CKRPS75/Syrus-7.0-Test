import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class ImpactCheckRequest(BaseModel):
    journey_id: uuid.UUID
    event_id: uuid.UUID


class ImpactResponse(BaseModel):
    id: uuid.UUID
    event_id: uuid.UUID
    journey_id: uuid.UUID
    affects_route: bool
    affected_leg: Dict[str, Any]
    estimated_delay: int = Field(..., description="Estimated delay in minutes")
    route_feasible: bool = Field(..., description="Whether traveller can physically reach destination")
    route_protected: bool = Field(..., description="Whether traveller satisfies deadline and risk constraints under delay")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field


class ItineraryBase(BaseModel):
    total_duration: int = Field(..., description="Duration in minutes", ge=0)
    arrival_time: datetime
    total_fare: float = Field(default=0.0, ge=0.0)
    walking_minutes: int = Field(default=0, ge=0)
    transfers: int = Field(default=0, ge=0)
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    is_current: bool = True
    is_protected: bool = True
    route_data: Dict[str, Any] = Field(default_factory=dict, description="Leg details and coordinates")


class ItineraryCreate(ItineraryBase):
    journey_id: uuid.UUID


class ItineraryResponse(ItineraryBase):
    id: uuid.UUID
    journey_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

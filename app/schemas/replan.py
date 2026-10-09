import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.db.models import ReplanStatusEnum
from app.schemas.itinerary import ItineraryResponse


class ReplanRequest(BaseModel):
    journey_id: uuid.UUID
    event_id: uuid.UUID


class ReplanProposalResponse(BaseModel):
    id: uuid.UUID
    journey_id: uuid.UUID
    event_id: uuid.UUID
    old_itinerary_id: uuid.UUID
    new_itinerary_id: uuid.UUID
    reason: str
    time_saved: int = Field(..., description="Minutes saved compared to delayed original route")
    status: ReplanStatusEnum
    created_at: datetime
    expires_at: Optional[datetime] = None
    new_itinerary: Optional[ItineraryResponse] = None

    model_config = ConfigDict(from_attributes=True)

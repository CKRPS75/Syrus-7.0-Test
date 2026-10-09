import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.db.models import DecisionEnum, ReplanStatusEnum


class ConfirmRequest(BaseModel):
    proposal_id: uuid.UUID
    decision: DecisionEnum


class ConfirmResponse(BaseModel):
    id: uuid.UUID
    proposal_id: uuid.UUID
    journey_id: uuid.UUID
    decision: DecisionEnum
    confirmed_at: datetime
    proposal_status: ReplanStatusEnum
    current_itinerary_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)

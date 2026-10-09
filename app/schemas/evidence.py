import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from app.db.models import ValidationStatusEnum


class EvidenceProcessRequest(BaseModel):
    source_type: str = Field(..., example="CROWD")
    source_name: str = Field(..., example="Twitter / X Mumbai Traffic")
    source_url: Optional[str] = None
    raw_text: str = Field(..., example="Dadar metro station entrance flooded due to heavy rains. Trains delayed by 20 mins.")
    published_at: Optional[datetime] = None
    latitude: Optional[float] = Field(default=None, example=19.0178)
    longitude: Optional[float] = Field(default=None, example=72.8478)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EvidenceResponse(BaseModel):
    id: uuid.UUID
    event_id: uuid.UUID
    report_id: uuid.UUID
    source_type: str
    source_name: str
    location_match: float
    time_match: float
    evidence_weight: float
    freshness_score: float
    independence_group: str
    validation_status: ValidationStatusEnum
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvidenceProcessResponse(BaseModel):
    report_id: uuid.UUID
    event_id: uuid.UUID
    evidence_id: uuid.UUID
    trust_status: str
    confidence_score: float
    message: str

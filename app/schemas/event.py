import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.db.models import TrustStatusEnum
from app.schemas.evidence import EvidenceResponse


class EventResponse(BaseModel):
    id: uuid.UUID
    event_type: str
    status: str
    trust_status: TrustStatusEnum
    title: str
    description: Optional[str] = None
    affected_line: Optional[str] = None
    affected_stop: Optional[str] = None
    affected_route: Optional[str] = None
    severity: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    valid_from: datetime
    valid_to: Optional[datetime] = None
    confidence_score: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventDetailResponse(EventResponse):
    evidence_records: List[EvidenceResponse] = Field(default_factory=list)

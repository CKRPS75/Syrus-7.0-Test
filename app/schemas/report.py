import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class ReportCreate(BaseModel):
    source_type: str = Field(..., example="CROWD")
    source_name: str = Field(..., example="Mumbai Commuter Network")
    source_url: Optional[str] = None
    raw_text: str = Field(..., example="Heavy waterlogging reported near Hindmata Flyover, Dadar Bus services disrupted.")
    published_at: Optional[datetime] = None
    latitude: Optional[float] = Field(default=None, example=19.0178)
    longitude: Optional[float] = Field(default=None, example=72.8478)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ReportResponse(ReportCreate):
    id: uuid.UUID
    retrieved_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

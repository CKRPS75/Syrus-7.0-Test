import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class DataSourceResponse(BaseModel):
    id: uuid.UUID
    source_type: str
    source_name: str
    source_url: Optional[str] = None
    version: Optional[str] = None
    checksum: Optional[str] = None
    retrieved_at: datetime
    validation_status: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)

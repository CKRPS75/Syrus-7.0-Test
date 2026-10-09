from pydantic import BaseModel
from datetime import datetime


class CrowdReport(BaseModel):
    report_id: str
    location: str
    affected_line: str | None = None
    affected_stop: str | None = None
    disruption_type: str
    severity: str
    reported_at: datetime
    source: str
    confidence: float = 0.0
import uuid
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.db.models import EventModel, ReportModel, EvidenceModel
from app.db.repositories.event_repo import EventRepository
from app.db.repositories.report_repo import ReportRepository
from app.db.repositories.evidence_repo import EvidenceRepository
from app.services.evidence.base import BaseEvidenceProcessor
from app.schemas.evidence import EvidenceProcessRequest, EvidenceProcessResponse


class EventService:
    def __init__(self, db: Session, evidence_processor: BaseEvidenceProcessor):
        self.db = db
        self.event_repo = EventRepository(db)
        self.report_repo = ReportRepository(db)
        self.evidence_repo = EvidenceRepository(db)
        self.processor = evidence_processor

    def process_evidence(self, req: EvidenceProcessRequest) -> EvidenceProcessResponse:
        # 1. Parse report via processor
        event_dict, evidence_dict, report_dict = self.processor.process_report(req.model_dump())

        # 2. Save Report
        report = ReportModel(
            id=uuid.uuid4(),
            **report_dict
        )
        self.report_repo.create(report)

        # 3. Save Event
        event = EventModel(
            id=uuid.uuid4(),
            **event_dict
        )
        self.event_repo.create(event)

        # 4. Save Evidence record
        evidence = EvidenceModel(
            id=uuid.uuid4(),
            event_id=event.id,
            report_id=report.id,
            **evidence_dict
        )
        self.evidence_repo.create(evidence)

        return EvidenceProcessResponse(
            report_id=report.id,
            event_id=event.id,
            evidence_id=evidence.id,
            trust_status=event.trust_status.value if hasattr(event.trust_status, 'value') else str(event.trust_status),
            confidence_score=event.confidence_score,
            message="Evidence processed and grounded successfully."
        )

    def get_event(self, event_id: uuid.UUID) -> Optional[EventModel]:
        return self.event_repo.get_by_id(event_id)

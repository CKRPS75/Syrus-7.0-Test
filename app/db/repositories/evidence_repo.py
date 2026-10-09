import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.models import EvidenceModel


class EvidenceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, evidence_id: uuid.UUID) -> Optional[EvidenceModel]:
        return self.db.query(EvidenceModel).filter(EvidenceModel.id == evidence_id).first()

    def get_by_event_id(self, event_id: uuid.UUID) -> List[EvidenceModel]:
        return self.db.query(EvidenceModel).filter(EvidenceModel.event_id == event_id).all()

    def create(self, evidence: EvidenceModel) -> EvidenceModel:
        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)
        return evidence

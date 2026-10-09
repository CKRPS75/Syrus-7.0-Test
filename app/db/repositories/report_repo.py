import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.db.models import ReportModel


class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, report_id: uuid.UUID) -> Optional[ReportModel]:
        return self.db.query(ReportModel).filter(ReportModel.id == report_id).first()

    def create(self, report: ReportModel) -> ReportModel:
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

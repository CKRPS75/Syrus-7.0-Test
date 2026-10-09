import uuid
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.db.models import EventModel


class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, event_id: uuid.UUID) -> Optional[EventModel]:
        return (
            self.db.query(EventModel)
            .options(joinedload(EventModel.evidence_records))
            .filter(EventModel.id == event_id)
            .first()
        )

    def create(self, event: EventModel) -> EventModel:
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def list_active(self) -> List[EventModel]:
        return self.db.query(EventModel).filter(EventModel.status == "ACTIVE").all()

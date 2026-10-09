import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.models import RouteImpactModel


class ImpactRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, impact_id: uuid.UUID) -> Optional[RouteImpactModel]:
        return self.db.query(RouteImpactModel).filter(RouteImpactModel.id == impact_id).first()

    def get_by_journey_and_event(self, journey_id: uuid.UUID, event_id: uuid.UUID) -> Optional[RouteImpactModel]:
        return (
            self.db.query(RouteImpactModel)
            .filter(RouteImpactModel.journey_id == journey_id, RouteImpactModel.event_id == event_id)
            .first()
        )

    def create(self, impact: RouteImpactModel) -> RouteImpactModel:
        self.db.add(impact)
        self.db.commit()
        self.db.refresh(impact)
        return impact

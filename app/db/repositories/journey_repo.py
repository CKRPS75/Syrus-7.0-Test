import uuid
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.db.models import JourneyModel


class JourneyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, journey_id: uuid.UUID) -> Optional[JourneyModel]:
        return (
            self.db.query(JourneyModel)
            .options(
                joinedload(JourneyModel.traveller),
                joinedload(JourneyModel.itineraries),
                joinedload(JourneyModel.route_impacts),
                joinedload(JourneyModel.replan_proposals),
            )
            .filter(JourneyModel.id == journey_id)
            .first()
        )

    def create(self, journey: JourneyModel) -> JourneyModel:
        self.db.add(journey)
        self.db.commit()
        self.db.refresh(journey)
        return journey

    def update_current_itinerary(self, journey_id: uuid.UUID, itinerary_id: uuid.UUID) -> Optional[JourneyModel]:
        journey = self.db.query(JourneyModel).filter(JourneyModel.id == journey_id).first()
        if journey:
            journey.current_itinerary_id = itinerary_id
            self.db.commit()
            self.db.refresh(journey)
        return journey

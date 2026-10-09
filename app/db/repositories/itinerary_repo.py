import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.models import ItineraryModel


class ItineraryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, itinerary_id: uuid.UUID) -> Optional[ItineraryModel]:
        return self.db.query(ItineraryModel).filter(ItineraryModel.id == itinerary_id).first()

    def create(self, itinerary: ItineraryModel) -> ItineraryModel:
        self.db.add(itinerary)
        self.db.commit()
        self.db.refresh(itinerary)
        return itinerary

    def set_current(self, journey_id: uuid.UUID, itinerary_id: uuid.UUID) -> None:
        # Mark all itineraries for journey as not current, then mark specified as current
        self.db.query(ItineraryModel).filter(ItineraryModel.journey_id == journey_id).update({"is_current": False})
        self.db.query(ItineraryModel).filter(ItineraryModel.id == itinerary_id).update({"is_current": True})
        self.db.commit()

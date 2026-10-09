import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.db.models import TravellerModel


class TravellerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, traveller_id: uuid.UUID) -> Optional[TravellerModel]:
        return self.db.query(TravellerModel).filter(TravellerModel.id == traveller_id).first()

    def create(self, traveller: TravellerModel) -> TravellerModel:
        self.db.add(traveller)
        self.db.commit()
        self.db.refresh(traveller)
        return traveller

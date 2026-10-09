import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.db.models import ConfirmationModel


class ConfirmationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, confirmation_id: uuid.UUID) -> Optional[ConfirmationModel]:
        return self.db.query(ConfirmationModel).filter(ConfirmationModel.id == confirmation_id).first()

    def create(self, confirmation: ConfirmationModel) -> ConfirmationModel:
        self.db.add(confirmation)
        self.db.commit()
        self.db.refresh(confirmation)
        return confirmation

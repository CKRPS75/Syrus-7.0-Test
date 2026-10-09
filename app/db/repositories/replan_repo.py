import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.models import ReplanProposalModel, ReplanStatusEnum


class ReplanRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, proposal_id: uuid.UUID) -> Optional[ReplanProposalModel]:
        return self.db.query(ReplanProposalModel).filter(ReplanProposalModel.id == proposal_id).first()

    def create(self, proposal: ReplanProposalModel) -> ReplanProposalModel:
        self.db.add(proposal)
        self.db.commit()
        self.db.refresh(proposal)
        return proposal

    def update_status(self, proposal_id: uuid.UUID, status: ReplanStatusEnum) -> Optional[ReplanProposalModel]:
        proposal = self.get_by_id(proposal_id)
        if proposal:
            proposal.status = status
            self.db.commit()
            self.db.refresh(proposal)
        return proposal

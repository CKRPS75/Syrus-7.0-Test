import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.db.models import ConfirmationModel, ReplanStatusEnum, DecisionEnum
from app.db.repositories.replan_repo import ReplanRepository
from app.db.repositories.confirmation_repo import ConfirmationRepository
from app.db.repositories.itinerary_repo import ItineraryRepository
from app.db.repositories.journey_repo import JourneyRepository
from app.schemas.confirm import ConfirmRequest, ConfirmResponse


class ConfirmationService:
    """Handles user decisions (ACCEPT/REJECT) on replan proposals."""

    def __init__(self, db: Session):
        self.db = db
        self.replan_repo = ReplanRepository(db)
        self.confirmation_repo = ConfirmationRepository(db)
        self.itinerary_repo = ItineraryRepository(db)
        self.journey_repo = JourneyRepository(db)

    def process_confirmation(self, req: ConfirmRequest) -> ConfirmResponse:
        proposal = self.replan_repo.get_by_id(req.proposal_id)
        if not proposal:
            raise ValueError(f"Replan proposal with ID {req.proposal_id} not found.")

        # Validation: proposal must be pending
        if proposal.status != ReplanStatusEnum.PENDING:
            raise ValueError(f"Proposal {req.proposal_id} is not in PENDING state (current status: {proposal.status.value}).")

        # 1. Update proposal status
        new_status = ReplanStatusEnum.ACCEPTED if req.decision == DecisionEnum.ACCEPT else ReplanStatusEnum.REJECTED
        self.replan_repo.update_status(proposal.id, new_status)

        # 2. If ACCEPTED, switch active itinerary on journey
        if req.decision == DecisionEnum.ACCEPT:
            self.itinerary_repo.set_current(proposal.journey_id, proposal.new_itinerary_id)
            self.journey_repo.update_current_itinerary(proposal.journey_id, proposal.new_itinerary_id)

        # 3. Create Confirmation record
        confirmation = ConfirmationModel(
            id=uuid.uuid4(),
            proposal_id=proposal.id,
            journey_id=proposal.journey_id,
            decision=req.decision,
            confirmed_at=datetime.now(timezone.utc)
        )
        self.confirmation_repo.create(confirmation)

        journey = self.journey_repo.get_by_id(proposal.journey_id)
        current_it_id = journey.current_itinerary_id if journey else proposal.new_itinerary_id

        return ConfirmResponse(
            id=confirmation.id,
            proposal_id=proposal.id,
            journey_id=proposal.journey_id,
            decision=req.decision,
            confirmed_at=confirmation.confirmed_at,
            proposal_status=new_status,
            current_itinerary_id=current_it_id
        )

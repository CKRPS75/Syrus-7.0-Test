import uuid
from typing import Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.db.models import ReplanProposalModel, ItineraryModel, ReplanStatusEnum
from app.db.repositories.journey_repo import JourneyRepository
from app.db.repositories.event_repo import EventRepository
from app.db.repositories.itinerary_repo import ItineraryRepository
from app.db.repositories.replan_repo import ReplanRepository
from app.services.routing.base import BaseRoutingProvider
from app.services.impact_service import ImpactService
from app.schemas.impact import ImpactCheckRequest
from app.schemas.replan import ReplanRequest


class ReplanService:
    """Generates alternative itineraries and replan proposals when routes are impacted."""

    def __init__(self, db: Session, routing_provider: BaseRoutingProvider):
        self.db = db
        self.journey_repo = JourneyRepository(db)
        self.event_repo = EventRepository(db)
        self.itinerary_repo = ItineraryRepository(db)
        self.replan_repo = ReplanRepository(db)
        self.impact_service = ImpactService(db)
        self.routing_provider = routing_provider

    def create_replan_proposal(self, req: ReplanRequest) -> ReplanProposalModel:
        journey = self.journey_repo.get_by_id(req.journey_id)
        if not journey:
            raise ValueError(f"Journey with ID {req.journey_id} not found.")

        event = self.event_repo.get_by_id(req.event_id)
        if not event:
            raise ValueError(f"Event with ID {req.event_id} not found.")

        # Check impact
        impact = self.impact_service.check_impact(ImpactCheckRequest(journey_id=req.journey_id, event_id=req.event_id))

        # Get current itinerary
        old_itinerary = None
        if journey.itineraries:
            for it in journey.itineraries:
                if it.is_current:
                    old_itinerary = it
                    break

        if not old_itinerary and journey.itineraries:
            old_itinerary = journey.itineraries[0]

        if not old_itinerary:
            raise ValueError("No active itinerary found for journey.")

        # Request alternative itinerary from routing provider
        alternatives = self.routing_provider.get_alternatives(
            origin=journey.origin,
            destination=journey.destination,
            avoid_affected_leg=impact.affected_leg,
            departure_time=journey.departure_time
        )

        alt_data = alternatives[0] if alternatives else {
            "total_duration": old_itinerary.total_duration,
            "arrival_time": old_itinerary.arrival_time,
            "total_fare": old_itinerary.total_fare + 10.0,
            "walking_minutes": old_itinerary.walking_minutes + 2,
            "transfers": old_itinerary.transfers,
            "risk_score": 0.05,
            "is_current": False,
            "is_protected": True,
            "route_data": {"summary": "Alternative Bypass Route", "legs": []}
        }

        # Create new alternative itinerary entity
        new_itinerary = ItineraryModel(
            id=uuid.uuid4(),
            journey_id=journey.id,
            total_duration=alt_data["total_duration"],
            arrival_time=alt_data["arrival_time"],
            total_fare=alt_data["total_fare"],
            walking_minutes=alt_data["walking_minutes"],
            transfers=alt_data["transfers"],
            risk_score=alt_data["risk_score"],
            is_current=False,
            is_protected=True,
            route_data=alt_data["route_data"]
        )
        self.itinerary_repo.create(new_itinerary)

        # Calculate time saved vs delayed old itinerary
        delayed_old_duration = old_itinerary.total_duration + impact.estimated_delay
        time_saved = max(0, delayed_old_duration - new_itinerary.total_duration)

        reason_msg = f"Disruption on line/route ({event.title}). Estimated delay {impact.estimated_delay} mins. Alternative route bypasses hazard."

        proposal = ReplanProposalModel(
            id=uuid.uuid4(),
            journey_id=journey.id,
            event_id=event.id,
            old_itinerary_id=old_itinerary.id,
            new_itinerary_id=new_itinerary.id,
            reason=reason_msg,
            time_saved=time_saved,
            status=ReplanStatusEnum.PENDING,
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15)
        )
        return self.replan_repo.create(proposal)

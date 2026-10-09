import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.db.models import JourneyModel, ItineraryModel, TravellerModel
from app.db.repositories.journey_repo import JourneyRepository
from app.db.repositories.itinerary_repo import ItineraryRepository
from app.db.repositories.traveller_repo import TravellerRepository
from app.services.routing.base import BaseRoutingProvider
from app.schemas.journey import JourneyPlanRequest


class JourneyService:
    def __init__(self, db: Session, routing_provider: BaseRoutingProvider):
        self.db = db
        self.journey_repo = JourneyRepository(db)
        self.itinerary_repo = ItineraryRepository(db)
        self.traveller_repo = TravellerRepository(db)
        self.routing_provider = routing_provider

    def plan_journey(self, req: JourneyPlanRequest) -> JourneyModel:
        # Verify or auto-create traveller if not existing
        traveller = self.traveller_repo.get_by_id(req.traveller_id)
        if not traveller:
            traveller = TravellerModel(
                id=req.traveller_id,
                name="Default Traveller"
            )
            self.traveller_repo.create(traveller)

        dep_time = req.departure_time or datetime.now(timezone.utc)

        # 1. Create Journey entity
        journey = JourneyModel(
            id=uuid.uuid4(),
            traveller_id=traveller.id,
            origin=req.origin.model_dump(),
            destination=req.destination.model_dump(),
            departure_time=dep_time,
            status="ACTIVE"
        )
        self.journey_repo.create(journey)

        # 2. Call routing provider for initial itinerary
        planned_route = self.routing_provider.plan_route(
            origin=req.origin.model_dump(),
            destination=req.destination.model_dump(),
            departure_time=dep_time,
            allowed_modes=traveller.allowed_modes,
            max_walking_minutes=traveller.max_walking_minutes,
            accessibility_required=traveller.accessibility_required
        )

        itinerary = ItineraryModel(
            id=uuid.uuid4(),
            journey_id=journey.id,
            total_duration=planned_route["total_duration"],
            arrival_time=planned_route["arrival_time"],
            total_fare=planned_route["total_fare"],
            walking_minutes=planned_route["walking_minutes"],
            transfers=planned_route["transfers"],
            risk_score=planned_route["risk_score"],
            is_current=True,
            is_protected=True,
            route_data=planned_route["route_data"]
        )
        self.itinerary_repo.create(itinerary)

        # 3. Update current_itinerary_id on journey
        self.journey_repo.update_current_itinerary(journey.id, itinerary.id)
        return self.journey_repo.get_by_id(journey.id)

    def get_journey(self, journey_id: uuid.UUID) -> Optional[JourneyModel]:
        return self.journey_repo.get_by_id(journey_id)

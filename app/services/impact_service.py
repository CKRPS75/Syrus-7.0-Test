import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.db.models import RouteImpactModel, JourneyModel, EventModel, ItineraryModel, TravellerModel
from app.db.repositories.journey_repo import JourneyRepository
from app.db.repositories.event_repo import EventRepository
from app.db.repositories.impact_repo import ImpactRepository
from app.schemas.impact import ImpactCheckRequest, ImpactResponse


class ImpactService:
    """Calculates disruption impacts and evaluates route feasibility vs route protection."""

    def __init__(self, db: Session):
        self.db = db
        self.journey_repo = JourneyRepository(db)
        self.event_repo = EventRepository(db)
        self.impact_repo = ImpactRepository(db)

    def calculate_delay(self, severity: str) -> int:
        """
        Synthetic Delay Model:
        T_arrival = scheduled_arrival + disruption_delay + missed_connection_delay

        Ranges (Synthetic demo ranges for hackathon):
        Low: 5-10 mins (avg 8)
        Medium: 10-25 mins (avg 15)
        High: 25-60 mins (avg 35)
        """
        sev = (severity or "MEDIUM").upper()
        if sev == "LOW":
            return 8
        elif sev == "HIGH":
            return 35
        else:  # MEDIUM
            return 15

    def check_impact(self, req: ImpactCheckRequest) -> RouteImpactModel:
        journey = self.journey_repo.get_by_id(req.journey_id)
        if not journey:
            raise ValueError(f"Journey with ID {req.journey_id} not found.")

        event = self.event_repo.get_by_id(req.event_id)
        if not event:
            raise ValueError(f"Event with ID {req.event_id} not found.")

        # Check existing impact record or compute new
        existing = self.impact_repo.get_by_journey_and_event(req.journey_id, req.event_id)
        if existing:
            return existing

        # Get current itinerary
        current_itinerary = None
        if journey.itineraries:
            for it in journey.itineraries:
                if it.is_current:
                    current_itinerary = it
                    break
            if not current_itinerary:
                current_itinerary = journey.itineraries[0]

        # 1. Determine if route is affected
        affects_route = False
        affected_leg = {}
        if current_itinerary and current_itinerary.route_data:
            legs = current_itinerary.route_data.get("legs", [])
            for leg in legs:
                # Match leg mode/route/line with event
                if (
                    event.affected_line and event.affected_line.lower() in str(leg.get("line", "")).lower()
                ) or (
                    event.affected_route and event.affected_route.lower() in str(leg.get("route_number", "")).lower()
                ) or (
                    event.affected_stop and event.affected_stop.lower() in str(leg.get("from_name", "")).lower()
                ) or (
                    event.event_type == "FLOODING" and leg.get("mode") in ["BUS", "WALK"]
                ):
                    affects_route = True
                    affected_leg = leg
                    break

        # 2. Calculate delay if affected
        estimated_delay = self.calculate_delay(event.severity) if affects_route else 0

        # 3. Feasibility vs Protection evaluation
        # Route Feasible: Destination can still be reached physically
        route_feasible = True  # In Mumbai MVP, alternative paths / walking exists

        # Route Protected: Deadline and risk tolerance constraints are met under delay
        route_protected = True
        if affects_route and current_itinerary:
            traveller = journey.traveller
            new_arrival = current_itinerary.arrival_time + timedelta(minutes=estimated_delay)

            # Check deadline constraint
            if traveller and traveller.deadline and new_arrival > traveller.deadline:
                route_protected = False

            # Check risk tolerance constraint (e.g. low risk tolerance < 0.3 can't tolerate >15 min delay)
            if traveller and traveller.risk_tolerance < 0.3 and estimated_delay > 10:
                route_protected = False

            # High severity delays (>30 mins) unprotect standard routes
            if estimated_delay >= 30:
                route_protected = False

        impact = RouteImpactModel(
            id=uuid.uuid4(),
            event_id=event.id,
            journey_id=journey.id,
            affects_route=affects_route,
            affected_leg=affected_leg,
            estimated_delay=estimated_delay,
            route_feasible=route_feasible,
            route_protected=route_protected
        )
        return self.impact_repo.create(impact)

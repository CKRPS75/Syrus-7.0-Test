import uuid
from app.services.routing.mock_provider import MockRoutingProvider
from app.services.evidence.mock_processor import MockEvidenceProcessor
from app.services.journey_service import JourneyService
from app.schemas.journey import JourneyPlanRequest, LocationPoint


def test_journey_service_mock_plan(db_session):
    routing_provider = MockRoutingProvider()
    journey_svc = JourneyService(db_session, routing_provider)

    req = JourneyPlanRequest(
        traveller_id=uuid.uuid4(),
        origin=LocationPoint(name="Station A", latitude=19.1, longitude=72.8),
        destination=LocationPoint(name="Station B", latitude=19.2, longitude=72.9)
    )

    journey = journey_svc.plan_journey(req)
    assert journey is not None
    assert journey.current_itinerary_id is not None
    assert len(journey.itineraries) == 1
    assert journey.itineraries[0].total_duration == 45

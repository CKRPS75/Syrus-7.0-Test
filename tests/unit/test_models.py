import uuid
from datetime import datetime, timezone
from app.db.models import (
    TravellerModel, JourneyModel, ItineraryModel, EventModel,
    ReportModel, EvidenceModel, RouteImpactModel, ReplanProposalModel,
    TrustStatusEnum, ValidationStatusEnum, ReplanStatusEnum
)


def test_traveller_and_journey_relationships(db_session):
    traveller = TravellerModel(
        id=uuid.uuid4(),
        name="Unit Test User",
        budget=120.0,
        risk_tolerance=0.4
    )
    db_session.add(traveller)
    db_session.commit()

    journey = JourneyModel(
        id=uuid.uuid4(),
        traveller_id=traveller.id,
        origin={"name": "Origin A", "lat": 19.0, "lng": 72.8},
        destination={"name": "Dest B", "lat": 19.1, "lng": 72.9}
    )
    db_session.add(journey)
    db_session.commit()

    retrieved = db_session.query(JourneyModel).filter(JourneyModel.id == journey.id).first()
    assert retrieved is not None
    assert retrieved.traveller.name == "Unit Test User"
    assert retrieved.origin["name"] == "Origin A"

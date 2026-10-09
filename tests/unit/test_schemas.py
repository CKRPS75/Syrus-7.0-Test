import pytest
import uuid
from pydantic import ValidationError
from app.schemas.traveller import TravellerCreate
from app.schemas.journey import JourneyPlanRequest, LocationPoint


def test_traveller_schema_validation():
    valid = TravellerCreate(
        name="Test User",
        budget=100.0,
        risk_tolerance=0.8
    )
    assert valid.name == "Test User"

    with pytest.raises(ValidationError):
        # Invalid risk_tolerance > 1.0
        TravellerCreate(name="Bad User", risk_tolerance=1.5)


def test_journey_plan_schema_validation():
    req = JourneyPlanRequest(
        traveller_id=uuid.uuid4(),
        origin=LocationPoint(name="Andheri", latitude=19.11, longitude=72.84),
        destination=LocationPoint(name="BKC", latitude=19.06, longitude=72.86)
    )
    assert req.origin.name == "Andheri"

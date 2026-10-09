from unittest.mock import Mock, patch

from app.services.crowding_service import estimate_crowding
from app.services.otp_service import plan_journey


def test_weekday_morning_towards_bkc_has_higher_risk_than_weekend():
    weekday = estimate_crowding(
        "Dadar",
        "BKC",
        "2026-10-09T08:45:00+05:30",
        legs=[{"mode": "RAIL"}, {"mode": "WALK"}],
    )
    weekend = estimate_crowding(
        "Dadar",
        "BKC",
        "2026-10-10T08:45:00+05:30",
        legs=[{"mode": "RAIL"}, {"mode": "WALK"}],
    )

    assert weekday["crowding_risk"] > weekend["crowding_risk"]
    assert weekday["is_observed"] is False
    assert weekend["confidence"] <= weekday["confidence"]


def test_plan_journey_adds_crowding_metadata():
    leg = {
        "mode": "RAIL",
        "start": {"scheduledTime": "2026-10-09T08:00:00+05:30"},
        "end": {"scheduledTime": "2026-10-09T08:15:00+05:30"},
        "duration": 900,
        "distance": 2500,
        "from": {"name": "Bandra", "lat": 19.0544, "lon": 72.8402},
        "to": {"name": "Andheri", "lat": 19.1197, "lon": 72.8464},
        "route": {"shortName": "Western", "longName": "Western Line"},
    }
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "data": {
            "plan": {
                "itineraries": [{
                    "start": "2026-10-09T08:05:00+05:30",
                    "end": "2026-10-09T08:25:00+05:30",
                    "duration": 1200,
                    "walkDistance": 200,
                    "numberOfTransfers": 0,
                    "legs": [leg],
                }],
                "routingErrors": [],
            }
        }
    }

    with patch("app.services.otp_service.requests.post", return_value=response):
        journeys = plan_journey("Bandra", "Andheri", "2026-10-09T08:00:00")

    journey = journeys[0]
    assert journey.crowding_risk is not None
    assert journey.crowding_summary
    assert journey.legs[0].crowding_risk == journey.crowding_risk

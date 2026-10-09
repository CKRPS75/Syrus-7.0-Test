import unittest
from unittest.mock import Mock, patch

from app.services.otp_service import plan_journey


def _leg(mode, from_name, to_name, route=None):
    return {
        "mode": mode,
        "start": {"scheduledTime": "2026-10-09T10:00:00+05:30"},
        "end": {"scheduledTime": "2026-10-09T10:05:00+05:30"},
        "duration": 300,
        "distance": 1000,
        "from": {"name": from_name, "lat": 19.0, "lon": 72.0},
        "to": {"name": to_name, "lat": 19.0, "lon": 72.0},
        "route": route,
    }


def _itinerary(start, legs):
    return {
        "start": start,
        "end": "2026-10-09T10:30:00+05:30",
        "duration": 1800,
        "walkDistance": 500,
        "numberOfTransfers": 1,
        "legs": legs,
    }


class TestPlanJourney(unittest.TestCase):
    @patch("app.services.otp_service.requests.post")
    def test_deduplicates_sequences_and_retains_departure_times(self, post):
        train_and_metro = [
            _leg("RAIL", "Bandra", "Andheri", {"shortName": "Western", "longName": "Western Line"}),
            _leg("SUBWAY", "Andheri", "Versova", {"shortName": "Line 1", "longName": "Blue Line"}),
        ]
        bus_route = [
            _leg("WALK", "Origin", "Bandra Talao"),
            _leg("BUS", "Bandra Talao", "Riddhi Siddhi", {"shortName": "200AS", "longName": "Bus 200AS"}),
            _leg("WALK", "Riddhi Siddhi", "Destination"),
        ]
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "data": {
                "plan": {
                    "itineraries": [
                        _itinerary("2026-10-09T10:03:00+05:30", train_and_metro),
                        _itinerary("2026-10-09T10:08:00+05:30", train_and_metro),
                        _itinerary("2026-10-09T10:05:13+05:30", bus_route),
                    ],
                    "routingErrors": [],
                }
            }
        }
        post.return_value = response

        journeys = plan_journey("Bandra", "Versova", "2026-10-09T10:00:00")

        self.assertEqual(len(journeys), 2)
        self.assertEqual(
            journeys[0].departure_options,
            [
                "2026-10-09T10:03:00+05:30",
                "2026-10-09T10:08:00+05:30",
            ],
        )
        self.assertEqual(
            [(leg.mode, leg.route_name) for leg in journeys[0].legs],
            [("RAIL", "Western"), ("SUBWAY", "Line 1")],
        )
        self.assertEqual(journeys[0].legs[0].route_long_name, "Western Line")
        self.assertEqual(
            [(leg.mode, leg.route_name) for leg in journeys[1].legs],
            [("WALK", None), ("BUS", "200AS"), ("WALK", None)],
        )
        self.assertEqual(journeys[1].legs[0].from_place, "Bandra")
        self.assertEqual(journeys[1].legs[-1].to_place, "Versova")
        self.assertTrue(journeys[0].fare_is_estimate)

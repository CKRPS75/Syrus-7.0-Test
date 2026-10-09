from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from app.services.routing.base import BaseRoutingProvider


class MockRoutingProvider(BaseRoutingProvider):
    """Deterministic mock routing provider for Mumbai MVP (Bus, Metro, Walk)."""

    def plan_route(
        self,
        origin: Dict[str, Any],
        destination: Dict[str, Any],
        departure_time: Optional[datetime] = None,
        allowed_modes: Optional[List[str]] = None,
        max_walking_minutes: int = 30,
        accessibility_required: bool = False
    ) -> Dict[str, Any]:
        dep = departure_time or datetime.now(timezone.utc)
        arr = dep + timedelta(minutes=45)

        return {
            "total_duration": 45,
            "arrival_time": arr,
            "total_fare": 25.0,
            "walking_minutes": 10,
            "transfers": 1,
            "risk_score": 0.1,
            "is_current": True,
            "is_protected": True,
            "route_data": {
                "summary": "Walk -> Metro Line 1 -> BEST Bus 351 -> Walk",
                "legs": [
                    {
                        "leg_id": "leg_1",
                        "mode": "WALK",
                        "from_name": origin.get("name", "Origin"),
                        "to_name": "Andheri Metro Station",
                        "duration_minutes": 5,
                        "distance_km": 0.4
                    },
                    {
                        "leg_id": "leg_2",
                        "mode": "METRO",
                        "line": "Metro Line 1",
                        "from_name": "Andheri Metro Station",
                        "to_name": "Ghatkopar Station",
                        "duration_minutes": 20,
                        "distance_km": 11.4
                    },
                    {
                        "leg_id": "leg_3",
                        "mode": "BUS",
                        "route_number": "BEST Bus 351",
                        "from_name": "Ghatkopar Station",
                        "to_name": "Kurla Depot",
                        "duration_minutes": 15,
                        "distance_km": 4.2
                    },
                    {
                        "leg_id": "leg_4",
                        "mode": "WALK",
                        "from_name": "Kurla Depot",
                        "to_name": destination.get("name", "Destination"),
                        "duration_minutes": 5,
                        "distance_km": 0.3
                    }
                ]
            }
        }

    def get_alternatives(
        self,
        origin: Dict[str, Any],
        destination: Dict[str, Any],
        avoid_affected_leg: Optional[Dict[str, Any]] = None,
        departure_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        dep = departure_time or datetime.now(timezone.utc)
        arr = dep + timedelta(minutes=40)

        # Alternative route avoiding disrupted bus/metro line
        return [
            {
                "total_duration": 40,
                "arrival_time": arr,
                "total_fare": 35.0,
                "walking_minutes": 8,
                "transfers": 1,
                "risk_score": 0.05,
                "is_current": False,
                "is_protected": True,
                "route_data": {
                    "summary": "Walk -> Metro Line 2A / 7 Direct -> Walk",
                    "reason": "Bypasses flooded bus corridor",
                    "legs": [
                        {
                            "leg_id": "alt_leg_1",
                            "mode": "WALK",
                            "from_name": origin.get("name", "Origin"),
                            "to_name": "DN Nagar Station",
                            "duration_minutes": 4,
                            "distance_km": 0.3
                        },
                        {
                            "leg_id": "alt_leg_2",
                            "mode": "METRO",
                            "line": "Metro Line 2A",
                            "from_name": "DN Nagar Station",
                            "to_name": destination.get("name", "Destination"),
                            "duration_minutes": 32,
                            "distance_km": 14.0
                        },
                        {
                            "leg_id": "alt_leg_3",
                            "mode": "WALK",
                            "from_name": "Metro Exit",
                            "to_name": destination.get("name", "Destination"),
                            "duration_minutes": 4,
                            "distance_km": 0.2
                        }
                    ]
                }
            }
        ]

    def estimate_arrival(self, itinerary_data: Dict[str, Any], delay_minutes: int) -> datetime:
        base_arr = itinerary_data.get("arrival_time") or datetime.now(timezone.utc)
        return base_arr + timedelta(minutes=delay_minutes)

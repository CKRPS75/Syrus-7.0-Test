from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class BaseRoutingProvider(ABC):
    @abstractmethod
    def plan_route(
        self,
        origin: Dict[str, Any],
        destination: Dict[str, Any],
        departure_time: Optional[datetime] = None,
        allowed_modes: Optional[List[str]] = None,
        max_walking_minutes: int = 30,
        accessibility_required: bool = False
    ) -> Dict[str, Any]:
        """Plans an initial multimodal route between origin and destination."""
        pass

    @abstractmethod
    def get_alternatives(
        self,
        origin: Dict[str, Any],
        destination: Dict[str, Any],
        avoid_affected_leg: Optional[Dict[str, Any]] = None,
        departure_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Returns alternative itineraries avoiding specified disrupted legs."""
        pass

    @abstractmethod
    def estimate_arrival(
        self,
        itinerary_data: Dict[str, Any],
        delay_minutes: int
    ) -> datetime:
        """Estimates updated arrival time given delay minutes."""
        pass

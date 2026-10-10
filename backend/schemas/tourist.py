from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class TouristStopInput(BaseModel):
    id: str
    name: str
    lat: float
    lon: Optional[float] = None
    lng: Optional[float] = None
    open_time: str = "00:00"
    close_time: str = "23:59"
    dwell_minutes: int = 45
    typical_dwell_minutes: Optional[int] = None
    priority: str = "MEDIUM" # HIGH, MEDIUM, LOW, FIXED
    fare_inr: float = 0.0
    entryFee: Optional[float] = None

    def get_lon(self) -> float:
        if self.lon is not None:
            return self.lon
        if self.lng is not None:
            return self.lng
        return 72.8464


class PlanTourRequest(BaseModel):
    start_location_name: Optional[str] = None
    start_location: Optional[str] = None
    custom_start_lat: Optional[float] = None
    custom_start_lon: Optional[float] = None
    stops: List[TouristStopInput]
    start_time: str = "08:30" # HH:MM
    curfew_deadline: str = "20:30" # HH:MM
    max_walking_m: Optional[int] = 1500
    budget_inr: Optional[float] = 100.0
    budget_mode: str = "LOWEST_COST" # LOWEST_COST, BALANCED, FASTEST

class PlannedTourLeg(BaseModel):
    from_stop: str
    to_stop: str
    mode: str = "BUS" # BUS, METRO, WALK, RAIL
    route_name: str
    bus_or_train_number: str
    boarding_stop: str
    alighting_stop: str
    distance_m: int
    duration_min: int
    fare_inr: float = 0.0
    departure_time: str
    arrival_time: str

class PlannedVisitWindow(BaseModel):
    stop_id: str
    stop_name: str
    arrival_time: str
    departure_time: str
    dwell_minutes: int
    open_time: str
    close_time: str
    is_open: bool
    priority: str
    ticket_fare_inr: float = 0.0

class TourPlanResponse(BaseModel):
    status: str = "FEASIBLE" # FEASIBLE, PROTECTED, BUDGET_DEFICIT, INFEASIBLE
    start_location: str
    budget_mode: str
    total_stops_visited: int
    total_travel_time_min: int
    total_dwell_time_min: int
    start_time: str
    curfew_deadline: str
    expected_return_time: str
    slack_buffer_minutes: int
    min_budget_required_inr: float
    total_transit_fare_inr: float
    total_ticket_fare_inr: float
    total_fare_inr: float
    budget_remaining_inr: float
    is_budget_sufficient: bool
    total_walking_m: int
    legs: List[PlannedTourLeg]
    visit_windows: List[PlannedVisitWindow]
    dropped_stops: List[TouristStopInput] = []
    reordered: bool = False
    explanation: str

class ReplanTourRequest(BaseModel):
    current_plan: TourPlanResponse
    disrupted_route: Optional[str] = None
    disrupted_location: Optional[str] = None
    delay_severity: str = "HIGH"
    confirmed: bool = True

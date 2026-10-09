import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.traveller import TravellerResponse
from app.schemas.itinerary import ItineraryResponse


class LocationPoint(BaseModel):
    name: str = Field(..., example="Andheri Station")
    latitude: float = Field(..., example=19.1197)
    longitude: float = Field(..., example=72.8464)


class JourneyPlanRequest(BaseModel):
    traveller_id: uuid.UUID
    origin: LocationPoint
    destination: LocationPoint
    departure_time: Optional[datetime] = None
    allowed_modes: List[Literal["BUS", "METRO", "TRAIN", "WALK"]] | None = None


class JourneyResponse(BaseModel):
    id: uuid.UUID
    traveller_id: uuid.UUID
    origin: Dict[str, Any]
    destination: Dict[str, Any]
    departure_time: datetime
    status: str
    current_itinerary_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JourneyRequest(BaseModel):
    origin: str
    destination: str
    departure: str
    deadline: str | None = None
    budget: float | None = None
    max_walking: int | None = None
    accessibility_required: bool = False
    allowed_modes: List[Literal["BUS", "METRO", "TRAIN", "WALK"]] | None = None
    forbidden_modes: List[str] = Field(default_factory=list)
    transfer_tolerance: int | None = None
    risk_tolerance: str = "MEDIUM"


class JourneyDetailResponse(JourneyResponse):
    traveller: Optional[TravellerResponse] = None
    current_itinerary: Optional[ItineraryResponse] = None
    itineraries: List[ItineraryResponse] = Field(default_factory=list)
    route_impacts: List[Dict[str, Any]] = Field(default_factory=list)
    replan_proposals: List[Dict[str, Any]] = Field(default_factory=list)

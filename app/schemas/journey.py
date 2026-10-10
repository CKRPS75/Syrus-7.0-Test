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


class JourneyRequest(BaseModel):
    origin: str = Field(..., example="Chembur")
    destination: str = Field(..., example="Andheri")
    departure: str = Field(default="2026-10-09T17:00:00", example="5:00 PM")
    deadline: Optional[str] = Field(default=None, example="7:00 PM")
    budget: Optional[float] = Field(default=80.0, example=80.0)
    max_walking: Optional[int] = Field(default=1000, example=1000)
    accessibility_required: bool = Field(default=False)
    allowed_modes: Optional[List[str]] = Field(default=["BUS", "METRO", "WALK"])
    forbidden_modes: Optional[List[str]] = Field(default_factory=list)
    transfer_tolerance: Optional[int] = Field(default=3)
    risk_tolerance: Optional[float] = Field(default=0.5)


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

from pydantic import BaseModel, Field
from typing import List


class JourneyLeg(BaseModel):
    mode: str
    from_place: str
    to_place: str
    distance_m: int | None = None
    duration_min: int | None = None
    route_name: str | None = None
    route_long_name: str | None = None
    wheelchair_accessible: bool = True


class Journey(BaseModel):
    journey_id: str
    origin: str
    destination: str
    departure: str
    departure_options: List[str] = Field(
        default_factory=list,
        description="Departure times returned by OTP for this leg sequence."
    )
    arrival: str | None = None
    fare: float | None = None
    fare_is_estimate: bool = Field(
        default=False,
        description="True when fare is synthetic and not an operator-published fare."
    )
    walking_m: int = 0
    transfers: int = 0
    wheelchair_accessible: bool = True
    legs: List[JourneyLeg] = Field(default_factory=list)
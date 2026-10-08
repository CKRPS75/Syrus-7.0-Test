from pydantic import BaseModel


class ReplanRequest(BaseModel):
    origin: str
    destination: str
    departure: str

    route_name: str
    disruption_type: str
    severity: str

    confirmed: bool = False
    active: bool = True

    deadline: str | None = None
    budget: float | None = None
    max_walking: int | None = None
    transfer_tolerance: int | None = None
    forbidden_modes: list[str] = []
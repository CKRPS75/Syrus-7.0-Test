from pydantic import BaseModel


class Disruption(BaseModel):
    disruption_id: str
    route_name: str | None = None
    stop_name: str | None = None
    disruption_type: str
    severity: str
    confirmed: bool = False
    active: bool = True
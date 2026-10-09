import os
import json
from fastapi import APIRouter, HTTPException
from typing import List
from backend.schemas.tourist import (
    TouristStopInput,
    PlanTourRequest,
    TourPlanResponse,
    ReplanTourRequest
)
from backend.routing.tourist_optimizer import (
    plan_tourist_itinerary,
    replan_tourist_itinerary,
    resolve_start_location
)

router = APIRouter(
    prefix="/tourist",
    tags=["Multi-Stop Tourist Optimizer (Persona T5)"]
)

ATTRACTIONS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "cities", "mumbai", "tourist_attractions.json"
)

@router.get("/attractions", response_model=List[dict])
def get_mumbai_attractions():
    """Returns curated Mumbai landmarks with opening hours, dwell times, and coordinates."""
    if not os.path.exists(ATTRACTIONS_FILE):
        raise HTTPException(status_code=404, detail="Attractions file not found")
    with open(ATTRACTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@router.post("/plan", response_model=TourPlanResponse)
def plan_tour(request: PlanTourRequest):
    """
    Plans a multi-stop day itinerary from ANY Mumbai starting location (e.g. Andheri, Chembur, Dadar)
    with authentic BEST bus & local train numbers, venue opening hours, and lowest budget optimization.
    """
    try:
        return plan_tourist_itinerary(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/replan", response_model=TourPlanResponse)
def replan_tour(request: ReplanTourRequest):
    """
    Mid-day disruption replanner for Persona T5:
    Reorders stops or drops low-priority stops to preserve curfew and budget.
    """
    try:
        delay_map = {"LOW": 10, "MEDIUM": 25, "HIGH": 45}
        delay_min = delay_map.get(request.delay_severity.upper(), 35)

        plan = request.current_plan
        origin_base = resolve_start_location(plan.start_location)

        stops = []
        for w in plan.visit_windows:
            stops.append(TouristStopInput(
                id=w.stop_id,
                name=w.stop_name,
                lat=18.9220,
                lon=72.8347,
                open_time=w.open_time,
                close_time=w.close_time,
                dwell_minutes=w.dwell_minutes,
                priority=w.priority
            ))

        if os.path.exists(ATTRACTIONS_FILE):
            with open(ATTRACTIONS_FILE, "r", encoding="utf-8") as f:
                cat = {item["id"]: item for item in json.load(f)}
                for s in stops:
                    if s.id in cat:
                        s.lat = cat[s.id]["lat"]
                        s.lon = cat[s.id]["lon"]

        budget_limit = plan.total_fare_inr + plan.budget_remaining_inr

        return replan_tourist_itinerary(
            origin_base=origin_base,
            current_stops=stops,
            start_time_str=plan.start_time,
            curfew_str=plan.curfew_deadline,
            budget_mode=plan.budget_mode or "LOWEST_COST",
            budget_inr=budget_limit,
            disruption_delay_min=delay_min,
            disrupted_location=request.disrupted_location
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

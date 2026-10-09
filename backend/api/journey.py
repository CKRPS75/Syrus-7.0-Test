import os
import json
import math
import requests
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.models.journey import Journey, JourneyLeg
from app.schemas.journey import JourneyRequest

router = APIRouter(
    prefix="/journey",
    tags=["Journey Planning (Person 3 / 4)"]
)

# Coordinates for major Mumbai transit hubs
MUMBAI_GEOCODE = {
    "CHEMBUR": (19.0622, 72.8974),
    "ANDHERI": (19.1197, 72.8464),
    "ANDHERI WEST": (19.1278, 72.8277),
    "ANDHERI EAST": (19.1158, 72.8569),
    "GHATKOPAR": (19.0858, 72.9081),
    "DADAR": (19.0178, 72.8478),
    "BANDRA": (19.0596, 72.8295),
    "BKC": (19.0652, 72.8687),
    "BORIVALI": (19.2291, 72.8574),
    "CHURCHGATE": (18.9322, 72.8264),
    "CSMT": (18.9400, 72.8353),
    "VERSOVA": (19.1316, 72.8174),
    "COLABA": (18.9067, 72.8147),
    "KURLA": (19.0657, 72.8793),
    "DAHISAR": (19.2573, 72.8601),
    "VIKHROLI": (19.1105, 72.9256)
}

def resolve_coords(location_str: str) -> tuple:
    loc_clean = location_str.upper().strip()
    for key, coords in MUMBAI_GEOCODE.items():
        if key in loc_clean or loc_clean in key:
            return coords
    # Default fallback to Mumbai center
    return (19.0760, 72.8777)


def resolve_known_coords(location_str: str) -> tuple | None:
    loc_clean = location_str.upper().strip()
    if not loc_clean:
        return None
    for key, coords in MUMBAI_GEOCODE.items():
        if key in loc_clean or loc_clean in key:
            return coords
    return None


OTP_URL = "http://localhost:8080/otp/routers/default/index/graphql"

def query_otp_or_simulate(origin: str, dest: str, dep_time: str, req: JourneyRequest) -> List[dict]:
    fromLat, fromLon = resolve_coords(origin)
    toLat, toLon = resolve_coords(dest)
    allowed_modes = req.allowed_modes
    if allowed_modes is None:
        allowed_modes = ["BUS", "METRO", "WALK"]
    otp_modes = {
        "BUS": "BUS",
        "METRO": "SUBWAY",
        "TRAIN": "RAIL",
        "WALK": "WALK",
    }
    selected_otp_modes = [otp_modes[mode] for mode in allowed_modes]
    if not selected_otp_modes:
        return []

    date_part = dep_time.split("T")[0] if "T" in dep_time else datetime.now().strftime("%Y-%m-%d")
    time_part = dep_time.split("T")[1] if "T" in dep_time else "17:00:00"
    if "+" in time_part:
        time_part = time_part.split("+")[0]

    # Try querying OTP if running
    try:
        transport_modes = ", ".join(
            f"{{ mode: {mode} }}" for mode in selected_otp_modes
        )
        query = """
        query TestJourney($fromLat: Float!, $fromLon: Float!, $toLat: Float!, $toLon: Float!, $date: String!, $time: String!) {
          plan(
            from: { lat: $fromLat, lon: $fromLon }
            to: { lat: $toLat, lon: $toLon }
            date: $date
            time: $time
            arriveBy: false
            transportModes: [__TRANSPORT_MODES__]
            numItineraries: 3
          ) {
            itineraries {
              start
              end
              duration
              walkDistance
              numberOfTransfers
              legs {
                mode
                duration
                distance
                from { name lat lon }
                to { name lat lon }
                intermediatePlaces { name lat lon }
                route { shortName longName }
              }
            }
          }
        }
        """
        query = query.replace("__TRANSPORT_MODES__", transport_modes)
        resp = requests.post(OTP_URL, json={"query": query, "variables": {
            "fromLat": fromLat, "fromLon": fromLon, "toLat": toLat, "toLon": toLon,
            "date": date_part, "time": time_part
        }}, timeout=3)

        if resp.status_code == 200:
            data = resp.json()
            if "data" in data and data["data"]["plan"] and data["data"]["plan"]["itineraries"]:
                itineraries = data["data"]["plan"]["itineraries"]
                out = []
                for idx, itin in enumerate(itineraries):
                    legs = []
                    for l in itin["legs"]:
                        route_name = l["route"]["shortName"] if l.get("route") else None
                        stops = []
                        for stop in [
                            l.get("from"),
                            *(l.get("intermediatePlaces") or []),
                            l.get("to"),
                        ]:
                            if (
                                stop
                                and stop.get("name")
                                and stop.get("lat") is not None
                                and stop.get("lon") is not None
                            ):
                                coordinates = [stop["lon"], stop["lat"]]
                                if not stops or stops[-1]["coordinates"] != coordinates:
                                    stops.append({
                                        "name": stop["name"],
                                        "coordinates": coordinates,
                                    })
                        legs.append({
                            "mode": l["mode"],
                            "route_name": route_name,
                            "from_place": l["from"]["name"],
                            "to_place": l["to"]["name"],
                            "duration_min": round(l["duration"] / 60),
                            "distance_m": round(l["distance"]),
                            "coordinates": [
                                [l["from"]["lon"], l["from"]["lat"]],
                                [l["to"]["lon"], l["to"]["lat"]],
                            ] if (
                                l["from"].get("lat") is not None
                                and l["from"].get("lon") is not None
                                and l["to"].get("lat") is not None
                                and l["to"].get("lon") is not None
                            ) else [],
                            "stops": stops,
                        })
                    fare = 20.0 + (len([l for l in legs if l["mode"] != "WALK"]) - 1) * 10.0
                    out.append({
                        "journey_id": f"OTP-{idx+1:03d}",
                        "origin": origin,
                        "destination": dest,
                        "departure": itin["start"],
                        "arrival": itin["end"],
                        "fare": max(10.0, fare),
                        "walking_m": round(itin["walkDistance"]),
                        "transfers": itin["numberOfTransfers"],
                        "wheelchair_accessible": req.accessibility_required if req else True,
                        "legs": legs
                    })
                return out
    except Exception:
        pass

    # The local simulation only represents bus, metro and walking journeys.
    if not {"BUS", "METRO", "WALK"}.issubset(set(allowed_modes)):
        return []

    # Fallback to realistic Multi-modal Simulation (Chembur -> Andheri etc.)
    d_lat = toLat - fromLat
    d_lon = toLon - fromLon
    dist_km = math.sqrt(d_lat**2 + d_lon**2) * 111.0

    # Realistic legs
    legs = [
        {"mode": "WALK", "route_name": "Walk", "from_place": origin, "to_place": f"{origin} Bus Stand", "duration_min": 5, "distance_m": 350},
        {"mode": "BUS", "route_name": "Bus 365", "from_place": f"{origin} Bus Stand", "to_place": "Kurla / Ghatkopar", "duration_min": 25, "distance_m": int(dist_km * 400)},
        {"mode": "SUBWAY", "route_name": "Metro Line 1", "from_place": "Ghatkopar Metro", "to_place": f"{dest} Metro", "duration_min": 18, "distance_m": int(dist_km * 550)},
        {"mode": "WALK", "route_name": "Walk", "from_place": f"{dest} Metro", "to_place": dest, "duration_min": 6, "distance_m": 420}
    ]
    for leg in legs:
        from_coords = resolve_known_coords(leg["from_place"])
        to_coords = resolve_known_coords(leg["to_place"])
        leg["coordinates"] = (
            [[from_coords[1], from_coords[0]], [to_coords[1], to_coords[0]]]
            if from_coords is not None and to_coords is not None
            else []
        )
        leg["stops"] = (
            [
                {"name": leg["from_place"], "coordinates": [from_coords[1], from_coords[0]]},
                {"name": leg["to_place"], "coordinates": [to_coords[1], to_coords[0]]},
            ]
            if from_coords is not None and to_coords is not None
            else []
        )

    total_dur_min = sum(l["duration_min"] for l in legs)
    fare = 45.0 # ₹15 bus + ₹30 metro

    start_dt = datetime.now(timezone.utc)
    end_dt = datetime.fromtimestamp(start_dt.timestamp() + total_dur_min * 60, timezone.utc)

    return [{
        "journey_id": "MUM-PLAN-001",
        "origin": origin,
        "destination": dest,
        "departure": start_dt.strftime("%I:%M %p"),
        "arrival": end_dt.strftime("%I:%M %p"),
        "fare": fare,
        "walking_m": 770,
        "transfers": 1,
        "wheelchair_accessible": True,
        "legs": legs
    }]

@router.post("/plan")
def plan_journey_endpoint(req: JourneyRequest):
    """Generates optimal multi-modal journey plan for given origin/destination."""
    journeys = query_otp_or_simulate(req.origin, req.destination, req.departure, req)
    if not journeys:
        raise HTTPException(status_code=404, detail="No feasible route found")
    return {
        "status": "SUCCESS",
        "origin": req.origin,
        "destination": req.destination,
        "departure": req.departure,
        "deadline": req.deadline,
        "budget": req.budget,
        "journey": journeys[0],
        "alternatives": journeys[1:]
    }

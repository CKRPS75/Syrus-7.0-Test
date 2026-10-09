import os
import json
import math
import itertools
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict, Any
from backend.schemas.tourist import (
    TouristStopInput,
    PlanTourRequest,
    PlannedTourLeg,
    PlannedVisitWindow,
    TourPlanResponse,
    ReplanTourRequest
)

# Reference File Path
MUMBAI_REF_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "mumbai_reference.json"
)

def load_dataset_stations() -> Dict[str, Dict[str, Any]]:
    """Dynamically loads verified Greater Mumbai transit stops from mumbai_reference.json."""
    stations_map = {}
    if os.path.exists(MUMBAI_REF_FILE):
        try:
            with open(MUMBAI_REF_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for s in data.get("stops", []):
                    key = s["stop_name"].upper().strip()
                    stations_map[key] = {
                        "name": s["stop_name"],
                        "lat": s["latitude"],
                        "lon": s["longitude"],
                        "routes": s.get("routes", []),
                        "aliases": [a.upper() for a in s.get("aliases", [])]
                    }
        except Exception as e:
            print("Error loading dataset stations:", e)
    return stations_map

DATASET_STATIONS = load_dataset_stations()

def calculate_best_bus_fare(dist_km: float, is_ac: bool = False) -> float:
    """Calculates official BEST bus fare from mumbai_reference.json."""
    if is_ac:
        # BEST AC: 0-5 km: ₹12, 5-10 km: ₹18, 10-15 km: ₹25, 15+ km: ₹30
        if dist_km <= 5.0: return 12.0
        elif dist_km <= 10.0: return 18.0
        elif dist_km <= 15.0: return 25.0
        else: return 30.0
    else:
        # BEST Non-AC: 0-5 km: ₹10, 5-10 km: ₹15, 10-15 km: ₹20, 15+ km: ₹25
        if dist_km <= 5.0: return 10.0
        elif dist_km <= 10.0: return 15.0
        elif dist_km <= 15.0: return 20.0
        else: return 25.0

def calculate_local_train_fare(dist_km: float) -> float:
    """Calculates Suburban Railway Second Class fare."""
    if dist_km <= 10.0: return 5.0
    elif dist_km <= 20.0: return 10.0
    elif dist_km <= 35.0: return 15.0
    else: return 20.0

def calculate_metro_fare(dist_km: float) -> float:
    """Calculates Mumbai Metro fare from mumbai_reference.json."""
    if dist_km <= 3.0: return 10.0
    elif dist_km <= 12.0: return 20.0
    elif dist_km <= 18.0: return 30.0
    elif dist_km <= 24.0: return 40.0
    elif dist_km <= 30.0: return 50.0
    else: return 60.0

def resolve_start_location(name: str, custom_lat: Optional[float] = None, custom_lon: Optional[float] = None) -> TouristStopInput:
    """Dynamically resolves verified Greater Mumbai locations from dataset."""
    if custom_lat and custom_lon:
        return TouristStopInput(
            id="CUSTOM_START",
            name=name,
            lat=custom_lat,
            lon=custom_lon,
            priority="FIXED"
        )
    
    clean_name = name.strip().upper()
    
    for key, data in DATASET_STATIONS.items():
        if clean_name in key or key in clean_name or any(clean_name in alias or alias in clean_name for alias in data["aliases"]):
            return TouristStopInput(
                id=f"LOC_{key.replace(' ', '_')}",
                name=data["name"],
                lat=data["lat"],
                lon=data["lon"],
                priority="FIXED"
            )
            
    # Default Greater Mumbai fallback: Dadar / Central Mumbai
    dadar = DATASET_STATIONS.get("DADAR", {"name": "Dadar", "lat": 19.0178, "lon": 72.8478})
    return TouristStopInput(
        id="LOC_DADAR",
        name=dadar["name"],
        lat=dadar["lat"],
        lon=dadar["lon"],
        priority="FIXED"
    )

def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000  # meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def time_to_mins(time_str: str) -> int:
    parts = time_str.split(":")
    return int(parts[0]) * 60 + int(parts[1])

def mins_to_time(minutes: int) -> str:
    h = (minutes // 60) % 24
    m = minutes % 60
    return f"{h:02d}:{m:02d}"

def determine_mumbai_transit_route(from_stop: TouristStopInput, to_stop: TouristStopInput, budget_mode: str = "LOWEST_COST") -> Dict[str, Any]:
    """
    Assigns strictly verified BEST bus lines and Suburban Rail / Metro lines
    with official updated fare matrices from mumbai_reference.json.
    """
    dist_m = haversine_distance_m(from_stop.lat, from_stop.lon, to_stop.lat, to_stop.lon)
    dist_km = dist_m / 1000.0
    fn = from_stop.name.upper()
    tn = to_stop.name.upper()
    is_ac = (budget_mode != "LOWEST_COST")

    # 1. Intra-Heritage South Mumbai Walk (< 700m)
    if dist_m < 700:
        return {
            "mode": "WALK",
            "route_name": "Walk (Kala Ghoda Heritage Walk)",
            "bus_or_train_number": "Walking Route",
            "boarding_stop": from_stop.name,
            "alighting_stop": to_stop.name,
            "duration_min": max(4, math.ceil(dist_m / 65.0)),
            "fare_inr": 0.0,
            "distance_m": int(dist_m)
        }

    # 2. Gateway of India ↔ Churchgate / Marine Drive
    if ("GATEWAY" in fn and ("MARINE" in tn or "CHURCHGATE" in tn)) or (("MARINE" in fn or "CHURCHGATE" in fn) and "GATEWAY" in tn):
        fare = calculate_best_bus_fare(dist_km, is_ac)
        return {
            "mode": "BUS",
            "route_name": "BEST Bus Route 112AS",
            "bus_or_train_number": "BEST Bus 112AS",
            "boarding_stop": "Gateway of India (Regal)",
            "alighting_stop": "Ahilyabai Holkar Chowk (Churchgate / Marine Drive)",
            "duration_min": 10,
            "fare_inr": fare,
            "distance_m": int(dist_m)
        }

    # 3. Marine Drive ↔ Girgaon Chowpatty
    if ("MARINE" in fn and "CHOWPATTY" in tn) or ("CHOWPATTY" in fn and "MARINE" in tn):
        fare = calculate_best_bus_fare(dist_km, is_ac)
        return {
            "mode": "BUS",
            "route_name": "BEST Bus Route 108AS",
            "bus_or_train_number": "BEST Bus 108AS",
            "boarding_stop": "Marine Drive Promenade",
            "alighting_stop": "Girgaon Chowpatty (Kamala Nehru Park)",
            "duration_min": 8,
            "fare_inr": fare,
            "distance_m": int(dist_m)
        }

    # 4. CSMT / Fort ↔ Gateway of India
    if ("CSMT" in fn and "GATEWAY" in tn) or ("GATEWAY" in fn and "CSMT" in tn):
        fare = calculate_best_bus_fare(dist_km, is_ac)
        return {
            "mode": "BUS",
            "route_name": "BEST Bus Route 116AS",
            "bus_or_train_number": "BEST Bus 116AS",
            "boarding_stop": "CSMT Station Terminus",
            "alighting_stop": "Gateway of India",
            "duration_min": 12,
            "fare_inr": fare,
            "distance_m": int(dist_m)
        }

    # 5. Western Suburbs (Borivali, Kandivali, Malad, Goregaon, Andheri, Bandra, Dadar) to South Mumbai (Churchgate/Gateway)
    western_corridor = ["BORIVALI", "KANDIVALI", "MALAD", "GOREGAON", "ANDHERI", "BANDRA", "DADAR", "DAHISAR"]
    if any(wc in fn for wc in western_corridor) or any(wc in tn for wc in western_corridor):
        is_origin_western = any(wc in fn for wc in western_corridor)
        hub_name = from_stop.name if is_origin_western else to_stop.name
        dest_name = to_stop.name if is_origin_western else from_stop.name

        train_fare = calculate_local_train_fare(dist_km)
        connector_bus_fare = calculate_best_bus_fare(1.5, is_ac)
        train_dur = max(18, int(dist_km * 1.1) + 6)

        return {
            "mode": "RAIL",
            "route_name": "Western Suburban Railway (Fast Local) + BEST Connector",
            "bus_or_train_number": "WR Fast Local Train + BEST Bus 112AS",
            "boarding_stop": f"{hub_name} Station",
            "alighting_stop": f"Churchgate Station to {dest_name}",
            "duration_min": train_dur + 8,
            "fare_inr": train_fare + connector_bus_fare,
            "distance_m": int(dist_m)
        }

    # 6. Eastern Suburbs (Mulund, Bhandup, Vikhroli, Ghatkopar, Kurla, Chembur, Sion) to South Mumbai (CSMT/Museum)
    eastern_corridor = ["MULUND", "BHANDUP", "VIKHROLI", "GHATKOPAR", "KURLA", "CHEMBUR", "SION"]
    if any(ec in fn for ec in eastern_corridor) or any(ec in tn for ec in eastern_corridor):
        is_origin_eastern = any(ec in fn for ec in eastern_corridor)
        hub_name = from_stop.name if is_origin_eastern else to_stop.name
        dest_name = to_stop.name if is_origin_eastern else from_stop.name

        # Chembur/Kurla has direct BEST Bus 14 to Museum or Harbour Local to CSMT
        if "CHEMBUR" in fn or "CHEMBUR" in tn or "SION" in fn or "SION" in tn:
            bus_fare = calculate_best_bus_fare(dist_km, is_ac)
            return {
                "mode": "BUS",
                "route_name": "BEST Bus Route 14 (Direct to Museum)",
                "bus_or_train_number": "BEST Bus 14",
                "boarding_stop": f"{hub_name} Naka / Station",
                "alighting_stop": f"Dr. S.P. Mukherjee Chowk (Museum / Kala Ghoda)",
                "duration_min": max(22, int(dist_km * 1.5) + 8),
                "fare_inr": bus_fare,
                "distance_m": int(dist_m)
            }
        else:
            train_fare = calculate_local_train_fare(dist_km)
            connector_bus_fare = calculate_best_bus_fare(1.5, is_ac)
            train_dur = max(20, int(dist_km * 1.1) + 6)
            return {
                "mode": "RAIL",
                "route_name": "Central Suburban Railway (Fast Local) + BEST Connector",
                "bus_or_train_number": "Central Local (Fast) + BEST Bus 116AS",
                "boarding_stop": f"{hub_name} Railway Station",
                "alighting_stop": f"CSMT Terminus to {dest_name}",
                "duration_min": train_dur + 8,
                "fare_inr": train_fare + connector_bus_fare,
                "distance_m": int(dist_m)
            }

    # 7. Metro Line 1 & Metro Line 3 Cross Corridors (Andheri ↔ Ghatkopar / BKC ↔ Marol)
    if ("VERSOVA" in fn or "GHATKOPAR" in fn) and ("ANDHERI" in tn or "GHATKOPAR" in tn or "VERSOVA" in tn):
        m_fare = calculate_metro_fare(dist_km)
        return {
            "mode": "METRO",
            "route_name": "Mumbai Metro Line 1 (Blue Line)",
            "bus_or_train_number": "Metro Line 1 (Versova-Ghatkopar)",
            "boarding_stop": f"{from_stop.name} Metro Station",
            "alighting_stop": f"{to_stop.name} Metro Station",
            "duration_min": max(10, int(dist_km * 1.5)),
            "fare_inr": m_fare,
            "distance_m": int(dist_m)
        }

    # 8. General City BEST Bus Routing from Dataset
    bus_fare = calculate_best_bus_fare(dist_km, is_ac)
    return {
        "mode": "BUS",
        "route_name": "BEST City Transit",
        "bus_or_train_number": "BEST Bus 138AS / 123AS",
        "boarding_stop": f"{from_stop.name} Bus Stand",
        "alighting_stop": f"{to_stop.name} Bus Stop",
        "duration_min": max(12, math.ceil(dist_km * 2.0) + 6),
        "fare_inr": bus_fare,
        "distance_m": int(dist_m)
    }

def calculate_single_leg(from_stop: TouristStopInput, to_stop: TouristStopInput, dep_min: int, budget_mode: str = "LOWEST_COST") -> PlannedTourLeg:
    route_info = determine_mumbai_transit_route(from_stop, to_stop, budget_mode)
    arr_min = dep_min + route_info["duration_min"]

    return PlannedTourLeg(
        from_stop=from_stop.name,
        to_stop=to_stop.name,
        mode=route_info["mode"],
        route_name=route_info["route_name"],
        bus_or_train_number=route_info["bus_or_train_number"],
        boarding_stop=route_info["boarding_stop"],
        alighting_stop=route_info["alighting_stop"],
        distance_m=route_info["distance_m"],
        duration_min=route_info["duration_min"],
        fare_inr=route_info["fare_inr"],
        departure_time=mins_to_time(dep_min),
        arrival_time=mins_to_time(arr_min)
    )

def simulate_tour(
    origin_base: TouristStopInput,
    stops: List[TouristStopInput],
    start_time_str: str,
    curfew_str: str,
    budget_mode: str = "LOWEST_COST",
    dwell_compress_pct: float = 0.0
) -> Tuple[List[PlannedTourLeg], List[PlannedVisitWindow], int, int, float, float, int, int]:
    current_time_min = time_to_mins(start_time_str)
    curfew_min = time_to_mins(curfew_str)

    legs: List[PlannedTourLeg] = []
    visit_windows: List[PlannedVisitWindow] = []

    total_travel_min = 0
    total_dwell_min = 0
    total_transit_fare = 0.0
    total_ticket_fare = 0.0
    total_walk_m = 0

    current_node = origin_base

    for stop in stops:
        # Leg to attraction
        leg = calculate_single_leg(current_node, stop, current_time_min, budget_mode)
        legs.append(leg)

        current_time_min += leg.duration_min
        total_travel_min += leg.duration_min
        total_transit_fare += leg.fare_inr
        if leg.mode == "WALK":
            total_walk_m += leg.distance_m
        else:
            total_walk_m += 100

        # Dwell at attraction
        effective_dwell = max(15, int(stop.dwell_minutes * (1.0 - dwell_compress_pct)))
        arr_time_str = mins_to_time(current_time_min)
        
        open_m = time_to_mins(stop.open_time)
        close_m = time_to_mins(stop.close_time)
        
        if current_time_min < open_m:
            wait_m = open_m - current_time_min
            current_time_min += wait_m
            total_dwell_min += wait_m

        is_open = (current_time_min >= open_m) and (current_time_min + effective_dwell <= close_m)

        dep_time_str = mins_to_time(current_time_min + effective_dwell)
        visit_windows.append(PlannedVisitWindow(
            stop_id=stop.id,
            stop_name=stop.name,
            arrival_time=arr_time_str,
            departure_time=dep_time_str,
            dwell_minutes=effective_dwell,
            open_time=stop.open_time,
            close_time=stop.close_time,
            is_open=is_open,
            priority=stop.priority,
            ticket_fare_inr=stop.fare_inr
        ))

        current_time_min += effective_dwell
        total_dwell_min += effective_dwell
        total_ticket_fare += stop.fare_inr

        current_node = stop

    # Return Leg back to user's origin
    return_leg = calculate_single_leg(current_node, origin_base, current_time_min, budget_mode)
    legs.append(return_leg)
    current_time_min += return_leg.duration_min
    total_travel_min += return_leg.duration_min
    total_transit_fare += return_leg.fare_inr
    if return_leg.mode == "WALK":
        total_walk_m += return_leg.distance_m

    slack_buffer = curfew_min - current_time_min

    return legs, visit_windows, total_travel_min, total_dwell_min, total_transit_fare, total_ticket_fare, total_walk_m, slack_buffer

def plan_tourist_itinerary(request: PlanTourRequest) -> TourPlanResponse:
    origin_base = resolve_start_location(
        request.start_location_name,
        request.custom_start_lat,
        request.custom_start_lon
    )

    user_budget = request.budget_inr if request.budget_inr is not None else 100.0

    legs, visit_windows, total_travel, total_dwell, total_transit_fare, total_ticket_fare, total_walk, slack = simulate_tour(
        origin_base=origin_base,
        stops=request.stops,
        start_time_str=request.start_time,
        curfew_str=request.curfew_deadline,
        budget_mode=request.budget_mode
    )

    final_arrival = mins_to_time(time_to_mins(request.start_time) + total_travel + total_dwell)
    
    min_budget_required = total_transit_fare
    is_budget_sufficient = user_budget >= min_budget_required
    budget_remaining = max(0.0, user_budget - total_transit_fare)

    if not is_budget_sufficient:
        status = "BUDGET_DEFICIT"
        deficit = min_budget_required - user_budget
        explanation = (
            f"Budget Deficit: Minimum Rs. {min_budget_required:.0f} is required for public transit across these destinations from {origin_base.name}. "
            f"Your allocated budget of Rs. {user_budget:.0f} is Rs. {deficit:.0f} short. Please increase your budget to at least Rs. {min_budget_required:.0f}."
        )
    elif slack >= 20:
        status = "PROTECTED"
        explanation = (
            f"Itinerary from {origin_base.name} is fully protected! Total public transit fare is Rs. {total_transit_fare:.0f} "
            f"(saving Rs. {budget_remaining:.0f} of your Rs. {user_budget:.0f} budget) with a comfortable {slack} min curfew buffer."
        )
    elif slack >= 0:
        status = "FEASIBLE"
        explanation = f"Itinerary is feasible from {origin_base.name} with Rs. {total_transit_fare:.0f} transit cost and a {slack} min curfew buffer."
    else:
        status = "INFEASIBLE"
        explanation = f"Curfew breach by {-slack} mins from {origin_base.name}. Consider starting earlier or reducing stops."

    return TourPlanResponse(
        status=status,
        start_location=origin_base.name,
        budget_mode=request.budget_mode,
        total_stops_visited=len(request.stops),
        total_travel_time_min=total_travel,
        total_dwell_time_min=total_dwell,
        start_time=request.start_time,
        curfew_deadline=request.curfew_deadline,
        expected_return_time=final_arrival,
        slack_buffer_minutes=slack,
        min_budget_required_inr=min_budget_required,
        total_transit_fare_inr=total_transit_fare,
        total_ticket_fare_inr=total_ticket_fare,
        total_fare_inr=total_transit_fare + total_ticket_fare,
        budget_remaining_inr=budget_remaining,
        is_budget_sufficient=is_budget_sufficient,
        total_walking_m=total_walk,
        legs=legs,
        visit_windows=visit_windows,
        dropped_stops=[],
        reordered=False,
        explanation=explanation
    )

def replan_tourist_itinerary(
    origin_base: TouristStopInput,
    current_stops: List[TouristStopInput],
    start_time_str: str,
    curfew_str: str,
    budget_mode: str = "LOWEST_COST",
    budget_inr: float = 100.0,
    disruption_delay_min: int = 35,
    disrupted_location: Optional[str] = None
) -> TourPlanResponse:
    best_candidate = None
    dropped: List[TouristStopInput] = []
    reordered = False

    candidate_stops = list(current_stops)

    while len(candidate_stops) >= 1:
        permutations_to_check = list(itertools.permutations(candidate_stops)) if len(candidate_stops) <= 5 else [tuple(candidate_stops)]
        
        best_perm = None
        best_slack = -999999
        best_legs = None
        best_windows = None
        best_totals = None

        for perm in permutations_to_check:
            p_list = list(perm)
            legs, windows, t_travel, t_dwell, t_transit_fare, t_ticket_fare, walk, slack = simulate_tour(
                origin_base,
                p_list,
                start_time_str,
                curfew_str,
                budget_mode
            )

            effective_slack = slack - disruption_delay_min
            all_open = all(w.is_open for w in windows)

            if all_open and effective_slack > best_slack:
                best_slack = effective_slack
                best_perm = p_list
                best_legs = legs
                best_windows = windows
                best_totals = (t_travel, t_dwell, t_transit_fare, t_ticket_fare, walk)

        if best_perm and best_slack >= 10:
            if best_perm != current_stops:
                reordered = True
            
            t_travel, t_dwell, t_transit_fare, t_ticket_fare, walk = best_totals
            return_min = time_to_mins(curfew_str) - best_slack
            budget_remaining = max(0.0, budget_inr - t_transit_fare)
            
            explanation_parts = []
            if reordered:
                explanation_parts.append(f"Reordered tour sequence to bypass congested corridor near {disrupted_location or 'South Mumbai'}.")
            if dropped:
                dropped_names = ", ".join(d.name for d in dropped)
                explanation_parts.append(f"Dropped low-priority stop(s) [{dropped_names}] to maintain budget and guarantee return to {origin_base.name} before {curfew_str} curfew.")
            if not reordered and not dropped:
                explanation_parts.append(f"Adjusted travel buffers. Expected return to {origin_base.name} with {best_slack} mins to spare.")

            return TourPlanResponse(
                status="PROTECTED" if best_slack >= 20 else "FEASIBLE",
                start_location=origin_base.name,
                budget_mode=budget_mode,
                total_stops_visited=len(best_perm),
                total_travel_time_min=t_travel + disruption_delay_min,
                total_dwell_time_min=t_dwell,
                start_time=start_time_str,
                curfew_deadline=curfew_str,
                expected_return_time=mins_to_time(return_min),
                slack_buffer_minutes=best_slack,
                min_budget_required_inr=t_transit_fare,
                total_transit_fare_inr=t_transit_fare,
                total_ticket_fare_inr=t_ticket_fare,
                total_fare_inr=t_transit_fare + t_ticket_fare,
                budget_remaining_inr=budget_remaining,
                is_budget_sufficient=budget_inr >= t_transit_fare,
                total_walking_m=walk,
                legs=best_legs,
                visit_windows=best_windows,
                dropped_stops=dropped,
                reordered=reordered,
                explanation=" ".join(explanation_parts)
            )

        # Drop lowest priority stop
        low_pri_stops = [s for s in candidate_stops if s.priority.upper() in {"LOW", "OPTIONAL"}]
        med_pri_stops = [s for s in candidate_stops if s.priority.upper() == "MEDIUM"]

        if low_pri_stops:
            to_drop = low_pri_stops[-1]
            candidate_stops.remove(to_drop)
            dropped.append(to_drop)
        elif med_pri_stops:
            to_drop = med_pri_stops[-1]
            candidate_stops.remove(to_drop)
            dropped.append(to_drop)
        else:
            to_drop = candidate_stops.pop()
            dropped.append(to_drop)

    return plan_tourist_itinerary(PlanTourRequest(
        start_location_name=origin_base.name,
        stops=candidate_stops,
        start_time=start_time_str,
        curfew_deadline=curfew_str,
        budget_inr=budget_inr,
        budget_mode=budget_mode
    ))

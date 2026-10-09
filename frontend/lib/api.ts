import {
  TravellerConstraints,
  JourneyPlanResponse,
  DisruptionAlert,
  TouristAttraction,
  TourPlanResponse
} from '../types';
import { computeCarbonMetrics } from './carbonCalculator';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export async function fetchBaseJourney(constraints: TravellerConstraints): Promise<JourneyPlanResponse> {
  const payload = {
    origin: constraints.origin,
    destination: constraints.destination,
    departure: constraints.departureTime || new Date().toISOString(),
    deadline: constraints.deadline,
    budget: constraints.budget,
    max_walking: constraints.maxWalkingMeters,
    accessibility_required: constraints.accessibilityRequired,
    forbidden_modes: []
  };

  const res = await fetch(`${API_BASE_URL}/journey/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    throw new Error(`Journey planning failed: ${res.statusText}`);
  }

  const data = await res.json();
  const j = data.journey;

  const legs = j.legs.map((l: any) => ({
    mode: l.mode,
    lineName: l.route_name,
    fromName: l.from_place,
    toName: l.to_place,
    durationMin: l.duration_min,
    distanceMeters: l.distance_m,
    coordinates: [[72.8467, 19.1205], [72.8569, 19.1158]]
  }));

  const carbonMetrics = computeCarbonMetrics(legs, j.fare);

  return {
    journeyId: j.journey_id || 'MUM-PLAN-001',
    summary: {
      origin: j.origin,
      destination: j.destination,
      departureTime: j.departure,
      arrivalTime: j.arrival,
      fare: j.fare,
      walkingMeters: j.walking_m,
      transfers: j.transfers,
      status: 'OPTIMAL',
      carbon: carbonMetrics
    },
    legs: legs
  };
}

export async function fetchReplanProposal(
  constraints: TravellerConstraints,
  reportText: string,
  sourceType: string = 'official'
): Promise<any> {
  const payload = {
    origin: constraints.origin,
    destination: constraints.destination,
    departure: constraints.departureTime,
    deadline: constraints.deadline,
    budget: constraints.budget,
    max_walking: constraints.maxWalkingMeters,
    accessibility_required: constraints.accessibilityRequired,
    report_text: reportText,
    source_type: sourceType,
    disrupted_route: "Metro Line 1"
  };

  const res = await fetch(`${API_BASE_URL}/replan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    throw new Error(`Replanning failed: ${res.statusText}`);
  }

  return await res.json();
}

export async function confirmRoute(proposalId: string, accepted: boolean): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/confirm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      proposal_id: proposalId,
      accepted
    })
  });

  if (!res.ok) {
    throw new Error(`Confirmation failed: ${res.statusText}`);
  }

  return await res.json();
}

// Persona T5 Tourist APIs
export async function getTouristAttractions(): Promise<TouristAttraction[]> {
  const res = await fetch(`${API_BASE_URL}/tourist/attractions`);
  if (!res.ok) {
    throw new Error('Failed to fetch attractions');
  }
  return await res.json();
}

export async function planTouristDay(
  startLocationName: string,
  selectedStops: TouristAttraction[],
  startTime: string = '09:30',
  curfewDeadline: string = '20:00',
  budgetInr: number = 100,
  budgetMode: string = 'LOWEST_COST'
): Promise<TourPlanResponse> {
  const payload = {
    start_location_name: startLocationName,
    stops: selectedStops.map(s => ({
      id: s.id,
      name: s.name,
      lat: s.lat,
      lon: s.lon,
      open_time: s.open_time,
      close_time: s.close_time,
      dwell_minutes: s.typical_dwell_minutes || 45,
      priority: s.priority || 'MEDIUM',
      fare_inr: s.fare_inr || 0
    })),
    start_time: startTime,
    curfew_deadline: curfewDeadline,
    budget_inr: budgetInr,
    budget_mode: budgetMode
  };

  const res = await fetch(`${API_BASE_URL}/tourist/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    throw new Error('Tourist plan calculation failed');
  }

  return await res.json();
}

export async function replanTouristDay(
  currentPlan: TourPlanResponse,
  severity: string = 'HIGH'
): Promise<TourPlanResponse> {
  const payload = {
    current_plan: currentPlan,
    disrupted_location: 'South Mumbai Heritage Corridor',
    delay_severity: severity,
    confirmed: true
  };

  const res = await fetch(`${API_BASE_URL}/tourist/replan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    throw new Error('Tourist replanning failed');
  }

  return await res.json();
}

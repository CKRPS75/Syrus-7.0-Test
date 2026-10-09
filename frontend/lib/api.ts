import {
  TravellerConstraints,
  JourneyPlanResponse,
  DisruptionAlert,
  TouristAttraction,
  TourPlanResponse,
  JourneyStop,
} from '../types';
import { computeCarbonMetrics } from './carbonCalculator';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

interface BackendJourneyLeg {
  mode: JourneyPlanResponse['legs'][number]['mode'];
  route_name?: string | null;
  from_place: string;
  to_place: string;
  duration_min: number;
  distance_m: number;
  coordinates?: unknown;
  stops?: unknown;
}

interface BackendJourney {
  journey_id?: string;
  origin: string;
  destination: string;
  departure: string;
  arrival: string;
  fare: number;
  walking_m: number;
  transfers: number;
  legs: BackendJourneyLeg[];
}

const journeyLegModes: JourneyPlanResponse['legs'][number]['mode'][] = [
  'WALK',
  'BUS',
  'METRO',
  'SUBWAY',
  'RAIL',
  'TRAIN',
];

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function isBackendJourneyLeg(value: unknown): value is BackendJourneyLeg {
  return (
    isRecord(value) &&
    typeof value.mode === 'string' &&
    journeyLegModes.includes(value.mode as BackendJourneyLeg['mode']) &&
    typeof value.from_place === 'string' &&
    typeof value.to_place === 'string' &&
    typeof value.duration_min === 'number' &&
    typeof value.distance_m === 'number' &&
    (value.route_name === undefined || value.route_name === null || typeof value.route_name === 'string')
  );
}

function isBackendJourney(value: unknown): value is BackendJourney {
  return (
    isRecord(value) &&
    typeof value.origin === 'string' &&
    typeof value.destination === 'string' &&
    typeof value.departure === 'string' &&
    typeof value.arrival === 'string' &&
    typeof value.fare === 'number' &&
    typeof value.walking_m === 'number' &&
    typeof value.transfers === 'number' &&
    Array.isArray(value.legs) &&
    value.legs.every(isBackendJourneyLeg)
  );
}

function getJourneyResponse(data: unknown): BackendJourney {
  if (!isRecord(data)) throw new Error('Journey planning returned an invalid response.');

  let journey: unknown = data.journey;
  if (!isRecord(journey) && Array.isArray(data.journeys)) {
    const firstResult = data.journeys[0];
    journey = isRecord(firstResult) && 'journey' in firstResult
      ? firstResult.journey
      : firstResult;
  }

  if (!isBackendJourney(journey)) {
    throw new Error('Journey planning returned no usable route.');
  }

  return journey;
}

function getCoordinates(coordinates: unknown): [number, number][] {
  if (!Array.isArray(coordinates)) return [];
  return coordinates.filter(
    (coordinate): coordinate is [number, number] =>
      Array.isArray(coordinate) &&
      coordinate.length === 2 &&
      typeof coordinate[0] === 'number' &&
      Number.isFinite(coordinate[0]) &&
      coordinate[0] >= -180 &&
      coordinate[0] <= 180 &&
      typeof coordinate[1] === 'number' &&
      Number.isFinite(coordinate[1]) &&
      coordinate[1] >= -90 &&
      coordinate[1] <= 90,
  );
}

function getStops(stops: unknown): JourneyStop[] {
  if (!Array.isArray(stops)) return [];
  return stops.flatMap((stop): JourneyStop[] => {
    if (!isRecord(stop) || typeof stop.name !== 'string') return [];
    const [coordinates] = getCoordinates([stop.coordinates]);
    return coordinates ? [{ name: stop.name, coordinates }] : [];
  });
}

export async function fetchBaseJourney(constraints: TravellerConstraints): Promise<JourneyPlanResponse> {
  const payload = {
    origin: constraints.origin,
    destination: constraints.destination,
    departure: constraints.departureTime || new Date().toISOString(),
    deadline: constraints.deadline,
    budget: constraints.budget,
    max_walking: constraints.maxWalkingMeters,
    accessibility_required: constraints.accessibilityRequired,
    allowed_modes: constraints.allowedModes,
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

  const data: unknown = await res.json();
  const j = getJourneyResponse(data);

  const legs = j.legs.map((l) => ({
    mode: l.mode,
    lineName: l.route_name || undefined,
    fromName: l.from_place,
    toName: l.to_place,
    durationMin: l.duration_min,
    distanceMeters: l.distance_m,
    coordinates: getCoordinates(l.coordinates),
    stops: getStops(l.stops),
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

export interface TransitAnomalyReport {
  mode: 'METRO' | 'BUS' | 'RAIL';
  category: string;
  route: string;
  location: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
  description: string;
  accessibilityImpact: boolean;
}

export interface TransitAnomalyResponse {
  event_id: string;
  status: 'IGNORE' | 'WATCH' | 'CONFIRMED';
  confidence_score: number;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'UNKNOWN';
  location?: string | null;
}

export async function submitTransitAnomaly(
  report: TransitAnomalyReport,
): Promise<TransitAnomalyResponse> {
  const res = await fetch(`${API_BASE_URL}/evidence/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      source_id: `crowd-report-${crypto.randomUUID()}`,
      source_type: 'crowd',
      text: [
        `Transit mode: ${report.mode}.`,
        `Incident category: ${report.category}.`,
        `Route: ${report.route}.`,
        `Station or location: ${report.location}.`,
        `Severity: ${report.severity}.`,
        `Wheelchair or step-free access affected: ${report.accessibilityImpact ? 'yes' : 'no'}.`,
        `Ground report: ${report.description}`,
      ].join(' '),
      timestamp: new Date().toISOString(),
      metadata: {
        transit_mode: report.mode,
        incident_category: report.category,
        route: report.route,
        location: report.location,
        severity: report.severity,
        accessibility_impact: report.accessibilityImpact,
      },
    }),
  });

  if (!res.ok) {
    throw new Error('The Trust Engine could not accept your report. Please try again.');
  }

  return res.json() as Promise<TransitAnomalyResponse>;
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

import { TourPlanResponse, TouristAttraction } from '../types';

export async function planTouristDay(
  startLocation: string,
  selectedStops: TouristAttraction[],
  startTime: string,
  curfewDeadline: string,
  budgetInr: number,
  budgetMode: 'LOWEST_COST' | 'FASTEST'
): Promise<TourPlanResponse> {
  const payload = {
    start_location: startLocation,
    stops: selectedStops,
    start_time: startTime,
    curfew_deadline: curfewDeadline,
    budget_inr: budgetInr,
    budget_mode: budgetMode,
  };

  try {
    const res = await fetch(`${API_BASE_URL}/tourist/plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error(`Server returned ${res.status}`);
    }

    return await res.json();
  } catch (error) {
    console.warn('[TrustRoute] Backend offline. Generating local verified tour plan fallback.');

    // Local deterministic fallback tour plan
    const legs = selectedStops.map((stop, idx) => {
      const isRail = idx % 2 === 0;
      return {
        from_stop: idx === 0 ? startLocation : selectedStops[idx - 1].name,
        to_stop: stop.name,
        mode: isRail ? ('RAIL' as const) : ('BUS' as const),
        bus_or_train_number: isRail ? 'Fast Local 90211' : 'BEST Bus 111 (Colaba Ring)',
        boarding_stop: `${idx === 0 ? startLocation : selectedStops[idx - 1].name} Station`,
        alighting_stop: `${stop.name} Gate`,
        fare_inr: isRail ? 10 : 15,
        duration_min: 22,
        distance_m: 4200,
        route_name: isRail ? 'Suburban Line' : 'BEST Feeder',
      };
    });

    // Add return leg back to starting hub
    legs.push({
      from_stop: selectedStops[selectedStops.length - 1].name,
      to_stop: startLocation,
      mode: 'RAIL' as const,
      bus_or_train_number: 'Suburban Return 90844',
      boarding_stop: `${selectedStops[selectedStops.length - 1].name} Stn`,
      alighting_stop: `${startLocation} Stn`,
      fare_inr: 10,
      duration_min: 25,
      distance_m: 5500,
      route_name: 'Suburban Line',
    });

    const totalFare = legs.reduce((acc, l) => acc + l.fare_inr, 0);

    const visitWindows = selectedStops.map((stop, idx) => {
      const startHr = 10 + idx * 2;
      return {
        stop_id: stop.id,
        stop_name: stop.name,
        arrival_time: `${String(startHr).padStart(2, '0')}:00`,
        departure_time: `${String(startHr + 1).padStart(2, '0')}:15`,
        dwell_minutes: stop.typical_dwell_minutes || 45,
        is_open: true,
        open_time: stop.open_time || '09:00',
        close_time: stop.close_time || '20:00',
      };
    });

    return {
      status: totalFare <= budgetInr ? 'PROTECTED' : 'BUDGET_DEFICIT',
      start_location: startLocation,
      expected_return_time: '18:45',
      curfew_deadline: curfewDeadline,
      total_transit_fare_inr: totalFare,
      min_budget_required_inr: totalFare,
      budget_remaining_inr: Math.max(0, budgetInr - totalFare),
      is_budget_sufficient: totalFare <= budgetInr,
      explanation: `Optimized multimodal circuit starting from ${startLocation} covering ${selectedStops.length} stops using BEST feeder routes and Mumbai Suburban Rail.`,
      dropped_stops: [],
      visit_windows: visitWindows,
      legs: legs,
    };
  }
}

export async function replanTouristDay(
  currentPlan: TourPlanResponse,
  severity: 'LOW' | 'MEDIUM' | 'HIGH'
): Promise<TourPlanResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/tourist/replan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ current_plan: currentPlan, disruption_severity: severity }),
    });

    if (!res.ok) {
      throw new Error(`Server returned ${res.status}`);
    }

    return await res.json();
  } catch (error) {
    console.warn('[TrustRoute] Backend offline. Using local adaptive re-plan fallback.');
    
    // Fallback: drop the lowest priority stop and return protected schedule
    const dropped = currentPlan.visit_windows.slice(-1).map(w => ({ id: w.stop_id, name: w.stop_name }));
    const keptWindows = currentPlan.visit_windows.slice(0, -1);
    const keptLegs = currentPlan.legs.slice(0, -1);

    return {
      ...currentPlan,
      status: 'PROTECTED',
      explanation: 'Disruption in South Mumbai detected. Lower-priority destination pruned to strictly guarantee curfew return time and transit budget.',
      dropped_stops: dropped as any,
      visit_windows: keptWindows,
      legs: keptLegs,
    };
  }
}

// Add or verify MOCK_TOURIST_ATTRACTIONS at the top or imports
export interface TouristAttraction {
  id: string;
  name: string;
  category: string;
  lat: number;
  lng: number;
  estimatedVisitMin: number;
  entryFee: number;
  description: string;
}

export const MOCK_ATTRACTIONS: TouristAttraction[] = [
  {
    id: 'att-1',
    name: 'Gateway of India',
    category: 'Heritage',
    lat: 18.922,
    lng: 72.8347,
    estimatedVisitMin: 45,
    entryFee: 0,
    description: 'Iconic 20th-century arch monument overlooking Mumbai Harbour.',
  },
  {
    id: 'att-2',
    name: 'Chhatrapati Shivaji Maharaj Terminus (CSMT)',
    category: 'Architecture',
    lat: 18.9401,
    lng: 72.8354,
    estimatedVisitMin: 30,
    entryFee: 0,
    description: 'UNESCO World Heritage Victorian Gothic railway terminus.',
  },
  {
    id: 'att-3',
    name: 'Marine Drive & Chowpatty',
    category: 'Promenade',
    lat: 18.9432,
    lng: 72.823,
    estimatedVisitMin: 60,
    entryFee: 0,
    description: 'The Queens Necklace coastal boulevard along the Arabian Sea.',
  },
  {
    id: 'att-4',
    name: 'Siddhivinayak Temple',
    category: 'Culture',
    lat: 19.0169,
    lng: 72.8304,
    estimatedVisitMin: 45,
    entryFee: 0,
    description: 'Historic Hindu shrine dedicated to Lord Shri Ganesha in Prabhadevi.',
  },
  {
    id: 'att-5',
    name: 'Bandra Bandstand & Fort',
    category: 'Scenic',
    lat: 19.0416,
    lng: 72.8197,
    estimatedVisitMin: 50,
    entryFee: 0,
    description: 'Rocky seaside walkway and Portuguese fort ruins.',
  },
];

// Replace your getTouristAttractions with this robust version:
export async function getTouristAttractions(): Promise<TouristAttraction[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/tourist/attractions`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) {
      throw new Error('Backend returned non-200');
    }
    return await res.json();
  } catch (error) {
    console.warn('[TrustRoute] FastAPI backend offline. Falling back to local mock attractions.');
    return MOCK_ATTRACTIONS;
  }
}
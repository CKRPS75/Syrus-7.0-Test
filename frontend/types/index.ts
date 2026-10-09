export type DisruptionStatus = 'IGNORE' | 'WATCH' | 'CONFIRMED' | 'RESOLVED';
export type TransitMode = 'BUS' | 'METRO' | 'TRAIN' | 'WALK';

export interface TravellerConstraints {
  origin: string;
  destination: string;
  departureTime: string;
  deadline?: string;
  budget?: number;
  maxWalkingMeters?: number;
  accessibilityRequired: boolean;
  allowedModes: TransitMode[];
}

export interface JourneyLeg {
  mode: 'WALK' | 'BUS' | 'METRO' | 'SUBWAY' | 'RAIL' | 'TRAIN';
  lineName?: string;
  fromName: string;
  toName: string;
  durationMin: number;
  distanceMeters: number;
  coordinates: [number, number][]; // [lng, lat]
  stops?: JourneyStop[];
}

export interface JourneyStop {
  name: string;
  coordinates: [number, number]; // [lng, lat]
}

export interface CarbonMetrics {
  co2EmittedGrams: number;
  co2SavedGrams: number;
  equivalentTreesPlantedDays?: number;
  cabComparisonFare: number;
  moneySaved: number;
}

export interface JourneySummary {
  origin: string;
  destination: string;
  departureTime: string;
  arrivalTime: string;
  fare: number;
  walkingMeters: number;
  transfers: number;
  status: 'OPTIMAL' | 'PROTECTED' | 'DELAYED';
  carbon?: CarbonMetrics;
}

export interface JourneyPlanResponse {
  journeyId: string;
  summary: JourneySummary;
  legs: JourneyLeg[];
}

export interface DisruptionAlert {
  eventId: string;
  title: string;
  status: DisruptionStatus;
  confidenceScore: number;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
  impactsCurrentRoute: boolean;
  affectedEntity: string;
  evidenceSources: string[];
  explanation: string;
  delayEstimateMin?: number;
}

// Persona T5 Tourist Types
export interface TouristAttraction {
  id: string;
  name: string;
  category: string;
  lat: number;
  lon: number;
  open_time: string;
  close_time: string;
  typical_dwell_minutes: number;
  priority: 'HIGH' | 'MEDIUM' | 'LOW' | 'FIXED';
  fare_inr: number;
  description: string;
}

export interface PlannedTourLeg {
  from_stop: string;
  to_stop: string;
  mode: string;
  route_name?: string;
  bus_or_train_number: string;
  boarding_stop: string;
  alighting_stop: string;
  distance_m: number;
  duration_min: number;
  fare_inr: number;
  departure_time: string;
  arrival_time: string;
}

export interface PlannedVisitWindow {
  stop_id: string;
  stop_name: string;
  arrival_time: string;
  departure_time: string;
  dwell_minutes: number;
  open_time: string;
  close_time: string;
  is_open: boolean;
  priority: string;
  ticket_fare_inr?: number;
}

export interface TourPlanResponse {
  status: 'FEASIBLE' | 'PROTECTED' | 'BUDGET_DEFICIT' | 'INFEASIBLE';
  start_location: string;
  budget_mode: string;
  total_stops_visited: number;
  total_travel_time_min: number;
  total_dwell_time_min: number;
  start_time: string;
  curfew_deadline: string;
  expected_return_time: string;
  slack_buffer_minutes: number;
  min_budget_required_inr: number;
  total_transit_fare_inr: number;
  total_ticket_fare_inr: number;
  total_fare_inr: number;
  budget_remaining_inr: number;
  is_budget_sufficient: boolean;
  total_walking_m: number;
  legs: PlannedTourLeg[];
  visit_windows: PlannedVisitWindow[];
  dropped_stops: TouristAttraction[];
  reordered: boolean;
  explanation: string;
}
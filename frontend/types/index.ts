export type DisruptionStatus = 'IGNORE' | 'WATCH' | 'CONFIRMED' | 'RESOLVED';

export interface TravellerConstraints {
  origin: string;
  destination: string;
  departureTime: string;
  deadline?: string;
  budget?: number;
  maxWalkingMeters?: number;
  accessibilityRequired: boolean;
  allowedModes: ('BUS' | 'METRO' | 'WALK')[];
}

export interface JourneyLeg {
  mode: 'WALK' | 'BUS' | 'METRO';
  lineName?: string;
  fromName: string;
  toName: string;
  durationMin: number;
  distanceMeters: number;
  coordinates: [number, number][]; // [lng, lat]
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
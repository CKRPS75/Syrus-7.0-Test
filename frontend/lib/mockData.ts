import { JourneyPlanResponse, DisruptionAlert } from '../types';

export const MOCK_BASE_JOURNEY: JourneyPlanResponse = {
  journeyId: 'j-mumbai-001',
  summary: {
    origin: 'Chembur',
    destination: 'Andheri',
    departureTime: '17:00',
    arrivalTime: '18:20',
    fare: 45,
    walkingMeters: 900,
    transfers: 1,
    status: 'OPTIMAL',
    carbon: {
      co2EmittedGrams: 485,
      co2SavedGrams: 2120, // 2.12 kg CO2 saved vs single-occupancy cab
      cabComparisonFare: 345,
      moneySaved: 300,
    },
  },
  legs: [
    {
      mode: 'WALK',
      fromName: 'Home (Chembur Naka)',
      toName: 'Chembur Bus Depot',
      durationMin: 6,
      distanceMeters: 400,
      coordinates: [
        [72.8985, 19.0622],
        [72.8955, 19.0645],
      ],
    },
    {
      mode: 'BUS',
      lineName: 'BEST Bus 365',
      fromName: 'Chembur Bus Depot',
      toName: 'Ghatkopar Station West',
      durationMin: 24,
      distanceMeters: 4500,
      coordinates: [
        [72.8955, 19.0645],
        [72.9082, 19.0863],
      ],
    },
    {
      mode: 'METRO',
      lineName: 'Metro Line 1 (Blue Line)',
      fromName: 'Ghatkopar Metro',
      toName: 'Andheri Metro',
      durationMin: 21,
      distanceMeters: 11400,
      coordinates: [
        [72.9082, 19.0863],
        [72.8467, 19.1197],
      ],
    },
    {
      mode: 'WALK',
      fromName: 'Andheri Station East',
      toName: 'Office / Destination',
      durationMin: 7,
      distanceMeters: 500,
      coordinates: [
        [72.8467, 19.1197],
        [72.8422, 19.1215],
      ],
    },
  ],
};

// Scenario A: Real Confirmed Disruption Impacting Route (USP 1, 3, 5)
export const SCENARIO_CONFIRMED: DisruptionAlert = {
  eventId: 'EVT-M1-409',
  title: 'Metro Line 1 Signal Interlocking Breakdown',
  status: 'CONFIRMED',
  confidenceScore: 0.88,
  severity: 'HIGH',
  impactsCurrentRoute: true,
  affectedEntity: 'Metro Line 1 (Ghatkopar - Andheri)',
  evidenceSources: [
    'Official Mumbai Metro Advisory (Status: Suspended)',
    '3 Independent verified crowd reports (< 12 mins)',
    'GDELT Event Index: Rail disruption reported at Saki Naka',
  ],
  explanation:
    'Multiple verified evidence sources corroborate an active power failure. Expected delay is ~35 mins, violating your 19:00 deadline buffer. Replan proposal triggered.',
  delayEstimateMin: 35,
};

// Scenario B: Unconfirmed / False Rumor (USP 1: Weighs evidence, not rumors)
export const SCENARIO_WATCH_RUMOR: DisruptionAlert = {
  eventId: 'EVT-CROWD-991',
  title: 'Unverified Crowd Rumor: Bus 365 Traffic Halt',
  status: 'WATCH',
  confidenceScore: 0.42,
  severity: 'LOW',
  impactsCurrentRoute: true,
  affectedEntity: 'Chembur Naka Roadway',
  evidenceSources: [
    '1 Unverified Single Crowd Report (No photo / no second source)',
    'Zero matching official alerts',
    'Crowd evidence capped at +2.6 (cannot confirm alone)',
  ],
  explanation:
    'Confidence score is 42% (below the 65% confirmation threshold). In accordance with USP 1, weak evidence generates a warning only. No automatic rerouting was triggered.',
  delayEstimateMin: 8,
};

// Scenario C: Real Confirmed Disruption, but Irrelevant to Traveller (USP 2: Impact on YOU)
export const SCENARIO_IRRELEVANT: DisruptionAlert = {
  eventId: 'EVT-WEST-012',
  title: 'Confirmed Closure: Western Railway Bandra Slow Line',
  status: 'CONFIRMED',
  confidenceScore: 0.94,
  severity: 'HIGH',
  impactsCurrentRoute: false,
  affectedEntity: 'Western Suburban Line (Bandra)',
  evidenceSources: [
    'Western Railway Official Alert',
    '6 Independent crowd reports',
    'Local news corroboration',
  ],
  explanation:
    'Disruption is 100% verified, but the Impact Engine determined your journey uses Metro Line 1 & Bus 365. Your specific itinerary is unaffected; no replanning is required.',
  delayEstimateMin: 40,
};

// Alternative Journey: Constraint-checked alternative
export const MOCK_ALTERNATIVE_JOURNEY: JourneyPlanResponse = {
  journeyId: 'j-mumbai-002-replan',
  summary: {
    origin: 'Chembur',
    destination: 'Andheri',
    departureTime: '17:00',
    arrivalTime: '18:48',
    fare: 55,
    walkingMeters: 850,
    transfers: 2,
    status: 'PROTECTED',
    carbon: {
      co2EmittedGrams: 610,
      co2SavedGrams: 1980, // 1.98 kg CO2 saved
      cabComparisonFare: 360,
      moneySaved: 305,
    },
  },
  legs: [
    {
      mode: 'WALK',
      fromName: 'Home (Chembur Naka)',
      toName: 'Chembur Monorail Station',
      durationMin: 5,
      distanceMeters: 350,
      coordinates: [
        [72.8985, 19.0622],
        [72.8965, 19.061],
      ],
    },
    {
      mode: 'BUS',
      lineName: 'BEST AC Fast Bus C-505',
      fromName: 'Chembur',
      toName: 'BKC Connector Interchange',
      durationMin: 28,
      distanceMeters: 6200,
      coordinates: [
        [72.8965, 19.061],
        [72.8682, 19.0657],
      ],
    },
    {
      mode: 'BUS',
      lineName: 'BEST Bus 340',
      fromName: 'BKC Connector',
      toName: 'Andheri Station East',
      durationMin: 32,
      distanceMeters: 7800,
      coordinates: [
        [72.8682, 19.0657],
        [72.8467, 19.1197],
      ],
    },
    {
      mode: 'WALK',
      fromName: 'Andheri Station East',
      toName: 'Office / Destination',
      durationMin: 7,
      distanceMeters: 500,
      coordinates: [
        [72.8467, 19.1197],
        [72.8422, 19.1215],
      ],
    },
  ],
};
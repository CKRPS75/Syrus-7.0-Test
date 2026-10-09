import { JourneyPlanResponse, DisruptionAlert } from '@/types';

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
  },
  legs: [
    {
      mode: 'WALK',
      fromName: 'Home (Chembur)',
      toName: 'Chembur Naka Bus Stop',
      durationMin: 6,
      distanceMeters: 400,
      coordinates: [
        [72.8985, 19.0622],
        [72.8955, 19.0645],
      ],
    },
    {
      mode: 'BUS',
      lineName: 'Bus 365',
      fromName: 'Chembur Naka',
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
      fromName: 'Andheri Metro Station',
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

export const MOCK_DISRUPTION_ALERT: DisruptionAlert = {
  eventId: 'EVT-M1-409',
  title: 'Metro Line 1 Major Signal Delay',
  status: 'CONFIRMED',
  confidenceScore: 0.88,
  severity: 'HIGH',
  impactsCurrentRoute: true,
  affectedEntity: 'Metro Line 1 (Ghatkopar - Andheri)',
  evidenceSources: [
    'Official Mumbai Metro Advisory (Status: Active Delay)',
    '3 Independent verified crowd reports (< 15 mins)',
    'Local Mobility News (GDELT feed indexed)',
  ],
  explanation:
    'Multiple verified reports confirm technical failure at Ghatkopar interlocking. Trains delayed up to 35 mins. Your planned 17:35 connection will be missed.',
  delayEstimateMin: 35,
};

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
  },
  legs: [
    {
      mode: 'WALK',
      fromName: 'Home (Chembur)',
      toName: 'Chembur Mono Station',
      durationMin: 5,
      distanceMeters: 350,
      coordinates: [
        [72.8985, 19.0622],
        [72.8965, 19.061],
      ],
    },
    {
      mode: 'BUS',
      lineName: 'AC Fast Bus C-505',
      fromName: 'Chembur',
      toName: 'Bandra Kurla Complex (BKC)',
      durationMin: 28,
      distanceMeters: 6200,
      coordinates: [
        [72.8965, 19.061],
        [72.8682, 19.0657],
      ],
    },
    {
      mode: 'BUS',
      lineName: 'Western Express Bus 340',
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
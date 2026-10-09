import { afterEach, describe, expect, it, vi } from 'vitest';
import { fetchBaseJourney } from './api';
import { TravellerConstraints } from '../types';

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('fetchBaseJourney', () => {
  it('sends selected transit modes and all trip constraints to the journey API', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({
        journey: {
          journey_id: 'OTP-001',
          origin: 'Chembur',
          destination: 'Andheri',
          departure: '2026-10-10T17:00:00+05:30',
          arrival: '2026-10-10T18:00:00+05:30',
          fare: 45,
          walking_m: 350,
          transfers: 1,
          legs: [{
            mode: 'RAIL',
            route_name: 'Western Line',
            from_place: 'Chembur',
            to_place: 'Andheri',
            duration_min: 45,
            distance_m: 18000,
            coordinates: [[72.9082, 19.0863], [72.8467, 19.1197]],
            stops: [
              { name: 'Ghatkopar', coordinates: [72.9082, 19.0863] },
              { name: 'Andheri', coordinates: [72.8467, 19.1197] },
            ],
          }],
        },
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );
    vi.stubGlobal('fetch', fetchMock);
    const constraints: TravellerConstraints = {
      origin: 'Chembur',
      destination: 'Andheri',
      departureTime: '17:00',
      deadline: '19:00',
      budget: 80,
      maxWalkingMeters: 1000,
      accessibilityRequired: true,
      allowedModes: ['BUS', 'METRO', 'TRAIN', 'WALK'],
    };

    await expect(fetchBaseJourney(constraints)).resolves.toMatchObject({
      legs: [{
        mode: 'RAIL',
        lineName: 'Western Line',
        stops: [
          { name: 'Ghatkopar', coordinates: [72.9082, 19.0863] },
          { name: 'Andheri', coordinates: [72.8467, 19.1197] },
        ],
      }],
    });
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({
      origin: 'Chembur',
      destination: 'Andheri',
      departure: '17:00',
      deadline: '19:00',
      budget: 80,
      max_walking: 1000,
      accessibility_required: true,
      allowed_modes: ['BUS', 'METRO', 'TRAIN', 'WALK'],
      forbidden_modes: [],
    });
  });

  it('accepts the journeys response envelope returned by the primary backend', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(
      new Response(JSON.stringify({
        journeys: [{
          journey: {
            journey_id: 'OTP-002',
            origin: 'Chembur',
            destination: 'Andheri',
            departure: '17:00',
            arrival: '18:00',
            fare: 50,
            walking_m: 250,
            transfers: 1,
            legs: [{
              mode: 'BUS',
              from_place: 'Chembur',
              to_place: 'Andheri',
              duration_min: 60,
              distance_m: 10000,
              coordinates: [[72.89, 19.06], [72.84, 19.12]],
              stops: [
                { name: 'Stop 1', coordinates: [72.89, 19.06] },
                { name: 'Stop 2', coordinates: [72.84, 19.12] },
              ],
            }],
          },
          constraint_check: { feasible: true },
        }],
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    ));

    await expect(fetchBaseJourney({
      origin: 'Chembur',
      destination: 'Andheri',
      departureTime: '17:00',
      accessibilityRequired: false,
      allowedModes: ['BUS'],
    })).resolves.toMatchObject({
      journeyId: 'OTP-002',
      legs: [{
        mode: 'BUS',
        coordinates: [[72.89, 19.06], [72.84, 19.12]],
        stops: [
          { name: 'Stop 1', coordinates: [72.89, 19.06] },
          { name: 'Stop 2', coordinates: [72.84, 19.12] },
        ],
      }],
    });
  });
});

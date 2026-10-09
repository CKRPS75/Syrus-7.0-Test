import { describe, expect, it } from 'vitest';
import { JourneyLeg } from '../types';
import { createRouteFeatureCollection } from './mapRouteData';
import { MOCK_BASE_JOURNEY } from './mockData';

describe('createRouteFeatureCollection', () => {
  it('places WALK, BUS, and METRO markers at their actual stop coordinates', () => {
    const legs = MOCK_BASE_JOURNEY.legs.slice(0, 3);
    const collection = createRouteFeatureCollection(legs);
    const markers = collection.features.filter((feature) => feature.geometry.type === 'Point');

    expect(markers).toHaveLength(6);
    expect(markers.map((marker) => marker.properties?.color)).toEqual([
      '#334155',
      '#334155',
      '#16a34a',
      '#16a34a',
      '#0284c7',
      '#0284c7',
    ]);
    const coordinates = markers.map((marker) =>
      (marker.geometry as GeoJSON.Point).coordinates,
    );
    expect(coordinates).toEqual([
      [72.8985, 19.0622],
      [72.8955, 19.0645],
      [72.8955, 19.0645],
      [72.9082, 19.0863],
      [72.9082, 19.0863],
      [72.8467, 19.1197],
    ]);
  });

  it('uses actual intermediate transit stops supplied by the routing response', () => {
    const leg: JourneyLeg = {
      mode: 'METRO',
      fromName: 'Station A',
      toName: 'Station C',
      durationMin: 10,
      distanceMeters: 1000,
      coordinates: [[72.8, 19.0], [72.9, 19.1]],
      stops: [
        { name: 'Station A', coordinates: [72.8, 19.0] },
        { name: 'Station B', coordinates: [72.85, 19.05] },
        { name: 'Station C', coordinates: [72.9, 19.1] },
      ],
    };
    const markers = createRouteFeatureCollection([leg]).features.filter((feature) => feature.geometry.type === 'Point');

    expect(markers.map((marker) => marker.properties?.stopName)).toEqual([
      'Station A',
      'Station B',
      'Station C',
    ]);
    expect(markers.map((marker) => (marker.geometry as GeoJSON.Point).coordinates)).toEqual([
      [72.8, 19.0],
      [72.85, 19.05],
      [72.9, 19.1],
    ]);
  });

  it('uses indigo for rail and ignores legs without valid coordinates', () => {
    const legs: JourneyLeg[] = [
      {
        mode: 'RAIL',
        fromName: 'Station A',
        toName: 'Station B',
        durationMin: 10,
        distanceMeters: 1000,
        coordinates: [[72.8, 19.0], [72.9, 19.1]],
      },
      {
        mode: 'TRAIN',
        fromName: 'Station B',
        toName: 'Station C',
        durationMin: 10,
        distanceMeters: 1000,
        coordinates: [],
      },
      {
        mode: 'BUS',
        fromName: 'Station C',
        toName: 'Station D',
        durationMin: 10,
        distanceMeters: 1000,
        coordinates: [[0, 0], [Number.NaN, 19]],
      },
      {
        mode: 'METRO',
        fromName: 'Station D',
        toName: 'Station E',
        durationMin: 10,
        distanceMeters: 1000,
        coordinates: [[null, 19], [72.9, 19.1]] as unknown as [number, number][],
      },
    ];
    const collection = createRouteFeatureCollection(legs);
    const markers = collection.features.filter((feature) => feature.geometry.type === 'Point');

    expect(markers).toHaveLength(2);
    expect(markers.every((marker) => marker.properties?.color === '#4f46e5')).toBe(true);
    expect(collection.features.some((feature) =>
      feature.geometry.type === 'Point' &&
      (feature.geometry as GeoJSON.Point).coordinates.includes(0),
    )).toBe(false);
  });
});

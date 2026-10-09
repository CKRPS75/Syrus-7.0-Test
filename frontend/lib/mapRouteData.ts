import { JourneyLeg } from '../types';

export const ROUTE_MODE_COLORS: Record<JourneyLeg['mode'], string> = {
  WALK: '#334155',
  BUS: '#16a34a',
  METRO: '#0284c7',
  SUBWAY: '#0284c7',
  RAIL: '#4f46e5',
  TRAIN: '#4f46e5',
};

export interface RouteFeatureProperties {
  mode: JourneyLeg['mode'];
  color: string;
  stopName?: string;
}

function isValidCoordinate(coordinate: unknown): coordinate is [number, number] {
  if (
    !Array.isArray(coordinate) ||
    coordinate.length !== 2 ||
    typeof coordinate[0] !== 'number' ||
    typeof coordinate[1] !== 'number'
  ) {
    return false;
  }

  const [longitude, latitude] = coordinate;
  return (
    Number.isFinite(longitude) &&
    Number.isFinite(latitude) &&
    longitude >= -180 &&
    longitude <= 180 &&
    latitude >= -90 &&
    latitude <= 90
  );
}

export function createRouteFeatureCollection(
  legs: JourneyLeg[],
): GeoJSON.FeatureCollection<GeoJSON.Geometry, RouteFeatureProperties> {
  const features: GeoJSON.Feature<GeoJSON.Geometry, RouteFeatureProperties>[] = [];

  legs.forEach((leg, index) => {
    const coordinates = leg.coordinates;
    if (!Array.isArray(coordinates) || !coordinates.length || !coordinates.every(isValidCoordinate)) return;

    const properties = {
      mode: leg.mode,
      color: ROUTE_MODE_COLORS[leg.mode],
    };

    if (coordinates.length >= 2) {
      features.push({
        type: 'Feature',
        id: `leg-${index}`,
        properties,
        geometry: {
          type: 'LineString',
          coordinates,
        },
      });
    }

    const stops = leg.stops?.length
      ? leg.stops
      : [
          { name: leg.fromName, coordinates: coordinates[0] },
          ...(coordinates.length > 1
            ? [{ name: leg.toName, coordinates: coordinates[coordinates.length - 1] }]
            : []),
        ];

    stops.forEach((stop, stopIndex) => {
      if (!isValidCoordinate(stop.coordinates)) return;
      features.push({
        type: 'Feature',
        id: `leg-${index}-stop-${stopIndex}`,
        properties: { ...properties, stopName: stop.name },
        geometry: {
          type: 'Point',
          coordinates: stop.coordinates,
        },
      });
    });
  });

  return {
    type: 'FeatureCollection',
    features,
  };
}

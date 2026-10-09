'use client';

import React, { useEffect, useRef } from 'react';
import { Map, LngLatBounds } from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { JourneyLeg } from '../types';

interface MapViewProps {
  legs: JourneyLeg[];
}

export default function MapView({ legs }: MapViewProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<Map | null>(null);

  useEffect(() => {
    if (!mapContainer.current) return;

    if (!mapInstance.current) {
      mapInstance.current = new Map({
        container: mapContainer.current,
        style: {
          version: 8,
          sources: {
            'osm-tiles': {
              type: 'raster',
              tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
              tileSize: 256,
              attribution: '&copy; OpenStreetMap contributors',
            },
          },
          layers: [
            {
              id: 'osm-tiles-layer',
              type: 'raster',
              source: 'osm-tiles',
              minzoom: 0,
              maxzoom: 19,
            },
          ],
        },
        center: [72.8777, 19.076], // Mumbai center
        zoom: 11,
      });
    }

    const map = mapInstance.current;

    const updateRouteData = () => {
      if (!legs || legs.length === 0) return;

      const validFeatures = legs
        .filter((leg) => leg.coordinates && leg.coordinates.length >= 2)
        .map((leg, idx) => ({
          type: 'Feature' as const,
          properties: {
            id: `leg-${idx}`,
            mode: leg.mode,
            color:
              leg.mode === 'METRO'
                ? '#0284c7'
                : leg.mode === 'BUS'
                ? '#16a34a'
                : '#64748b',
          },
          geometry: {
            type: 'LineString' as const,
            coordinates: leg.coordinates,
          },
        }));

      const geojsonData: GeoJSON.FeatureCollection = {
        type: 'FeatureCollection',
        features: validFeatures,
      };

      const source = map.getSource('trustroute-paths') as any;

      if (source && typeof source.setData === 'function') {
        source.setData(geojsonData);
      } else if (!source) {
        map.addSource('trustroute-paths', {
          type: 'geojson',
          data: geojsonData,
        });

        map.addLayer({
          id: 'route-line-layer',
          type: 'line',
          source: 'trustroute-paths',
          layout: {
            'line-join': 'round',
            'line-cap': 'round',
          },
          paint: {
            'line-color': ['get', 'color'],
            'line-width': ['case', ['==', ['get', 'mode'], 'WALK'], 3, 5],
          },
        });
      }

      const allCoords = legs.flatMap((l) => l.coordinates);
      if (allCoords.length > 0) {
        const bounds = allCoords.reduce(
          (b, coord) => b.extend(coord),
          new LngLatBounds(allCoords[0], allCoords[0])
        );
        map.fitBounds(bounds, { padding: 45, maxZoom: 14 });
      }
    };

    if (map.isStyleLoaded()) {
      updateRouteData();
    } else {
      map.once('load', updateRouteData);
    }
  }, [legs]);

  return (
    <div className="relative w-full h-80 rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-800 shadow-sm">
      <div ref={mapContainer} className="w-full h-full" />
      <div className="absolute top-3 right-3 bg-white/95 dark:bg-slate-900/90 backdrop-blur px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 text-xs flex gap-3 shadow-md font-semibold text-slate-800 dark:text-slate-200">
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-slate-500 inline-block" /> Walk
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-green-600 inline-block" /> Bus
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-sky-600 inline-block" /> Metro
        </span>
      </div>
    </div>
  );
}
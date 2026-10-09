'use client';

import React, { useEffect, useRef } from 'react';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { JourneyLeg } from '../types';

// Explicitly set the worker URL to MapLibre's unpkg CDN worker to prevent local bundler worker failures
// @ts-ignore
if (typeof window !== 'undefined' && maplibregl.setWorkerUrl) {
  // @ts-ignore
  maplibregl.setWorkerUrl('https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl-csp-worker.js');
}

interface MapViewProps {
  legs: JourneyLeg[];
}

export default function MapView({ legs }: MapViewProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<maplibregl.Map | null>(null);

  useEffect(() => {
    if (!mapContainer.current) return;

    if (!mapInstance.current) {
      mapInstance.current = new maplibregl.Map({
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
        center: [72.8777, 19.076], // Mumbai coordinates
        zoom: 11,
      });
    }

    const map = mapInstance.current;

    const renderLayers = () => {
      if (!legs || legs.length === 0) return;

      const allCoordinates: [number, number][] = [];

      legs.forEach((leg, index) => {
        const sourceId = `route-leg-${index}`;
        const layerId = `layer-leg-${index}`;

        if (map.getSource(sourceId)) {
          if (map.getLayer(layerId)) {
            map.removeLayer(layerId);
          }
          map.removeSource(sourceId);
        }

        allCoordinates.push(...leg.coordinates);

        map.addSource(sourceId, {
          type: 'geojson',
          data: {
            type: 'Feature',
            properties: {},
            geometry: {
              type: 'LineString',
              coordinates: leg.coordinates,
            },
          },
        });

        const color =
          leg.mode === 'METRO'
            ? '#0284c7'
            : leg.mode === 'BUS'
            ? '#16a34a'
            : '#64748b';

        map.addLayer({
          id: layerId,
          type: 'line',
          source: sourceId,
          layout: {
            'line-join': 'round',
            'line-cap': 'round',
          },
          paint: {
            'line-color': color,
            'line-width': leg.mode === 'WALK' ? 3 : 5,
            'line-dasharray': leg.mode === 'WALK' ? [2, 2] : [1, 0],
          },
        });
      });

      if (allCoordinates.length > 0) {
        const bounds = allCoordinates.reduce(
          (b, coord) => b.extend(coord),
          new maplibregl.LngLatBounds(allCoordinates[0], allCoordinates[0])
        );
        map.fitBounds(bounds, { padding: 40 });
      }
    };

    if (map.isStyleLoaded()) {
      renderLayers();
    } else {
      map.once('load', renderLayers);
    }
  }, [legs]);

  return (
    <div className="relative w-full h-80 rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-800 shadow-sm">
      <div ref={mapContainer} className="w-full h-full" />
      <div className="absolute top-3 right-3 bg-white/90 dark:bg-slate-900/90 backdrop-blur px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 text-xs flex gap-3 shadow-sm font-semibold text-slate-800 dark:text-slate-200">
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-slate-500 inline-block" /> Walk[cite: 55, 56]
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-green-600 inline-block" /> Bus[cite: 55]
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-sky-600 inline-block" /> Metro[cite: 55]
        </span>
      </div>
    </div>
  );
}
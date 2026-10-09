'use client';

import React, { useEffect, useRef } from 'react';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { JourneyLeg } from '@/types';

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
        center: [72.8777, 19.076], // Mumbai default
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
          map.removeLayer(layerId);
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
    <div className="relative w-full h-80 rounded-xl overflow-hidden border border-slate-200 shadow-sm">
      <div ref={mapContainer} className="w-full h-full" />
      <div className="absolute top-3 right-3 bg-white/95 backdrop-blur px-3 py-1.5 rounded-lg border border-slate-200 text-xs flex gap-3 shadow-sm font-medium">
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
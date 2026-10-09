'use client';

import React, { useEffect, useRef } from 'react';
import { Map, LngLatBounds } from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { JourneyLeg } from '../types';
import { createRouteFeatureCollection } from '../lib/mapRouteData';

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
      const geojsonData = createRouteFeatureCollection(legs);

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

        map.addLayer({
          id: 'route-marker-layer',
          type: 'circle',
          source: 'trustroute-paths',
          filter: ['==', ['geometry-type'], 'Point'],
          paint: {
            'circle-radius': 12,
            'circle-color': ['get', 'color'],
            'circle-stroke-color': '#ffffff',
            'circle-stroke-width': 3,
            'circle-opacity': 1,
          },
        });
      }

      // Fit bounds cleanly
      const allCoords: [number, number][] = [];
      geojsonData.features.forEach((feature) => {
        const coordinates =
          feature.geometry.type === 'LineString'
            ? feature.geometry.coordinates
            : feature.geometry.type === 'Point'
              ? [feature.geometry.coordinates]
              : [];

        coordinates.forEach(([longitude, latitude]) => {
          if (
            Number.isFinite(longitude) &&
            Number.isFinite(latitude) &&
            longitude >= -180 &&
            longitude <= 180 &&
            latitude >= -90 &&
            latitude <= 90
          ) {
            allCoords.push([longitude, latitude]);
          }
        });
      });
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
          <span className="w-2.5 h-2.5 rounded-full bg-slate-700 inline-block" /> Walk
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-green-600 inline-block" /> Bus
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-sky-600 inline-block" /> Metro
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-indigo-600 inline-block" /> Rail
        </span>
      </div>
    </div>
  );
}
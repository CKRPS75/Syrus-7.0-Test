'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Map, Marker, LngLatBounds, setWorkerCount, setWorkerUrl } from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { JourneyLeg } from '../types';
import { ROUTE_MODE_COLORS } from '../lib/mapRouteData';

// Configure MapLibre Web Worker for Next.js Turbopack client rendering
if (typeof window !== 'undefined') {
  try {
    setWorkerUrl('/maplibre-gl-worker.mjs');
  } catch {}
}

interface MapViewProps {
  legs: JourneyLeg[];
}

export default function MapView({ legs }: MapViewProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const svgOverlayRef = useRef<SVGSVGElement>(null);
  const mapInstance = useRef<Map | null>(null);
  const markersRef = useRef<Marker[]>([]);
  const [mapReady, setMapReady] = useState(false);

  useEffect(() => {
    if (!mapContainer.current) return;

    if (!mapInstance.current) {
      try {
        const map = new Map({
          container: mapContainer.current,
          style: {
            version: 8,
            sources: {
              'osm-tiles': {
                type: 'raster',
                tiles: [
                  'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png',
                  'https://b.tile.openstreetmap.org/{z}/{x}/{y}.png',
                  'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png'
                ],
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

        map.on('load', () => {
          setMapReady(true);
        });

        mapInstance.current = map;
      } catch (err) {
        console.warn('MapLibre init notice:', err);
      }
    }

    return () => {
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];
    };
  }, []);

  useEffect(() => {
    const map = mapInstance.current;
    if (!map) return;

    const renderTransitRoute = () => {
      // 1. Clear previous DOM markers
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];

      // 2. Collect all valid coordinates for bounds fitting
      const allCoords: [number, number][] = [];
      const stopPoints: { name: string; mode: string; coord: [number, number]; isOrigin?: boolean; isDest?: boolean }[] = [];

      legs.forEach((leg, legIdx) => {
        const coords = leg.coordinates || [];

        coords.forEach((coord, coordIdx) => {
          if (Array.isArray(coord) && coord.length === 2 && !isNaN(coord[0]) && !isNaN(coord[1])) {
            allCoords.push(coord);

            // Register stop marker for start and end of each leg
            if (coordIdx === 0 && legIdx === 0) {
              stopPoints.push({
                name: leg.fromName,
                mode: leg.mode,
                coord,
                isOrigin: true,
              });
            } else if (coordIdx === coords.length - 1 && legIdx === legs.length - 1) {
              stopPoints.push({
                name: leg.toName,
                mode: leg.mode,
                coord,
                isDest: true,
              });
            } else if (coordIdx === 0 || coordIdx === coords.length - 1) {
              stopPoints.push({
                name: coordIdx === 0 ? leg.fromName : leg.toName,
                mode: leg.mode,
                coord,
              });
            }
          }
        });
      });

      // 3. Attach custom HTML DOM Markers for each transit stop / hub
      stopPoints.forEach((stop) => {
        const color = ROUTE_MODE_COLORS[stop.mode as keyof typeof ROUTE_MODE_COLORS] || '#4f46e5';
        
        const el = document.createElement('div');
        el.className = 'group relative cursor-pointer flex items-center justify-center';
        
        // Marker badge styling
        if (stop.isOrigin) {
          el.innerHTML = `
            <div class="relative flex items-center justify-center">
              <span class="animate-ping absolute inline-flex h-7 w-7 rounded-full bg-emerald-400 opacity-75"></span>
              <div class="w-6 h-6 rounded-full bg-emerald-600 border-2 border-white shadow-lg flex items-center justify-center text-white text-[10px] font-black">A</div>
              <div class="absolute -top-7 whitespace-nowrap bg-slate-900/90 text-white text-[10px] font-bold px-2 py-0.5 rounded-md shadow-md border border-slate-700 pointer-events-none">${stop.name}</div>
            </div>
          `;
        } else if (stop.isDest) {
          el.innerHTML = `
            <div class="relative flex items-center justify-center">
              <span class="animate-ping absolute inline-flex h-7 w-7 rounded-full bg-rose-400 opacity-75"></span>
              <div class="w-6 h-6 rounded-full bg-rose-600 border-2 border-white shadow-lg flex items-center justify-center text-white text-[10px] font-black">B</div>
              <div class="absolute -top-7 whitespace-nowrap bg-slate-900/90 text-white text-[10px] font-bold px-2 py-0.5 rounded-md shadow-md border border-slate-700 pointer-events-none">${stop.name}</div>
            </div>
          `;
        } else {
          el.innerHTML = `
            <div class="relative flex items-center justify-center">
              <div class="w-3.5 h-3.5 rounded-full border-2 border-white shadow-md flex items-center justify-center" style="background-color: ${color}"></div>
              <div class="absolute -top-6 whitespace-nowrap bg-white/95 dark:bg-slate-900/95 text-slate-800 dark:text-slate-200 text-[9px] font-bold px-1.5 py-0.5 rounded shadow border border-slate-200 dark:border-slate-800 opacity-90">${stop.name}</div>
            </div>
          `;
        }

        try {
          const marker = new Marker({ element: el })
            .setLngLat(stop.coord)
            .addTo(map);
          markersRef.current.push(marker);
        } catch {
          // Ignore marker attachment fallback
        }
      });

      // 4. Update SVG overlay polyline for synchronous crisp rendering
      const updateSvgPaths = () => {
        if (!svgOverlayRef.current || !map) return;
        const svg = svgOverlayRef.current;
        while (svg.firstChild) {
          svg.removeChild(svg.firstChild);
        }

        legs.forEach((leg) => {
          const coords = leg.coordinates || [];
          if (coords.length < 2) return;
          const color = ROUTE_MODE_COLORS[leg.mode as keyof typeof ROUTE_MODE_COLORS] || '#4f46e5';
          const points = coords.map((c) => {
            const p = map.project([c[0], c[1]]);
            return `${p.x},${p.y}`;
          }).join(' ');

          const polyline = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
          polyline.setAttribute('points', points);
          polyline.setAttribute('stroke', color);
          polyline.setAttribute('stroke-width', leg.mode === 'WALK' ? '4' : '6');
          polyline.setAttribute('stroke-linecap', 'round');
          polyline.setAttribute('stroke-linejoin', 'round');
          polyline.setAttribute('stroke-opacity', '0.9');
          if (leg.mode === 'WALK') {
            polyline.setAttribute('stroke-dasharray', '6 6');
          }
          polyline.setAttribute('fill', 'none');
          svg.appendChild(polyline);
        });
      };

      updateSvgPaths();
      map.off('move', updateSvgPaths);
      map.off('zoom', updateSvgPaths);
      map.off('resize', updateSvgPaths);
      map.on('move', updateSvgPaths);
      map.on('zoom', updateSvgPaths);
      map.on('resize', updateSvgPaths);

      // 5. Fit bounds to route
      if (allCoords.length > 0) {
        try {
          const bounds = allCoords.reduce(
            (b, coord) => b.extend(coord),
            new LngLatBounds(allCoords[0], allCoords[0])
          );
          map.fitBounds(bounds, { padding: 50, maxZoom: 14 });
        } catch {
          // Fallback bounds
        }
      }
    };

    if (map.isStyleLoaded()) {
      renderTransitRoute();
    } else {
      map.once('load', renderTransitRoute);
    }
  }, [legs, mapReady]);

  return (
    <div className="relative w-full h-80 rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-800 shadow-sm">
      <div ref={mapContainer} className="w-full h-full" />
      <svg
        ref={svgOverlayRef}
        className="absolute inset-0 w-full h-full pointer-events-none z-[1]"
      />
      <div className="absolute top-3 right-3 bg-white/95 dark:bg-slate-900/90 backdrop-blur px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 text-xs flex gap-3 shadow-md font-semibold text-slate-800 dark:text-slate-200 z-10">
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
'use client';

import React, { useState, useEffect } from 'react';
import {
  TouristAttraction,
  TourPlanResponse,
  JourneyLeg
} from '../types';
import {
  getTouristAttractions,
  planTouristDay,
  replanTouristDay
} from '../lib/api';
import { computeCarbonMetrics } from '../lib/carbonCalculator';
import CarbonBadge from './CarbonBadge';
import {
  Compass,
  Clock,
  MapPin,
  AlertTriangle,
  CheckCircle,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Trash2,
  Plus,
  Bus,
  Train,
  IndianRupee,
  Wallet,
  AlertCircle
} from 'lucide-react';

// Verified Mumbai Dataset Hubs
const MUMBAI_DATASET_HUBS = [
  'Dadar',
  'Andheri',
  'Chembur',
  'Bandra',
  'Borivali',
  'Ghatkopar',
  'Kurla',
  'Sion',
  'Mulund',
  'CSMT',
  'Churchgate',
  'Colaba',
  'Versova',
  'BKC'
];

// Robust Fallback Tourist Attractions
const FALLBACK_ATTRACTIONS: TouristAttraction[] = [
  {
    id: 'GATEWAY_OF_INDIA',
    name: 'Gateway of India',
    category: 'Heritage',
    lat: 18.922,
    lng: 72.8347,
    typical_dwell_minutes: 45,
    open_time: '06:00',
    close_time: '23:00',
    fare_inr: 0,
    priority: 'HIGH',
    description: 'Iconic 20th-century basalt arch monument on Mumbai Harbour.'
  },
  {
    id: 'CSMVS_MUSEUM',
    name: 'CSMVS Museum (Prince of Wales)',
    category: 'Culture & Art',
    lat: 18.9269,
    lng: 72.8327,
    typical_dwell_minutes: 60,
    open_time: '10:15',
    close_time: '18:00',
    fare_inr: 150,
    priority: 'HIGH',
    description: 'Premier art and history museum in Indo-Saracenic architecture.'
  },
  {
    id: 'JEHANGIR_ART_GALLERY',
    name: 'Jehangir Art Gallery',
    category: 'Art',
    lat: 18.9275,
    lng: 72.8317,
    typical_dwell_minutes: 40,
    open_time: '11:00',
    close_time: '19:00',
    fare_inr: 0,
    priority: 'MEDIUM',
    description: 'Foremost modern Indian art gallery in Kala Ghoda.'
  },
  {
    id: 'MARINE_DRIVE',
    name: 'Marine Drive & Chowpatty',
    category: 'Scenic',
    lat: 18.9432,
    lng: 72.823,
    typical_dwell_minutes: 60,
    open_time: '00:00',
    close_time: '23:59',
    fare_inr: 0,
    priority: 'HIGH',
    description: "The Queen's Necklace coastal promenade along the Arabian Sea."
  },
  {
    id: 'SIDDHIVINAYAK_TEMPLE',
    name: 'Siddhivinayak Temple',
    category: 'Heritage',
    lat: 19.0169,
    lng: 72.8304,
    typical_dwell_minutes: 45,
    open_time: '05:30',
    close_time: '22:00',
    fare_inr: 0,
    priority: 'MEDIUM',
    description: 'Historic temple dedicated to Lord Ganesha in Prabhadevi.'
  },
  {
    id: 'BANDRA_BANDSTAND',
    name: 'Bandra Bandstand & Fort',
    category: 'Scenic',
    lat: 19.0416,
    lng: 72.8197,
    typical_dwell_minutes: 50,
    open_time: '06:00',
    close_time: '21:00',
    fare_inr: 0,
    priority: 'MEDIUM',
    description: 'Rocky seaside walkway and Portuguese fort ruins.'
  }
];

export default function TouristPlanner() {
  const [attractions, setAttractions] = useState<TouristAttraction[]>([]);
  const [selectedStops, setSelectedStops] = useState<TouristAttraction[]>([]);
  const [startLocation, setStartLocation] = useState('Dadar');
  const [startTime, setStartTime] = useState('09:00');
  const [curfewDeadline, setCurfewDeadline] = useState('20:00');
  const [budgetInr, setBudgetInr] = useState(100);
  const [budgetMode, setBudgetMode] = useState<'LOWEST_COST' | 'FASTEST'>('LOWEST_COST');
  const [plan, setPlan] = useState<TourPlanResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isReplanning, setIsReplanning] = useState(false);
  const [disruptionMsg, setDisruptionMsg] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await getTouristAttractions();
        const list = data && data.length > 0 ? data : FALLBACK_ATTRACTIONS;
        
        setAttractions(list);

        const defaults = list.filter((a) =>
          ['GATEWAY_OF_INDIA', 'CSMVS_MUSEUM', 'JEHANGIR_ART_GALLERY', 'MARINE_DRIVE'].includes(a.id)
        );

        setSelectedStops(defaults.length > 0 ? defaults : list.slice(0, 4));
      } catch (e) {
        console.warn('Backend unavailable, using Mumbai fallback attractions:', e);
        setAttractions(FALLBACK_ATTRACTIONS);
        setSelectedStops(FALLBACK_ATTRACTIONS.slice(0, 4));
      }
    }

    load();
  }, []);

  const handlePlanTour = async () => {
    if (selectedStops.length === 0) return;
    setIsLoading(true);
    setDisruptionMsg(null);
    try {
      const result = await planTouristDay(
        startLocation,
        selectedStops,
        startTime,
        curfewDeadline,
        budgetInr,
        budgetMode
      );
      setPlan(result);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSimulateDisruption = async () => {
    if (!plan) return;
    setIsReplanning(true);
    try {
      const replanned = await replanTouristDay(plan, 'HIGH');
      setPlan(replanned);
      setDisruptionMsg(
        '⚠ South Mumbai Corridor Congestion Detected. Adaptive reordering & budget preservation executed!'
      );
    } catch (e) {
      console.error(e);
    } finally {
      setIsReplanning(false);
    }
  };

  const addStop = (attr: TouristAttraction) => {
    if (!selectedStops.some(s => s.id === attr.id)) {
      setSelectedStops([...selectedStops, attr]);
    }
  };

  const removeStop = (id: string) => {
    setSelectedStops(selectedStops.filter(s => s.id !== id));
  };

  // Convert tour legs to JourneyLeg format for Carbon Calculator
  const tourCarbonMetrics = plan
    ? computeCarbonMetrics(
        plan.legs.map(l => {
          const mode: JourneyLeg['mode'] =
            l.mode === 'RAIL'
              ? 'RAIL'
              : l.mode === 'METRO'
                ? 'METRO'
                : l.mode === 'WALK'
                  ? 'WALK'
                  : 'BUS';

          return {
            fromName: l.from_stop,
            toName: l.to_stop,
            mode,
            durationMin: l.duration_min,
            distanceMeters: l.distance_m,
            coordinates: []
          };
        }),
        plan.total_transit_fare_inr
      )
    : undefined;

  return (
    <div className="space-y-6">
      {/* Configuration Form */}
      <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2.5">
            <div className="bg-amber-500 text-white p-2 rounded-xl">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 dark:text-white">Persona T5: Multi-Stop Day Optimizer</h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Verified Mumbai GTFS dataset routing (BEST Buses &amp; Suburban Rails) with official fare tables.
              </p>
            </div>
          </div>
          <span className="text-xs bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 font-semibold px-3 py-1 rounded-full border border-amber-200 dark:border-amber-800/60">
            Mumbai GTFS Verified
          </span>
        </div>

        {/* Start Location Input */}
        <div className="mb-5 space-y-2">
          <label className="text-xs font-bold text-slate-700 dark:text-slate-300 block">
            Select Your Starting Point in Mumbai (Dataset Verified Hubs):
          </label>
          <div className="flex flex-wrap gap-1.5 mb-2">
            {MUMBAI_DATASET_HUBS.map(hub => (
              <button
                key={hub}
                onClick={() => setStartLocation(hub)}
                className={`text-xs px-2.5 py-1 rounded-lg border font-medium transition ${
                  startLocation.toLowerCase() === hub.toLowerCase()
                    ? 'bg-indigo-600 text-white border-indigo-600 font-bold shadow-xs'
                    : 'bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700'
                }`}
              >
                {hub}
              </button>
            ))}
          </div>
          <input
            type="text"
            value={startLocation}
            onChange={e => setStartLocation(e.target.value)}
            placeholder="Or enter custom Mumbai location..."
            className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        {/* Times & Budget Settings */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-5">
          <div>
            <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 block mb-1">Departure Time</label>
            <input
              type="time"
              value={startTime}
              onChange={e => setStartTime(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-sm font-medium text-slate-800 dark:text-slate-100"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 block mb-1">Return Curfew / Deadline</label>
            <input
              type="time"
              value={curfewDeadline}
              onChange={e => setCurfewDeadline(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-sm font-medium text-slate-800 dark:text-slate-100"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 block mb-1">Allocated Budget (₹ INR)</label>
            <input
              type="number"
              min={10}
              value={budgetInr}
              onChange={e => setBudgetInr(Math.max(0, Number(e.target.value)))}
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-sm font-medium text-slate-800 dark:text-slate-100"
            />
          </div>
        </div>

        {/* Budget Mode Toggle with Official Pricing */}
        <div className="mb-5 p-3.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700/60 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Wallet className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            <span className="text-xs font-bold text-slate-800 dark:text-slate-200">Transit Pricing Structure:</span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setBudgetMode('LOWEST_COST')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                budgetMode === 'LOWEST_COST'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700'
              }`}
            >
              🎯 Non-AC BEST (₹10 Base) + Local Train (₹5–₹10)
            </button>
            <button
              onClick={() => setBudgetMode('FASTEST')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                budgetMode === 'FASTEST'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700'
              }`}
            >
              ⚡ AC BEST (₹12 Base) / Metro (₹10–₹40)
            </button>
          </div>
        </div>

        {/* Selected Stops */}
        <div className="space-y-2 mb-4">
          <label className="text-xs font-bold text-slate-700 dark:text-slate-300 block">
            Destinations to Tour from {startLocation} ({selectedStops.length})
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {selectedStops.map(stop => (
              <div
                key={stop.id}
                className="flex items-center justify-between bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 p-2.5 rounded-xl text-xs"
              >
                <div>
                  <p className="font-bold text-slate-800 dark:text-slate-200">{stop.name}</p>
                  <p className="text-[10px] text-slate-500 dark:text-slate-400">
                    Dwell: {stop.typical_dwell_minutes}m • Priority:{' '}
                    <span
                      className={`font-semibold ${
                        stop.priority === 'HIGH'
                          ? 'text-rose-600 dark:text-rose-400'
                          : stop.priority === 'MEDIUM'
                          ? 'text-amber-600 dark:text-amber-400'
                          : 'text-slate-500 dark:text-slate-400'
                      }`}
                    >
                      {stop.priority}
                    </span>
                    {stop.fare_inr > 0 && ` • Entry Ticket: ₹${stop.fare_inr}`}
                  </p>
                </div>
                <button
                  onClick={() => removeStop(stop.id)}
                  className="text-slate-400 hover:text-rose-500 p-1"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Add more stops buttons */}
        <div className="flex flex-wrap gap-1.5 mb-5">
          <span className="text-[11px] text-slate-400 py-1 mr-1">Add to circuit:</span>
          {attractions
            .filter(a => a.id !== 'HOTEL_BASE' && !selectedStops.some(s => s.id === a.id))
            .map(a => (
              <button
                key={a.id}
                onClick={() => addStop(a)}
                className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs px-2.5 py-1 rounded-lg transition"
              >
                <Plus className="w-3 h-3" />
                {a.name}
              </button>
            ))}
        </div>

        {/* Action Button */}
        <button
          onClick={handlePlanTour}
          disabled={isLoading || selectedStops.length === 0}
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-xl text-sm transition shadow-sm flex items-center justify-center gap-2"
        >
          {isLoading ? (
            'Computing Verified Routes & Fares...'
          ) : (
            <>
              <Compass className="w-4 h-4" /> Generate Optimal Day Tour from {startLocation}
            </>
          )}
        </button>
      </div>

      {/* Plan Results */}
      {plan && (
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 space-y-5">
          {/* Summary Card */}
          <div className="flex flex-wrap items-center justify-between bg-slate-50 dark:bg-slate-800/70 p-4 rounded-xl border border-slate-200 dark:border-slate-700/60 gap-3">
            <div>
              <div className="flex items-center gap-2">
                <span
                  className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${
                    plan.status === 'PROTECTED'
                      ? 'bg-emerald-100 dark:bg-emerald-950/50 text-emerald-800 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800'
                      : plan.status === 'FEASIBLE'
                      ? 'bg-blue-100 dark:bg-blue-950/50 text-blue-800 dark:text-blue-300 border-blue-300 dark:border-blue-800'
                      : plan.status === 'BUDGET_DEFICIT'
                      ? 'bg-amber-100 dark:bg-amber-950/50 text-amber-800 dark:text-amber-300 border-amber-300 dark:border-amber-800'
                      : 'bg-rose-100 dark:bg-rose-950/50 text-rose-800 dark:text-rose-300 border-rose-300 dark:border-rose-800'
                  }`}
                >
                  {plan.status}
                </span>
                <span className="text-xs font-bold text-slate-800 dark:text-slate-200">
                  Origin Base: {plan.start_location}
                </span>
              </div>
              <p className="text-sm font-bold text-slate-900 dark:text-white mt-1">
                Back at {plan.start_location} by {plan.expected_return_time} (Curfew: {plan.curfew_deadline})
              </p>
            </div>

            <div className="text-right">
              <p className="text-sm font-bold text-emerald-700 dark:text-emerald-400 flex items-center justify-end gap-1">
                <IndianRupee className="w-4 h-4" /> Total Transit Fare: ₹{plan.total_transit_fare_inr.toFixed(0)}
              </p>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                Min Required: ₹{plan.min_budget_required_inr.toFixed(0)} • Remaining: ₹{plan.budget_remaining_inr.toFixed(0)}
              </p>
            </div>
          </div>

          {/* SDG 13 Carbon & Economic Footprint Metric */}
          {tourCarbonMetrics && <CarbonBadge metrics={tourCarbonMetrics} />}

          {/* Budget Deficit Warning */}
          {!plan.is_budget_sufficient && (
            <div className="bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 p-3.5 rounded-xl text-xs text-amber-900 dark:text-amber-200 flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 text-amber-600 dark:text-amber-400 mt-0.5 shrink-0" />
              <div>
                <p className="font-bold">Allocated Budget Below Minimum Transit Cost</p>
                <p className="text-[11px] mt-0.5">
                  Minimum public transit cost across these locations is ₹{plan.min_budget_required_inr.toFixed(0)}. Increase budget by ₹
                  {(plan.min_budget_required_inr - (budgetInr || 0)).toFixed(0)} to cover official bus &amp; rail tickets.
                </p>
              </div>
            </div>
          )}

          {/* Explanation Banner */}
          <div className="bg-indigo-50/60 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-800/60 p-3.5 rounded-xl text-xs text-indigo-900 dark:text-indigo-200 leading-relaxed">
            <span className="font-bold">Optimizer Summary: </span>
            {plan.explanation}
          </div>

          {/* Disruption Alert Message */}
          {disruptionMsg && (
            <div className="bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 p-4 rounded-xl text-xs space-y-1">
              <div className="flex items-center gap-2 font-bold text-amber-900 dark:text-amber-200">
                <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                Adaptive Re-optimization Applied
              </div>
              <p className="text-amber-800 dark:text-amber-300 leading-relaxed">{plan.explanation}</p>
              {plan.dropped_stops.length > 0 && (
                <div className="mt-2 bg-white/70 dark:bg-slate-800 p-2 rounded-lg border border-amber-200 dark:border-amber-800/60 font-medium text-amber-950 dark:text-amber-200">
                  🚫 Dropped to Protect Curfew &amp; Budget:{' '}
                  {plan.dropped_stops.map(s => s.name).join(', ')}
                </div>
              )}
            </div>
          )}

          {/* Detailed Timeline Sequence with Verified Bus/Train Numbers */}
          <div className="space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
              Verified Transit Route Instructions &amp; Boarding Points
            </h3>

            {plan.visit_windows.map((win, idx) => {
              const leg = plan.legs[idx];
              return (
                <div key={win.stop_id} className="space-y-2.5">
                  {/* Transit Instruction Card */}
                  {leg && (
                    <div className="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60 p-3.5 rounded-xl text-xs space-y-1.5">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 font-bold text-indigo-950 dark:text-indigo-200">
                          {leg.mode === 'RAIL' ? (
                            <Train className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                          ) : (
                            <Bus className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                          )}
                          <span className="bg-indigo-100 dark:bg-indigo-950 text-indigo-800 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 px-2.5 py-0.5 rounded text-[11px] font-bold">
                            {leg.bus_or_train_number || leg.route_name}
                          </span>
                        </div>
                        <span className="font-bold text-emerald-700 dark:text-emerald-400">₹{leg.fare_inr.toFixed(0)} • {leg.duration_min} mins</span>
                      </div>

                      <div className="text-slate-600 dark:text-slate-300 grid grid-cols-1 sm:grid-cols-2 gap-1 text-[11px] pl-6">
                        <p>
                          <span className="font-semibold text-slate-500 dark:text-slate-400">Board:</span> {leg.boarding_stop}
                        </p>
                        <p>
                          <span className="font-semibold text-slate-500 dark:text-slate-400">Alight:</span> {leg.alighting_stop}
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Attraction Destination Card */}
                  <div className="bg-white dark:bg-slate-800/90 border-2 border-slate-200 dark:border-slate-700 p-4 rounded-xl flex items-center justify-between shadow-xs">
                    <div className="flex items-center gap-3">
                      <div className="w-7 h-7 rounded-full bg-indigo-600 text-white text-xs font-bold flex items-center justify-center">
                        {idx + 1}
                      </div>
                      <div>
                        <p className="text-sm font-bold text-slate-900 dark:text-white">{win.stop_name}</p>
                        <p className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2 mt-0.5">
                          <Clock className="w-3.5 h-3.5 text-slate-400" />
                          Visit Window: {win.arrival_time} – {win.departure_time} ({win.dwell_minutes}m stay)
                        </p>
                      </div>
                    </div>

                    <div className="text-right">
                      <span
                        className={`text-[10px] font-bold px-2.5 py-1 rounded-full ${
                          win.is_open
                            ? 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800'
                            : 'bg-rose-100 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300 border border-rose-300 dark:border-rose-800'
                        }`}
                      >
                        {win.is_open ? 'Open (' + win.open_time + '–' + win.close_time + ')' : 'Closed'}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}

            {/* Return Transit to User's Origin Base */}
            {plan.legs[plan.legs.length - 1] && (
              <div className="space-y-2.5">
                <div className="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60 p-3.5 rounded-xl text-xs space-y-1.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 font-bold text-indigo-950 dark:text-indigo-200">
                      <Train className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                      <span className="bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 px-2 py-0.5 rounded text-[11px] font-bold">
                        RETURN: {plan.legs[plan.legs.length - 1].bus_or_train_number || 'Return Transit'}
                      </span>
                    </div>
                    <span className="font-bold text-emerald-700 dark:text-emerald-400">
                      ₹{plan.legs[plan.legs.length - 1].fare_inr.toFixed(0)} • {plan.legs[plan.legs.length - 1].duration_min} mins
                    </span>
                  </div>
                  <div className="text-slate-600 dark:text-slate-300 text-[11px] pl-6">
                    <p>
                      <span className="font-semibold text-slate-500 dark:text-slate-400">Board:</span> {plan.legs[plan.legs.length - 1].boarding_stop} ➔ <span className="font-semibold text-slate-500 dark:text-slate-400">Back at:</span> {plan.start_location}
                    </p>
                  </div>
                </div>

                <div className="bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 p-3.5 rounded-xl flex items-center justify-between">
                  <div className="flex items-center gap-2 font-bold text-emerald-950 dark:text-emerald-200 text-xs">
                    <CheckCircle className="w-4 h-4 text-emerald-600 dark:text-emerald-400" /> Back at {plan.start_location} by{' '}
                    {plan.expected_return_time}
                  </div>
                  <span className="text-xs font-semibold text-emerald-700 dark:text-emerald-300">Curfew: {plan.curfew_deadline}</span>
                </div>
              </div>
            )}
          </div>

          {/* Mid-Day Disruption Simulation Trigger */}
          <div className="pt-3 border-t border-slate-200 dark:border-slate-800">
            <button
              onClick={handleSimulateDisruption}
              disabled={isReplanning}
              className="w-full bg-amber-50 dark:bg-amber-950/40 hover:bg-amber-100 dark:hover:bg-amber-900/40 border border-amber-300 dark:border-amber-800 text-amber-900 dark:text-amber-200 font-semibold py-3 rounded-xl text-xs transition flex items-center justify-center gap-2"
            >
              <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400" />
              {isReplanning ? 'Re-optimizing Tour...' : 'Simulate Mid-Day Corridor Disruption (Persona T5 Test)'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
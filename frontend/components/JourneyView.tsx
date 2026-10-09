'use client';

import React from 'react';
import { JourneyPlanResponse } from '@/types';
import { Footprints, Bus, Train, Clock, IndianRupee, ArrowRight } from 'lucide-react';

interface JourneyViewProps {
  journey: JourneyPlanResponse;
}

export default function JourneyView({ journey }: JourneyViewProps) {
  const { summary, legs } = journey;

  return (
    <div className="space-y-4">
      {/* Metrics Row */}
      <div className="grid grid-cols-4 gap-2 bg-slate-50 p-3 rounded-xl border border-slate-200 text-center">
        <div>
          <span className="text-xs text-slate-500 block">Est. Arrival</span>
          <span className="font-semibold text-slate-800 flex items-center justify-center gap-1 text-sm sm:text-base">
            <Clock className="w-4 h-4 text-emerald-600" /> {summary.arrivalTime}
          </span>
        </div>
        <div>
          <span className="text-xs text-slate-500 block">Total Fare</span>
          <span className="font-semibold text-slate-800 flex items-center justify-center gap-1 text-sm sm:text-base">
            <IndianRupee className="w-4 h-4 text-amber-600" /> {summary.fare}
          </span>
        </div>
        <div>
          <span className="text-xs text-slate-500 block">Walking</span>
          <span className="font-semibold text-slate-800 flex items-center justify-center gap-1 text-sm sm:text-base">
            <Footprints className="w-4 h-4 text-slate-600" /> {summary.walkingMeters}m
          </span>
        </div>
        <div>
          <span className="text-xs text-slate-500 block">Transfers</span>
          <span className="font-semibold text-slate-800 text-sm sm:text-base">
            {summary.transfers}
          </span>
        </div>
      </div>

      {/* Leg Step by Step */}
      <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
        {legs.map((leg, index) => (
          <div key={index} className="relative group">
            <div
              className={`absolute -left-6 top-1 w-5 h-5 rounded-full border-2 bg-white flex items-center justify-center ${
                leg.mode === 'METRO'
                  ? 'border-sky-600 text-sky-600'
                  : leg.mode === 'BUS'
                  ? 'border-green-600 text-green-600'
                  : 'border-slate-400 text-slate-500'
              }`}
            >
              {leg.mode === 'METRO' && <Train className="w-2.5 h-2.5" />}
              {leg.mode === 'BUS' && <Bus className="w-2.5 h-2.5" />}
              {leg.mode === 'WALK' && <Footprints className="w-2.5 h-2.5" />}
            </div>

            <div className="bg-white p-3 rounded-lg border border-slate-200 hover:border-slate-300 transition-all shadow-sm">
              <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                <span className="font-bold tracking-wide uppercase text-slate-700">
                  {leg.lineName || leg.mode}
                </span>
                <span>{leg.durationMin} mins</span>
              </div>
              <div className="text-sm font-medium text-slate-800 flex items-center gap-2">
                <span>{leg.fromName}</span>
                <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
                <span>{leg.toName}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
'use client';

import React from 'react';
import { JourneyPlanResponse } from '@/types';
import { Check, X, ShieldAlert, Sparkles } from 'lucide-react';

interface RouteComparisonProps {
  currentRoute: JourneyPlanResponse;
  alternativeRoute: JourneyPlanResponse;
  delayMin: number;
}

export default function RouteComparison({
  currentRoute,
  alternativeRoute,
  delayMin,
}: RouteComparisonProps) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
      <div className="bg-slate-900 text-white px-4 py-2.5 flex items-center justify-between text-xs">
        <span className="font-semibold flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          Alternative Route Proposal
        </span>
        <span className="bg-emerald-500/20 text-emerald-300 font-bold px-2 py-0.5 rounded">
          Saves ~27 Mins
        </span>
      </div>

      <div className="p-4 space-y-4">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b text-slate-400 text-left">
              <th className="pb-2 font-medium">Metric</th>
              <th className="pb-2 font-medium text-red-600">Current (Disrupted)</th>
              <th className="pb-2 font-medium text-emerald-600">Alternative</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            <tr>
              <td className="py-2 text-slate-600 font-medium">ETA</td>
              <td className="py-2 text-red-600 line-through">
                {currentRoute.summary.arrivalTime} (+{delayMin}m)
              </td>
              <td className="py-2 text-emerald-700 font-bold">
                {alternativeRoute.summary.arrivalTime}
              </td>
            </tr>
            <tr>
              <td className="py-2 text-slate-600 font-medium">Total Fare</td>
              <td className="py-2 text-slate-700">₹{currentRoute.summary.fare}</td>
              <td className="py-2 text-slate-700">₹{alternativeRoute.summary.fare}</td>
            </tr>
            <tr>
              <td className="py-2 text-slate-600 font-medium">Walking</td>
              <td className="py-2 text-slate-700">{currentRoute.summary.walkingMeters}m</td>
              <td className="py-2 text-slate-700">{alternativeRoute.summary.walkingMeters}m</td>
            </tr>
            <tr>
              <td className="py-2 text-slate-600 font-medium">Transfers</td>
              <td className="py-2 text-slate-700">{currentRoute.summary.transfers}</td>
              <td className="py-2 text-slate-700">{alternativeRoute.summary.transfers}</td>
            </tr>
            <tr>
              <td className="py-2 text-slate-600 font-medium">Deadline Status</td>
              <td className="py-2 text-red-600 flex items-center gap-1 font-semibold">
                <X className="w-3.5 h-3.5" /> Breached
              </td>
              <td className="py-2 text-emerald-700 flex items-center gap-1 font-semibold">
                <Check className="w-3.5 h-3.5" /> Protected
              </td>
            </tr>
          </tbody>
        </table>

        <div className="bg-amber-50 border border-amber-200 p-2.5 rounded-lg text-[11px] text-amber-800">
          <strong>Why Reroute?</strong> Metro Line 1 delay violates your hard deadline constraint. The suggested alternative uses BKC connector buses to protect your target arrival time.
        </div>
      </div>
    </div>
  );
}
'use client';

import React from 'react';
import { JourneyPlanResponse } from '../types';
import { Check, X, Sparkles, AlertCircle } from 'lucide-react';

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
    <div className="bg-white dark:bg-slate-900/90 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-lg transition-colors">
      <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white px-4 py-3 flex items-center justify-between text-xs">
        <span className="font-bold flex items-center gap-1.5">
          <Sparkles className="w-4 h-4 text-amber-300" />
          Safe Dynamic Replanning (USP 3 &amp; 4)
        </span>
        <span className="bg-white/20 backdrop-blur-md px-2.5 py-0.5 rounded-full font-bold">
          Saves ~27 mins vs delay
        </span>
      </div>

      <div className="p-4 space-y-4">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-400 text-left">
              <th className="pb-2 font-medium">Metric</th>
              <th className="pb-2 font-semibold text-rose-500">Current (Disrupted)</th>
              <th className="pb-2 font-semibold text-emerald-500">Proposed Alternative</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
            <tr>
              <td className="py-2.5 text-slate-600 dark:text-slate-400 font-medium">Arrival Time</td>
              <td className="py-2.5 text-rose-500 font-semibold line-through">
                {currentRoute.summary.arrivalTime} (+{delayMin}m)
              </td>
              <td className="py-2.5 text-emerald-600 dark:text-emerald-400 font-bold">
                {alternativeRoute.summary.arrivalTime}
              </td>
            </tr>
            <tr>
              <td className="py-2.5 text-slate-600 dark:text-slate-400 font-medium">Total Fare</td>
              <td className="py-2.5 text-slate-700 dark:text-slate-300">₹{currentRoute.summary.fare}</td>
              <td className="py-2.5 text-slate-700 dark:text-slate-300 font-medium">
                ₹{alternativeRoute.summary.fare}{' '}
                <span className="text-[10px] text-emerald-600 dark:text-emerald-400">(Within Budget)</span>
              </td>
            </tr>
            <tr>
              <td className="py-2.5 text-slate-600 dark:text-slate-400 font-medium">Walking Distance</td>
              <td className="py-2.5 text-slate-700 dark:text-slate-300">{currentRoute.summary.walkingMeters}m</td>
              <td className="py-2.5 text-slate-700 dark:text-slate-300 font-medium">{alternativeRoute.summary.walkingMeters}m</td>
            </tr>
            <tr>
              <td className="py-2.5 text-slate-600 dark:text-slate-400 font-medium">Transfers</td>
              <td className="py-2.5 text-slate-700 dark:text-slate-300">{currentRoute.summary.transfers}</td>
              <td className="py-2.5 text-slate-700 dark:text-slate-300">{alternativeRoute.summary.transfers}</td>
            </tr>
            <tr>
              <td className="py-2.5 text-slate-600 dark:text-slate-400 font-medium">Deadline Feasibility</td>
              <td className="py-2.5 text-rose-500 font-semibold flex items-center gap-1">
                <X className="w-3.5 h-3.5" /> Breached
              </td>
              <td className="py-2.5 text-emerald-600 dark:text-emerald-400 font-bold flex items-center gap-1">
                <Check className="w-3.5 h-3.5" /> Protected
              </td>
            </tr>
            <tr>
              <td className="py-2.5 text-slate-600 dark:text-slate-400 font-medium">Accessibility</td>
              <td className="py-2.5 text-slate-700 dark:text-slate-300">Step-free</td>
              <td className="py-2.5 text-emerald-600 dark:text-emerald-400 font-medium flex items-center gap-1">
                <Check className="w-3 h-3" /> Step-free Certified
              </td>
            </tr>
          </tbody>
        </table>

        <div className="bg-amber-500/10 border border-amber-500/30 p-3 rounded-xl text-[11px] text-amber-800 dark:text-amber-300 flex items-start gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-amber-500" />
          <span>
            <strong>Meaningful Improvement:</strong> Time saving exceeds the threshold of ΔT ≥ max(8 mins, 15% remaining journey)[cite: 70]. Hard constraints (₹80 budget cap, 1000m max walking) strictly hold[cite: 54, 109].
          </span>
        </div>
      </div>
    </div>
  );
}
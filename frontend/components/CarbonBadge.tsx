// components/CarbonBadge.tsx
'use client';

import React from 'react';
import { CarbonMetrics } from '../types';
import { Leaf, IndianRupee, TrendingUp } from 'lucide-react';

interface CarbonBadgeProps {
  metrics?: CarbonMetrics;
}

export default function CarbonBadge({ metrics }: CarbonBadgeProps) {
  if (!metrics) return null;

  const kgSaved = (metrics.co2SavedGrams / 1000).toFixed(2);

  return (
    <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-3.5 space-y-2">
      <div className="flex items-center justify-between text-xs">
        <span className="font-bold text-emerald-800 dark:text-emerald-300 flex items-center gap-1.5">
          <Leaf className="w-4 h-4 text-emerald-500" />
          SDG 13 Climate Impact &amp; Savings
        </span>
        <span className="bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 font-extrabold px-2 py-0.5 rounded-full text-[10px]">
          🌱 -{kgSaved} kg CO₂
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[11px] pt-1 border-t border-emerald-500/20">
        <div className="text-slate-600 dark:text-slate-300">
          <span className="text-slate-400 block text-[10px]">Emissions vs Cab</span>
          <span className="font-semibold text-emerald-700 dark:text-emerald-400">
            {metrics.co2EmittedGrams}g vs {(metrics.co2EmittedGrams + metrics.co2SavedGrams)}g
          </span>
        </div>
        <div className="text-slate-600 dark:text-slate-300">
          <span className="text-slate-400 block text-[10px]">Money Saved vs Cab</span>
          <span className="font-semibold text-emerald-700 dark:text-emerald-400 flex items-center">
            <IndianRupee className="w-3 h-3" />
            {metrics.moneySaved} (Cab ~₹{metrics.cabComparisonFare})
          </span>
        </div>
      </div>
    </div>
  );
}
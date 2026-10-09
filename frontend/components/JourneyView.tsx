
'use client';

import React from 'react';
import { JourneyPlanResponse } from '../types';
import CarbonBadge from './CarbonBadge';
import {
  Footprints,
  Bus,
  Train,
  Clock,
  IndianRupee,
  ArrowRight,
  ShieldCheck,
  AlertCircle,
} from 'lucide-react';

interface JourneyViewProps {
  journey: JourneyPlanResponse;
}

export default function JourneyView({ journey }: JourneyViewProps) {
  const { summary, legs } = journey;

  const isProtected = summary.status === 'PROTECTED';
  const isDelayed = summary.status === 'DELAYED';

  return (
    <div className="space-y-4">
      {/* Route Status Header */}
      <div className="flex items-center justify-between text-xs pb-1 border-b border-slate-100 dark:border-slate-800">
        <span className="font-bold text-slate-700 dark:text-slate-300">
          Planned Itinerary
        </span>

        <span
          className={`px-2 py-0.5 rounded-full font-bold text-[10px] flex items-center gap-1 ${
            isProtected
              ? 'bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30'
              : isDelayed
              ? 'bg-rose-500/20 text-rose-700 dark:text-rose-300 border border-rose-500/30'
              : 'bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border border-indigo-500/20'
          }`}
        >
          {isProtected ? (
            <>
              <ShieldCheck className="w-3 h-3" />
              Protected Reroute
            </>
          ) : isDelayed ? (
            <>
              <AlertCircle className="w-3 h-3" />
              Disruption Impacted
            </>
          ) : (
            'Optimal Schedule'
          )}
        </span>
      </div>

      {/* Metrics Summary Row */}
      <div className="grid grid-cols-4 gap-2 bg-slate-50 dark:bg-slate-800/60 p-3 rounded-2xl border border-slate-200 dark:border-slate-700/60 text-center">
        <div>
          <span className="text-[11px] text-slate-500 dark:text-slate-400 block font-medium">
            Est. Arrival
          </span>
          <span className="font-bold text-slate-800 dark:text-slate-200 flex items-center justify-center gap-1 text-xs sm:text-sm mt-0.5">
            <Clock className="w-3.5 h-3.5 text-emerald-500" />
            {summary.arrivalTime}
          </span>
        </div>

        <div>
          <span className="text-[11px] text-slate-500 dark:text-slate-400 block font-medium">
            Total Fare
          </span>
          <span className="font-bold text-slate-800 dark:text-slate-200 flex items-center justify-center gap-1 text-xs sm:text-sm mt-0.5">
            <IndianRupee className="w-3.5 h-3.5 text-amber-500" />
            {summary.fare}
          </span>
        </div>

        <div>
          <span className="text-[11px] text-slate-500 dark:text-slate-400 block font-medium">
            Walking
          </span>
          <span className="font-bold text-slate-800 dark:text-slate-200 flex items-center justify-center gap-1 text-xs sm:text-sm mt-0.5">
            <Footprints className="w-3.5 h-3.5 text-slate-500" />
            {summary.walkingMeters}m
          </span>
        </div>

        <div>
          <span className="text-[11px] text-slate-500 dark:text-slate-400 block font-medium">
            Transfers
          </span>
          <span className="font-bold text-slate-800 dark:text-slate-200 text-xs sm:text-sm mt-0.5 block">
            {summary.transfers}
          </span>
        </div>
      </div>

      {/* SDG 13 Carbon & Economic Footprint Metric */}
      <CarbonBadge metrics={summary.carbon} />

      {/* Progressive Door-to-Door Journey Timeline */}
      <div className="relative pl-6 space-y-3.5 pt-2 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-200 dark:before:bg-slate-700">
        {legs.map((leg, index) => {
          const isMetro =
            leg.mode === 'METRO' || leg.mode === 'SUBWAY';
          const isRail =
            leg.mode === 'RAIL' || leg.mode === 'TRAIN';
          const isBus = leg.mode === 'BUS';
          const isWalk = leg.mode === 'WALK';

          const modeColor = isMetro
            ? 'border-sky-500 text-sky-500'
            : isRail
            ? 'border-indigo-500 text-indigo-500'
            : isBus
            ? 'border-green-500 text-green-500'
            : 'border-slate-400 text-slate-400';

          const modeBadgeColor = isMetro
            ? 'bg-sky-500/10 text-sky-700 dark:text-sky-300'
            : isRail
            ? 'bg-indigo-500/10 text-indigo-700 dark:text-indigo-300'
            : isBus
            ? 'bg-green-500/10 text-green-700 dark:text-green-300'
            : 'bg-slate-200/60 dark:bg-slate-700/60 text-slate-600 dark:text-slate-300';

          return (
            <div key={`${leg.mode}-${index}`} className="relative group">
              {/* Timeline Icon Node */}
              <div
                className={`absolute -left-6 top-1 w-5 h-5 rounded-full border-2 bg-white dark:bg-slate-900 flex items-center justify-center shadow-xs transition-transform group-hover:scale-110 ${modeColor}`}
              >
                {isMetro && <Train className="w-2.5 h-2.5" />}
                {isRail && <Train className="w-2.5 h-2.5" />}
                {isBus && <Bus className="w-2.5 h-2.5" />}
                {isWalk && <Footprints className="w-2.5 h-2.5" />}
              </div>

              {/* Leg Card Content */}
              <div className="bg-slate-50 dark:bg-slate-800/40 p-3 rounded-xl border border-slate-200 dark:border-slate-700/60 shadow-xs hover:border-indigo-400/40 transition-colors">
                <div className="flex items-center justify-between text-[11px] mb-1 gap-2">
                  <span
                    className={`font-bold uppercase tracking-wider px-1.5 py-0.5 rounded text-[10px] ${modeBadgeColor}`}
                  >
                    {leg.lineName || leg.mode}
                  </span>

                  <span className="text-slate-500 dark:text-slate-400 font-medium text-right">
                    {leg.durationMin} mins
                    {' · '}
                    {leg.distanceMeters > 1000
                      ? `${(leg.distanceMeters / 1000).toFixed(1)} km`
                      : `${leg.distanceMeters} m`}
                  </span>
                </div>

                <div className="text-xs font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-1.5 flex-wrap">
                  <span>{leg.fromName}</span>
                  <ArrowRight className="w-3 h-3 text-slate-400 shrink-0" />
                  <span>{leg.toName}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

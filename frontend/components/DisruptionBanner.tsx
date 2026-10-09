'use client';

import React from 'react';
import { DisruptionAlert } from '../types';
import { AlertTriangle, ShieldAlert, ChevronRight } from 'lucide-react';

interface DisruptionBannerProps {
  alert: DisruptionAlert;
  onOpenExplain: () => void;
}

export default function DisruptionBanner({ alert, onOpenExplain }: DisruptionBannerProps) {
  if (alert.status === 'IGNORE') return null;

  const isConfirmed = alert.status === 'CONFIRMED';

  return (
    <div
      onClick={onOpenExplain}
      className={`p-4 rounded-2xl border cursor-pointer transition-all flex items-start gap-3 shadow-md ${
        isConfirmed
          ? 'bg-rose-50 border-rose-200 text-rose-900 dark:bg-rose-950/40 dark:border-rose-800/80 dark:text-rose-100 hover:ring-2 hover:ring-rose-500/30'
          : 'bg-amber-50 border-amber-200 text-amber-900 dark:bg-amber-950/40 dark:border-amber-800/80 dark:text-amber-100 hover:ring-2 hover:ring-amber-500/30'
      }`}
    >
      <div className="mt-0.5">
        {isConfirmed ? (
          <ShieldAlert className="w-5 h-5 text-rose-600 dark:text-rose-400 shrink-0" />
        ) : (
          <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0" />
        )}
      </div>

      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span
            className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
              isConfirmed
                ? 'bg-rose-600 text-white'
                : 'bg-amber-500 text-white dark:bg-amber-600'
            }`}
          >
            {alert.status}
          </span>
          <span className="text-[11px] font-semibold opacity-80">
            Confidence: {Math.round(alert.confidenceScore * 100)}%
          </span>
        </div>

        <h4 className="font-bold text-xs sm:text-sm mt-1 text-slate-900 dark:text-white">
          {alert.title}
        </h4>
        <p className="text-[11px] opacity-80 mt-0.5 line-clamp-1">
          {alert.explanation}
        </p>
      </div>

      <div className="flex items-center text-xs font-bold text-indigo-600 dark:text-indigo-400 gap-0.5 self-center shrink-0">
        <span>Why?</span>
        <ChevronRight className="w-4 h-4" />
      </div>
    </div>
  );
}
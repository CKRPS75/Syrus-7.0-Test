'use client';

import React from 'react';
import { DisruptionAlert } from '@/types';
import { AlertTriangle, AlertCircle, ShieldAlert, ChevronRight } from 'lucide-react';

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
      className={`p-4 rounded-xl border cursor-pointer transition-all flex items-start gap-3 shadow-sm ${
        isConfirmed
          ? 'bg-red-50 border-red-200 hover:bg-red-100/70'
          : 'bg-amber-50 border-amber-200 hover:bg-amber-100/70'
      }`}
    >
      <div className="mt-0.5">
        {isConfirmed ? (
          <ShieldAlert className="w-5 h-5 text-red-600" />
        ) : (
          <AlertTriangle className="w-5 h-5 text-amber-600" />
        )}
      </div>

      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span
            className={`text-xs font-bold px-2 py-0.5 rounded-full ${
              isConfirmed ? 'bg-red-600 text-white' : 'bg-amber-500 text-white'
            }`}
          >
            {alert.status}
          </span>
          <span className="text-xs text-slate-500 font-medium">
            Confidence: {Math.round(alert.confidenceScore * 100)}%
          </span>
        </div>

        <h4 className="font-semibold text-slate-900 text-sm mt-1">{alert.title}</h4>
        <p className="text-xs text-slate-600 mt-0.5 line-clamp-1">{alert.explanation}</p>
      </div>

      <div className="flex items-center text-xs font-semibold text-slate-600 gap-0.5 self-center">
        <span>Why?</span>
        <ChevronRight className="w-4 h-4" />
      </div>
    </div>
  );
}
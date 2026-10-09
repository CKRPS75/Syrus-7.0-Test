'use client';

import React from 'react';
import { DisruptionAlert } from '../types';
import { X, CheckCircle, ShieldCheck } from 'lucide-react';

interface ExplainabilityModalProps {
  isOpen: boolean;
  onClose: () => void;
  alert: DisruptionAlert;
}

export default function ExplainabilityModal({
  isOpen,
  onClose,
  alert,
}: ExplainabilityModalProps) {
  if (!isOpen) return null;

  const scorePercentage = Math.round(alert.confidenceScore * 100);
  const barColor = alert.confidenceScore >= 0.65 ? 'bg-red-500' : 'bg-amber-500';

  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white max-w-md w-full rounded-2xl p-6 shadow-xl border border-slate-100 relative space-y-4">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-100"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2 text-indigo-600 font-semibold text-sm">
          <ShieldCheck className="w-5 h-5" />
          <span>Trust & Evidence Explanation</span>
        </div>

        <div>
          <h3 className="font-bold text-slate-900 text-lg">{alert.title}</h3>
          <p className="text-xs text-slate-500 mt-1">Impacted: {alert.affectedEntity}</p>
        </div>

        <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
          <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
            <span>Evidence Confidence (P*)</span>
            <span>{scorePercentage}%</span>
          </div>
          <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
            <div
              className={`h-full ${barColor}`}
              style={{ width: `${scorePercentage}%` }}
            />
          </div>
        </div>

        <div>
          <span className="text-xs font-bold text-slate-700 uppercase tracking-wide block mb-2">
            Corroborated Sources
          </span>
          <div className="space-y-2">
            {alert.evidenceSources.map((source, i) => (
              <div
                key={i}
                className="flex items-start gap-2 bg-emerald-50 text-emerald-900 p-2.5 rounded-lg text-xs border border-emerald-100"
              >
                <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span>{source}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs text-slate-600">
          <span className="font-semibold block mb-0.5 text-slate-800">Impact Assessment:</span>
          {alert.explanation}
        </div>

        <button
          onClick={onClose}
          className="w-full bg-slate-900 text-white font-medium py-2.5 rounded-xl hover:bg-slate-800 text-xs transition"
        >
          Close
        </button>
      </div>
    </div>
  );
}
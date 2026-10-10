'use client';

import React from 'react';
import { DisruptionAlert } from '../types';
import { X, CheckCircle2, ShieldCheck, Layers } from 'lucide-react';

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
  const isConfirmed = alert.status === 'CONFIRMED';

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-white dark:bg-slate-900 max-w-lg w-full rounded-3xl p-6 shadow-2xl border border-slate-200 dark:border-slate-800 relative space-y-4 text-slate-900 dark:text-slate-100 transition-colors">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-1.5 rounded-full text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2 text-indigo-600 dark:text-indigo-400 font-bold text-xs uppercase tracking-wider">
          <ShieldCheck className="w-4 h-4" />
          <span>Evidence & Grounded Explanation (Feature 1 & 6)</span>
        </div>

        <div>
          <h3 className="font-extrabold text-lg text-slate-900 dark:text-white">{alert.title}</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Target Entity: <span className="font-semibold text-slate-700 dark:text-slate-200">{alert.affectedEntity}</span>
          </p>
        </div>

        {/* Confidence Gauge */}
        <div className="bg-slate-50 dark:bg-slate-800/60 p-4 rounded-2xl border border-slate-200 dark:border-slate-700/60">
          <div className="flex justify-between text-xs font-bold mb-1.5">
            <span className="text-slate-700 dark:text-slate-300">Trust Engine Confidence (P*)</span>
            <span className={isConfirmed ? 'text-rose-500' : 'text-amber-500'}>
              {scorePercentage}% ({alert.status})
            </span>
          </div>
          <div className="w-full h-2.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-500 ${
                isConfirmed ? 'bg-gradient-to-r from-orange-500 to-rose-600' : 'bg-amber-500'
              }`}
              style={{ width: `${scorePercentage}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
            Formula: P* = 1 / (1 + e^-L), where L = logit(0.10) + Σ e_i[cite: 62, 100]. Crowd reports are capped at +2.6, meaning rumors alone can never reach the 0.65 confirmation threshold[cite: 63, 100].
          </p>
        </div>

        {/* Evidence Sources */}
        <div>
          <span className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider block mb-2">
            Corroborated Evidence Sources
          </span>
          <div className="space-y-2">
            {alert.evidenceSources.map((source, i) => (
              <div
                key={i}
                className="flex items-start gap-2.5 bg-emerald-500/10 text-emerald-800 dark:text-emerald-300 p-2.5 rounded-xl text-xs border border-emerald-500/20"
              >
                <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
                <span>{source}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Grounded LLM Explanation */}
        <div className="bg-slate-50 dark:bg-slate-800/40 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700/60 text-xs text-slate-600 dark:text-slate-300">
          <span className="font-bold block mb-1 text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-indigo-500" /> Grounded Impact Assessment:
          </span>
          {alert.explanation}
        </div>

        <button
          onClick={onClose}
          className="w-full bg-slate-900 hover:bg-slate-800 dark:bg-indigo-600 dark:hover:bg-indigo-700 text-white font-bold py-2.5 rounded-xl text-xs transition shadow-md"
        >
          Close Inspector
        </button>
      </div>
    </div>
  );
}
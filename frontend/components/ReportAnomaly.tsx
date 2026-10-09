'use client';

import React, { FormEvent, useState } from 'react';
import { Bus, CheckCircle2, Info, LoaderCircle, Send, ShieldCheck, Train, TramFront, TriangleAlert } from 'lucide-react';
import { submitTransitAnomaly, TransitAnomalyResponse } from '../lib/api';

type TransitMode = 'METRO' | 'BUS' | 'RAIL';
type Severity = 'LOW' | 'MEDIUM' | 'HIGH';

const modes: { value: TransitMode; label: string; Icon: typeof TramFront }[] = [
  { value: 'METRO', label: 'Metro', Icon: TramFront },
  { value: 'BUS', label: 'BEST Bus', Icon: Bus },
  { value: 'RAIL', label: 'Local Train', Icon: Train },
];

const categories = [
  'Vehicle / Technical Breakdown',
  'Service Delay',
  'Overcrowding',
  'Waterlogging / Track Flooding',
  'Accident or Safety Concern',
  'Accessibility Disruption',
  'Other',
];

const fieldClass = 'w-full rounded-xl border border-slate-200 bg-white/80 px-3 py-2.5 text-xs text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100';
const labelClass = 'mb-1.5 block text-xs font-bold text-slate-700';

export default function ReportAnomaly() {
  const [mode, setMode] = useState<TransitMode>('METRO');
  const [category, setCategory] = useState(categories[0]);
  const [route, setRoute] = useState('Metro Line 1 (Blue Line)');
  const [location, setLocation] = useState('Ghatkopar Station West');
  const [severity, setSeverity] = useState<Severity>('HIGH');
  const [description, setDescription] = useState('');
  const [accessibilityImpact, setAccessibilityImpact] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<TransitAnomalyResponse | null>(null);

  const handleModeChange = (value: TransitMode) => {
    setMode(value);
    if (value === 'METRO') setRoute('Metro Line 1 (Blue Line)');
    else if (value === 'BUS') setRoute('BEST Route 365');
    else setRoute('Central Line');
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError('');
    setResult(null);
    setIsSubmitting(true);
    try {
      setResult(await submitTransitAnomaly({
        mode,
        category,
        route,
        location,
        severity,
        description: description.trim(),
        accessibilityImpact,
      }));
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'The Trust Engine could not accept your report. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="grid items-start gap-6 xl:grid-cols-12">
      <form onSubmit={handleSubmit} className="space-y-5 rounded-[28px] border border-rose-200 bg-rose-50/60 p-5 shadow-sm sm:p-8 xl:col-span-7">
        <header className="flex items-center gap-3">
          <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl border border-rose-200 bg-rose-100 text-rose-600">
            <TriangleAlert className="h-5 w-5" />
          </span>
          <div>
            <h1 className="text-lg font-extrabold text-slate-900">Report Transit Anomaly</h1>
            <p className="mt-0.5 text-xs text-slate-500">Submit real-time ground truth to protect fellow Mumbai commuters.</p>
          </div>
        </header>

        <fieldset>
          <legend className={labelClass}>1. Transit Mode</legend>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
            {modes.map(({ value, label, Icon }) => (
              <button key={value} type="button" onClick={() => handleModeChange(value)} aria-pressed={mode === value}
                className={`flex items-center justify-center gap-2 rounded-xl border px-3 py-2.5 text-xs font-bold transition ${mode === value ? 'border-sky-600 bg-sky-600 text-white shadow-sm' : 'border-slate-200 bg-white/80 text-slate-600 hover:border-sky-300'}`}>
                <Icon className="h-4 w-4" />{label}
              </button>
            ))}
          </div>
        </fieldset>

        <div>
          <label htmlFor="anomaly-category" className={labelClass}>2. Incident Category</label>
          <select id="anomaly-category" value={category} onChange={(event) => setCategory(event.target.value)} className={fieldClass}>
            {categories.map((option) => <option key={option}>{option}</option>)}
          </select>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="anomaly-route" className={labelClass}>3. Line / Route Number</label>
            <input id="anomaly-route" value={route} onChange={(event) => setRoute(event.target.value)} className={fieldClass} required />
          </div>
          <div>
            <label htmlFor="anomaly-location" className={labelClass}>4. Station / Exact Location</label>
            <input id="anomaly-location" value={location} onChange={(event) => setLocation(event.target.value)} className={fieldClass} required />
          </div>
        </div>

        <fieldset>
          <legend className={labelClass}>5. Severity Level</legend>
          <div className="grid grid-cols-3 gap-2">
            {(['LOW', 'MEDIUM', 'HIGH'] as const).map((level) => (
              <button key={level} type="button" onClick={() => setSeverity(level)} aria-pressed={severity === level}
                className={`rounded-xl border px-3 py-2.5 text-[11px] font-extrabold transition ${severity === level ? level === 'HIGH' ? 'border-rose-600 bg-rose-600 text-white' : level === 'MEDIUM' ? 'border-amber-500 bg-amber-500 text-white' : 'border-emerald-600 bg-emerald-600 text-white' : 'border-slate-200 bg-white/80 text-slate-600 hover:bg-white'}`}>
                {level}
              </button>
            ))}
          </div>
        </fieldset>

        <div>
          <label htmlFor="anomaly-description" className={labelClass}>6. Ground Truth Description</label>
          <textarea id="anomaly-description" value={description} onChange={(event) => setDescription(event.target.value)}
            placeholder="Provide details about the disruption (e.g. stalled train, water on tracks)..."
            className={`${fieldClass} min-h-20 resize-y`} required minLength={8} />
        </div>

        <label className="flex items-center gap-2 text-xs font-semibold text-slate-600">
          <input type="checkbox" checked={accessibilityImpact} onChange={(event) => setAccessibilityImpact(event.target.checked)} className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
          Disruption impacts wheelchair / step-free access
        </label>

        {error && <p role="alert" className="rounded-xl border border-rose-200 bg-rose-100 px-3 py-2.5 text-xs font-semibold text-rose-700">{error}</p>}
        {result && (
          <div role="status" className="flex gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-3 text-xs text-emerald-800">
            <CheckCircle2 className="h-4 w-4 shrink-0" />
            <p>Your report was accepted by the Trust Engine. Status: <strong>{result.status}</strong> · Evidence confidence: <strong>{Math.round(result.confidence_score * 100)}%</strong>.</p>
          </div>
        )}
        <button type="submit" disabled={isSubmitting} className="flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-rose-600 to-indigo-600 px-4 py-3.5 text-xs font-extrabold text-white shadow-md transition hover:brightness-105 disabled:cursor-wait disabled:opacity-60">
          {isSubmitting ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          {isSubmitting ? 'Submitting report...' : 'Submit to Trust Engine'}
        </button>
      </form>

      <aside className="rounded-[28px] border border-indigo-200 bg-indigo-50/70 p-5 shadow-sm sm:p-7 xl:col-span-5">
        <h2 className="flex items-center gap-2 text-[11px] font-extrabold tracking-wide text-indigo-700"><ShieldCheck className="h-4 w-4" /> BAYESIAN EVIDENCE PIPELINE PREVIEW</h2>
        <p className="mt-4 text-xs leading-relaxed text-slate-600">Your report will be ingested as a raw evidence signal with anti-rumor guardrails applied automatically:</p>
        <div className="mt-5 space-y-3 rounded-2xl border border-indigo-100 bg-white/80 p-4 text-xs">
          <div className="flex justify-between gap-3"><span className="text-slate-500">Signal Contribution:</span><strong className="text-indigo-600">+0.8 Evidence Weight</strong></div>
          <div className="flex justify-between gap-3"><span className="text-slate-500">Crowd Cap Guardrail:</span><strong className="text-slate-700">+2.6 Maximum Total</strong></div>
          <div className="flex justify-between gap-3"><span className="text-slate-500">Confirmation Threshold:</span><strong className="text-emerald-600">P* ≥ 0.65</strong></div>
          <div className="flex justify-between gap-3"><span className="text-slate-500">Initial Status:</span><strong className="text-amber-600">WATCH (Warning Only)</strong></div>
        </div>
        <div className="mt-4 flex gap-2 rounded-2xl border border-indigo-200 bg-indigo-100/80 p-4 text-xs leading-relaxed text-indigo-800">
          <Info className="mt-0.5 h-4 w-4 shrink-0" />
          <p><strong>Anti-Sybil Defense:</strong> A lone crowd report generates a warning badge without altering passenger itineraries until independent verification arrives.</p>
        </div>
      </aside>
    </section>
  );
}

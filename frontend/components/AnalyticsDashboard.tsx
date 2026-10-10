'use client';

import React, { useState, useEffect } from 'react';
import {
  Activity,
  Clock3,
  Leaf,
  ShieldCheck,
  TriangleAlert,
  Wallet,
} from 'lucide-react';
import { fetchAnalyticsStats, fetchVulnerabilityMatrix } from '../lib/api';

type ModeFilter = 'ALL' | 'RAIL' | 'METRO' | 'BUS';

const emissions = [
  { mode: 'Ride-Hail Cab / Private Car (Baseline)', icon: '●', grams: 150, color: 'bg-rose-500', text: 'text-rose-600' },
  { mode: 'BEST Diesel/CNG Bus', icon: '▦', grams: 38, color: 'bg-amber-500', text: 'text-amber-600' },
  { mode: 'Mumbai Metro (Line 1/2A/7)', icon: '▣', grams: 22, color: 'bg-sky-500', text: 'text-sky-600' },
  { mode: 'Suburban Electric Railway', icon: '▤', grams: 18, color: 'bg-indigo-500', text: 'text-indigo-600' },
  { mode: 'Pedestrian / Walking', icon: '↟', grams: 0, color: 'bg-emerald-500', text: 'text-emerald-600' },
];

const defaultCorridors = [
  { corridor: 'Kurla Interchange (Central/Harbour)', mode: 'RAIL', issue: 'Signal Interlocking & Track Flooding', risk: 'CRITICAL', delay: '+34m', cause: 'Low track elevation + high interlocking switch density' },
  { corridor: 'Ghatkopar Metro Station (East-West)', mode: 'METRO', issue: 'Door Obstruction & Platform Overcrowding', risk: 'HIGH', delay: '+18m', cause: 'Crush load surge from Central Railway transfers' },
  { corridor: 'BKC Feeder Arterial (SCLR & Connector)', mode: 'BUS', issue: 'Surface Gridlock & Bus Bunching', risk: 'HIGH', delay: '+26m', cause: 'Narrow entry funnels into corporate financial hub' },
  { corridor: 'Dadar Junction Forecourt', mode: 'RAIL', issue: 'Footpath Blockage & Wheelchair Inaccessibility', risk: 'MEDIUM', delay: '+12m', cause: 'Encroached station exits and broken pedestrian curbs' },
  { corridor: 'Andheri Subway & West Approach', mode: 'BUS', issue: 'Monsoon Sump Waterlogging', risk: 'CRITICAL', delay: '+45m', cause: 'Underpass drainage saturation forcing multi-km detours' },
];

export default function AnalyticsDashboard() {
  const [filter, setFilter] = useState<ModeFilter>('ALL');
  const [stats, setStats] = useState<any>(null);
  const [corridors, setCorridors] = useState<any[]>(defaultCorridors);

  useEffect(() => {
    async function load() {
      try {
        const s = await fetchAnalyticsStats();
        if (s) setStats(s);
        const v = await fetchVulnerabilityMatrix();
        if (v && v.length > 0) {
          setCorridors(v.map(item => ({
            corridor: item.corridor,
            mode: item.mode,
            issue: item.dominantFailure || item.issue,
            risk: item.riskLevel || item.risk,
            delay: item.avgDelayMin !== undefined ? `+${item.avgDelayMin}m` : item.delay,
            cause: item.primaryCause || item.cause,
          })));
        }
      } catch (err) {
        console.warn('Analytics loading error notice:', err);
      }
    }
    load();
  }, []);

  const filteredCorridors = corridors.filter((row) => filter === 'ALL' || row.mode === filter);

  const metricCards = [
    { label: 'NET CO₂ ABATEMENT', value: stats?.net_co2_abatement_kg ? `-${Number(stats.net_co2_abatement_kg).toLocaleString()}` : '-1,842', unit: 'kg', detail: `Equivalent to ${stats?.trees_planted_equivalent || 88} trees planted vs. private cab baselines.`, icon: Leaf, style: 'border-emerald-200 bg-emerald-50 text-emerald-700' },
    { label: 'RUMORS FILTERED', value: `${stats?.rumors_filtered || 47}`, unit: 'Blocked', detail: 'Crowd reports capped at +2.6 to prevent unverified panic detours.', icon: ShieldCheck, style: 'border-amber-200 bg-amber-50 text-amber-700' },
    { label: 'COMMUTE DELAY AVERTED', value: `${stats?.commute_delay_averted_min || 27.4}`, unit: 'min/rider', detail: 'Average delay saved when passengers accept dynamic rerouting.', icon: Clock3, style: 'border-sky-200 bg-sky-50 text-sky-700' },
    { label: 'AVG COMMUTE COST', value: stats?.avg_commute_cost_inr ? `₹${Number(stats.avg_commute_cost_inr).toFixed(2)}` : '₹38.50', unit: `-${stats?.cab_savings_percent || 78}% vs Cab`, detail: 'Public bus + train integration guarantees hard budget constraints.', icon: Wallet, style: 'border-purple-200 bg-purple-50 text-purple-700' },
  ];

  return (
    <section className="space-y-6 text-slate-800">
      <header>
        <h1 className="text-2xl font-extrabold tracking-tight sm:text-3xl">Multimodal Transit Analytics &amp; Vulnerability Matrix</h1>
        <p className="mt-1 text-sm text-slate-500">Illustrative pilot reference metrics for transit reliability, carbon impact, and corridor-level fault patterns — not live analytics telemetry.</p>
      </header>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {metricCards.map(({ label, value, unit, detail, icon: Icon, style }) => (
          <article key={label} className={`rounded-3xl border p-5 shadow-sm ${style}`}>
            <div className="flex items-center gap-2 text-[11px] font-extrabold tracking-wide">
              <Icon className="h-4 w-4" /> {label}
            </div>
            <div className="mt-3 flex items-baseline gap-2">
              <strong className="text-3xl font-extrabold text-slate-900">{value}</strong>
              <span className="text-sm font-bold">{unit}</span>
            </div>
            <p className="mt-2 text-xs leading-relaxed text-slate-600">{detail}</p>
          </article>
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-12">
        <article className="rounded-3xl border border-emerald-200 bg-emerald-50/70 p-5 shadow-sm xl:col-span-7">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h2 className="flex items-center gap-2 font-bold"><Leaf className="h-4 w-4 text-emerald-600" /> SDG 13: Emissions by Mode of Transport</h2>
              <p className="mt-1 text-xs text-slate-500">Grams of CO₂ generated per passenger per kilometer across Mumbai.</p>
            </div>
            <span className="rounded-full border border-emerald-200 bg-emerald-100 px-3 py-1 text-[11px] font-bold text-emerald-700">-81.3% Eco-Efficiency</span>
          </div>
          <div className="mt-6 space-y-4">
            {emissions.map((item) => (
              <div key={item.mode}>
                <div className={`mb-1 flex items-center justify-between gap-2 text-xs font-bold ${item.text}`}>
                  <span>{item.icon} {item.mode}</span>
                  <span className="shrink-0 text-slate-700">{item.grams} g CO₂/km</span>
                </div>
                <div className="h-3 overflow-hidden rounded-full bg-slate-200">
                  <div className={`h-full rounded-full ${item.color}`} style={{ width: `${Math.max((item.grams / 150) * 100, item.grams === 0 ? 2 : 4)}%` }} />
                </div>
              </div>
            ))}
          </div>
          <p className="mt-5 rounded-2xl border border-emerald-200 bg-emerald-100/80 p-4 text-xs leading-relaxed text-emerald-800">
            <strong>Environmental Impact:</strong> The pilot reference journey routes 94% of user kilometers onto electrified rail, metro, or clean walking corridors.
          </p>
        </article>

        <article className="rounded-3xl border border-indigo-200 bg-indigo-50/70 p-5 shadow-sm xl:col-span-5">
          <h2 className="flex items-center gap-2 font-bold"><ShieldCheck className="h-4 w-4 text-indigo-600" /> Bayesian Confidence Mechanics</h2>
          <p className="mt-1 text-xs text-slate-500">Evidence accumulation and the crowd-report guardrail.</p>
          <div className="mt-5 divide-y divide-indigo-100 rounded-2xl border border-indigo-100 bg-white/80 px-4">
            {[
              ['Base Prior ($P_0$)', '10% ($L_0 = -2.197$)', 'text-slate-700'],
              ['1 Crowd Report', '+0.8 weight (P* ≈ 42%)', 'text-amber-600'],
              ['Crowd Cap Guardrail', '+2.6 Max (P* ≤ 59.9%)', 'text-rose-600'],
              ['Reroute Threshold', 'P* ≥ 0.65 (65%)', 'text-emerald-600'],
            ].map(([label, value, color]) => (
              <div key={label} className="flex flex-wrap justify-between gap-2 py-3 text-xs">
                <span className="text-slate-500">{label}</span><strong className={color}>{value}</strong>
              </div>
            ))}
          </div>
          <div className="mt-4 rounded-2xl border border-indigo-200 bg-indigo-100/80 p-4">
            <h3 className="text-xs font-extrabold text-indigo-800">Why Passengers Never Suffer Rumor Reroutes</h3>
            <p className="mt-1 text-xs leading-relaxed text-indigo-700">Crowd submissions are capped at +2.6. Without corroboration from official transit advisories or local news, a crowd-only report cannot reach the reroute threshold.</p>
          </div>
        </article>
      </div>

      <article className="rounded-3xl border border-rose-200 bg-rose-50/60 p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="flex items-center gap-2 font-bold"><TriangleAlert className="h-4 w-4 text-rose-500" /> Vulnerability Matrix: Mode vs. Regional Problem Types</h2>
            <p className="mt-1 text-xs text-slate-500">Pilot corridor fault profiles across Mumbai transit hubs.</p>
          </div>
          <div className="flex gap-1 rounded-xl border border-slate-200 bg-white p-1">
            {(['ALL', 'RAIL', 'METRO', 'BUS'] as const).map((mode) => (
              <button key={mode} onClick={() => setFilter(mode)} className={`rounded-lg px-3 py-1.5 text-[11px] font-bold ${filter === mode ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'}`}>{mode}</button>
            ))}
          </div>
        </div>
        <div className="mt-5 overflow-x-auto">
          <table className="w-full min-w-[780px] border-collapse text-left text-xs">
            <thead className="text-[10px] uppercase tracking-wide text-slate-400">
              <tr>{['Corridor / Hub', 'Mode', 'Dominant Failure Pattern', 'Risk Level', 'Avg Delay', 'Root Cause'].map((heading) => <th key={heading} className="border-b border-slate-200 px-2 py-3">{heading}</th>)}</tr>
            </thead>
            <tbody>
              {filteredCorridors.map((row) => (
                <tr key={row.corridor} className="border-b border-rose-100 last:border-0">
                  <td className="px-2 py-3 font-bold text-slate-800">{row.corridor}</td>
                  <td className="px-2 py-3"><span className="rounded-md bg-indigo-100 px-2 py-1 font-bold text-indigo-700">{row.mode}</span></td>
                  <td className="px-2 py-3">{row.issue}</td>
                  <td className="px-2 py-3"><span className={`rounded-full px-2 py-1 text-[10px] font-extrabold ${row.risk === 'CRITICAL' ? 'bg-rose-100 text-rose-600' : row.risk === 'HIGH' ? 'bg-amber-100 text-amber-700' : 'bg-slate-200 text-slate-700'}`}>{row.risk}</span></td>
                  <td className="px-2 py-3 font-bold">{row.delay}</td>
                  <td className="px-2 py-3 text-slate-500">{row.cause}</td>
                </tr>
              ))}
              {filteredCorridors.length === 0 && <tr><td colSpan={6} className="px-2 py-8 text-center text-slate-500"><Activity className="mx-auto mb-2 h-4 w-4" />No corridor reference rows for this mode.</td></tr>}
            </tbody>
          </table>
        </div>
      </article>
    </section>
  );
}

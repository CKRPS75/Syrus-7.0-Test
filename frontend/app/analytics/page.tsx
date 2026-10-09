'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Compass,
  Sparkles,
  AlertTriangle,
  BarChart3,
  Leaf,
  ShieldCheck,
  TrendingDown,
  Clock,
  MapPin,
  ArrowRight,
  Sun,
  Moon,
  Train,
  Bus,
  Footprints,
  IndianRupee,
  Activity,
  Layers,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
} from 'lucide-react';

export default function AnalyticsDashboardPage() {
  const pathname = usePathname();
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [selectedRegionFilter, setSelectedRegionFilter] = useState<'ALL' | 'RAIL' | 'METRO' | 'BUS'>('ALL');

  const toggleTheme = () => {
    const root = document.documentElement;
    if (isDarkMode) {
      root.classList.remove('dark');
      setIsDarkMode(false);
    } else {
      root.classList.add('dark');
      setIsDarkMode(true);
    }
  };

  // Mock Vulnerability Dataset
  const vulnerabilityData = [
    {
      corridor: 'Kurla Interchange (Central/Harbour)',
      mode: 'RAIL',
      dominantFailure: 'Signal Interlocking & Track Flooding',
      riskLevel: 'CRITICAL',
      avgDelayMin: 34,
      monthlyIncidents: 28,
      primaryCause: 'Low track elevation + high interlocking switch density',
    },
    {
      corridor: 'Ghatkopar Metro Station (East-West)',
      mode: 'METRO',
      dominantFailure: 'Door Obstruction & Platform Overcrowding',
      riskLevel: 'HIGH',
      avgDelayMin: 18,
      monthlyIncidents: 21,
      primaryCause: 'Crush load surge from Central Railway transfers',
    },
    {
      corridor: 'BKC Feeder Arterial (SCLR & Connector)',
      mode: 'BUS',
      dominantFailure: 'Surface Gridlock & Bus Bunching',
      riskLevel: 'HIGH',
      avgDelayMin: 26,
      monthlyIncidents: 33,
      primaryCause: 'Narrow entry funnels into corporate financial hub',
    },
    {
      corridor: 'Dadar Junction Forecourt',
      mode: 'RAIL',
      dominantFailure: 'Footpath Blockage & Wheelchair Inaccessibility',
      riskLevel: 'MEDIUM',
      avgDelayMin: 12,
      monthlyIncidents: 14,
      primaryCause: 'Encroached station exits and broken pedestrian curbs',
    },
    {
      corridor: 'Andheri Subway & West Approach',
      mode: 'BUS',
      dominantFailure: 'Monsoon Sump Waterlogging',
      riskLevel: 'CRITICAL',
      avgDelayMin: 45,
      monthlyIncidents: 19,
      primaryCause: 'Underpass drainage saturation forcing multi-km detours',
    },
  ];

  const filteredVulnerabilities = vulnerabilityData.filter((item) => {
    if (selectedRegionFilter === 'ALL') return true;
    return item.mode === selectedRegionFilter;
  });

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col md:flex-row transition-colors">
      {/* -------------------- SIDEBAR NAVIGATION -------------------- */}
      <aside className="w-full md:w-64 bg-white dark:bg-slate-900/90 border-r border-slate-200 dark:border-slate-800 p-5 flex flex-col justify-between shrink-0">
        <div className="space-y-6">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 p-0.5 shadow-md group-hover:scale-105 transition-all">
              <div className="w-full h-full bg-white dark:bg-slate-950 rounded-[14px] flex items-center justify-center">
                <Compass className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              </div>
            </div>
            <div>
              <h1 className="text-base font-extrabold tracking-tight text-slate-900 dark:text-white">
                TrustRoute
              </h1>
              <span className="text-[10px] font-semibold text-indigo-600 dark:text-indigo-400 block -mt-0.5">
                Mumbai Mobility Lab
              </span>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="space-y-1.5 text-xs font-semibold">
            <Link
              href="/"
              className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition ${
                pathname === '/'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              <Compass className="w-4 h-4" />
              <span>Route Planner</span>
            </Link>

            <Link
              href="/#tourist"
              className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
            >
              <Sparkles className="w-4 h-4 text-amber-500" />
              <span>Tourist Day Optimizer</span>
            </Link>

            <Link
              href="/report"
              className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition ${
                pathname === '/report'
                  ? 'bg-rose-600 text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              <AlertTriangle className="w-4 h-4 text-rose-500" />
              <span>Report Anomaly</span>
            </Link>

            <Link
              href="/analytics"
              className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 font-bold border border-indigo-500/20 shadow-xs"
            >
              <BarChart3 className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              <span>Analytics & Stats</span>
            </Link>
          </nav>
        </div>

        {/* Sidebar Footer Controls */}
        <div className="pt-6 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
            <p className="font-bold text-slate-700 dark:text-slate-200">MMRDA CTS 2026</p>
            <p>Live Ingestion Active</p>
          </div>
          <button
            type="button"
            onClick={toggleTheme}
            className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:scale-105 active:scale-95 transition"
            title="Toggle Light/Dark Theme"
          >
            {isDarkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-indigo-600" />}
          </button>
        </div>
      </aside>

      {/* -------------------- MAIN DASHBOARD CONTENT -------------------- */}
      <main className="flex-1 p-4 sm:p-8 space-y-8 overflow-y-auto max-w-7xl mx-auto w-full">
        {/* Header */}
        <div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white tracking-tight">
            Multimodal Transit Analytics &amp; Vulnerability Matrix
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Real-time Bayesian reliability tracking, SDG 13 carbon abatement metrics, and corridor-level fault profiling.
          </p>
        </div>

        {/* -------------------- TIER 1: HIGH-LEVEL KPIS -------------------- */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-1.5">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Leaf className="w-3.5 h-3.5 text-emerald-500" /> Net CO₂ Abatement
            </span>
            <div className="text-2xl font-extrabold text-slate-900 dark:text-white">
              -1,842 <span className="text-sm font-semibold text-emerald-500">kg</span>
            </div>
            <p className="text-[10px] text-slate-500 leading-tight">
              Equivalent to <strong>88 trees planted</strong> vs. private cab baselines.
            </p>
          </div>

          <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-1.5">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-indigo-500" /> Rumors Filtered
            </span>
            <div className="text-2xl font-extrabold text-slate-900 dark:text-white">
              47 <span className="text-sm font-semibold text-amber-500">Blocked</span>
            </div>
            <p className="text-[10px] text-slate-500 leading-tight">
              Crowd reports capped at +2.6 to prevent unverified panic detours.
            </p>
          </div>

          <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-1.5">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-sky-500" /> Commute Delay Averted
            </span>
            <div className="text-2xl font-extrabold text-slate-900 dark:text-white">
              27.4 <span className="text-sm font-semibold text-sky-500">min/rider</span>
            </div>
            <p className="text-[10px] text-slate-500 leading-tight">
              Average delay saved when passengers accept dynamic rerouting.
            </p>
          </div>

          <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-1.5">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <IndianRupee className="w-3.5 h-3.5 text-amber-500" /> Avg Commute Cost
            </span>
            <div className="text-2xl font-extrabold text-slate-900 dark:text-white">
              ₹38.50 <span className="text-sm font-semibold text-emerald-500">-78% vs Cab</span>
            </div>
            <p className="text-[10px] text-slate-500 leading-tight">
              Public bus + train integration guarantees hard budget constraints.
            </p>
          </div>
        </div>

        {/* -------------------- TIER 2: CARBON OFFSET & ENVIRONMENTAL ANALYTICS -------------------- */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Carbon Abatement Comparison Breakdown */}
          <div className="lg:col-span-7 bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-5">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <Leaf className="w-4 h-4 text-emerald-500" />
                  SDG 13: Emissions by Mode of Transport
                </h3>
                <p className="text-[11px] text-slate-500">
                  Grams of CO₂ generated per passenger per kilometer across Mumbai.
                </p>
              </div>
              <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                -81.3% Eco-Efficiency
              </span>
            </div>

            {/* Visual Bars Comparison */}
            <div className="space-y-3.5 text-xs">
              <div>
                <div className="flex justify-between font-semibold mb-1">
                  <span className="flex items-center gap-1.5 text-rose-600 dark:text-rose-400">
                    Ride-Hail Cab / Private Car (Baseline)
                  </span>
                  <span>150 g CO₂/km</span>
                </div>
                <div className="w-full h-3 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-rose-500 rounded-full w-full" />
                </div>
              </div>

              <div>
                <div className="flex justify-between font-semibold mb-1">
                  <span className="flex items-center gap-1.5 text-amber-600 dark:text-amber-400">
                    <Bus className="w-3.5 h-3.5" /> BEST Diesel/CNG Bus
                  </span>
                  <span>38 g CO₂/km</span>
                </div>
                <div className="w-full h-3 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-amber-500 rounded-full w-[25%]" />
                </div>
              </div>

              <div>
                <div className="flex justify-between font-semibold mb-1">
                  <span className="flex items-center gap-1.5 text-sky-600 dark:text-sky-400">
                    <Train className="w-3.5 h-3.5" /> Mumbai Metro (Line 1/2A/7)
                  </span>
                  <span>22 g CO₂/km</span>
                </div>
                <div className="w-full h-3 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-sky-500 rounded-full w-[14.6%]" />
                </div>
              </div>

              <div>
                <div className="flex justify-between font-semibold mb-1">
                  <span className="flex items-center gap-1.5 text-indigo-600 dark:text-indigo-400">
                    <Train className="w-3.5 h-3.5" /> Suburban Electric Railway
                  </span>
                  <span>18 g CO₂/km</span>
                </div>
                <div className="w-full h-3 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-500 rounded-full w-[12%]" />
                </div>
              </div>

              <div>
                <div className="flex justify-between font-semibold mb-1">
                  <span className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
                    <Footprints className="w-3.5 h-3.5" /> Pedestrian / Walking
                  </span>
                  <span>0 g CO₂/km</span>
                </div>
                <div className="w-full h-3 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-500 rounded-full w-[2%]" />
                </div>
              </div>
            </div>

            <div className="p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-[11px] text-emerald-800 dark:text-emerald-300 leading-relaxed">
              <strong>Environmental Impact:</strong> TrustRoute journeys route <strong>94%</strong> of user kilometers onto electrified rail, metro, or clean walking corridors, reducing daily urban travel emissions by more than four-fifths compared to surface vehicular congestion.
            </div>
          </div>

          {/* Bayesian Trust Threshold Math Preview */}
          <div className="lg:col-span-5 bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-indigo-500" />
                Bayesian Confidence Mechanics
              </h3>
              <p className="text-[11px] text-slate-500">
                Logit evidence accumulation curve and rumor prevention cap.
              </p>
            </div>

            <div className="bg-slate-50 dark:bg-slate-800/60 p-3 rounded-2xl border border-slate-200 dark:border-slate-700/60 space-y-2 text-xs">
              <div className="flex justify-between items-center py-1 border-b border-slate-200 dark:border-slate-700">
                <span className="text-slate-500">Base Prior ($P_0$):</span>
                <span className="font-mono font-bold">10% ($L_0 = -2.197$)</span>
              </div>
              <div className="flex justify-between items-center py-1 border-b border-slate-200 dark:border-slate-700">
                <span className="text-slate-500">1 Crowd Report:</span>
                <span className="font-mono font-bold text-amber-500">+0.8 weight (P* ≈ 42%)</span>
              </div>
              <div className="flex justify-between items-center py-1 border-b border-slate-200 dark:border-slate-700">
                <span className="text-slate-500">Crowd Cap Guardrail:</span>
                <span className="font-mono font-bold text-rose-500">+2.6 Max (P* ≤ 59.9%)</span>
              </div>
              <div className="flex justify-between items-center py-1">
                <span className="text-slate-500">Reroute Threshold:</span>
                <span className="font-mono font-bold text-emerald-500">P* ≥ 0.65 (65%)</span>
              </div>
            </div>

            <div className="p-3 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-[11px] text-indigo-800 dark:text-indigo-300 space-y-1">
              <p className="font-bold">Why Passengers Never Suffer Rumor Reroutes:</p>
              <p className="leading-relaxed">
                Because crowd submissions are mathematically capped at +2.6, no matter how many duplicate reports are filed, the posterior probability can never exceed 59.9% without corroboration from official transit advisory feeds (+3.0) or local news GDELT sensors (+1.5).
              </p>
            </div>
          </div>
        </div>

        {/* -------------------- TIER 3: MODE & REGIONAL FAILURE VULNERABILITY MATRIX -------------------- */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-rose-500" />
                Vulnerability Matrix: Mode vs. Regional Problem Types
              </h3>
              <p className="text-[11px] text-slate-500">
                Historical fault profiling across Mumbai’s critical transit corridors (MMRDA CTS &amp; GTFS telemetry).
              </p>
            </div>

            {/* Filter Tabs */}
            <div className="flex bg-slate-100 dark:bg-slate-800 p-1 rounded-xl text-xs font-bold">
              {(['ALL', 'RAIL', 'METRO', 'BUS'] as const).map((filter) => (
                <button
                  key={filter}
                  onClick={() => setSelectedRegionFilter(filter)}
                  className={`px-3 py-1.5 rounded-lg transition ${
                    selectedRegionFilter === filter
                      ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  {filter}
                </button>
              ))}
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800 text-[11px] text-slate-400 font-bold uppercase tracking-wider">
                  <th className="py-3 px-3">Corridor / Hub</th>
                  <th className="py-3 px-3">Mode</th>
                  <th className="py-3 px-3">Dominant Failure Pattern</th>
                  <th className="py-3 px-3">Risk Level</th>
                  <th className="py-3 px-3">Avg Delay</th>
                  <th className="py-3 px-3">Root Cause</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-medium">
                {filteredVulnerabilities.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition">
                    <td className="py-3 px-3 font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                      <MapPin className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
                      <span>{row.corridor}</span>
                    </td>
                    <td className="py-3 px-3">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          row.mode === 'METRO'
                            ? 'bg-sky-500/10 text-sky-600 dark:text-sky-300'
                            : row.mode === 'RAIL'
                            ? 'bg-indigo-500/10 text-indigo-600 dark:text-indigo-300'
                            : 'bg-green-500/10 text-green-600 dark:text-green-300'
                        }`}
                      >
                        {row.mode}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-slate-700 dark:text-slate-300">
                      {row.dominantFailure}
                    </td>
                    <td className="py-3 px-3">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          row.riskLevel === 'CRITICAL'
                            ? 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20'
                            : row.riskLevel === 'HIGH'
                            ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20'
                            : 'bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300'
                        }`}
                      >
                        {row.riskLevel}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-bold text-slate-900 dark:text-white">
                      +{row.avgDelayMin}m
                    </td>
                    <td className="py-3 px-3 text-slate-500 dark:text-slate-400 text-[11px]">
                      {row.primaryCause}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}
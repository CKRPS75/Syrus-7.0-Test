'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  ArrowLeft,
  AlertTriangle,
  Send,
  Bus,
  Train,
  CheckCircle2,
  ShieldCheck,
  Sun,
  Moon,
  Info,
} from 'lucide-react';
import { AnomalyType } from '../../types';

export default function ReportAnomalyPage() {
  const router = useRouter();
  const [isDarkMode, setIsDarkMode] = useState(true);

  // Form Fields
  const [mode, setMode] = useState<'METRO' | 'BUS' | 'TRAIN'>('METRO');
  const [anomalyType, setAnomalyType] = useState<AnomalyType>('VEHICLE_BREAKDOWN');
  const [lineOrIdentifier, setLineOrIdentifier] = useState('Metro Line 1 (Blue Line)');
  const [stationOrLocation, setStationOrLocation] = useState('Ghatkopar Station West');
  const [direction, setDirection] = useState('Towards Andheri / Versova');
  const [severity, setSeverity] = useState<'LOW' | 'MEDIUM' | 'HIGH'>('HIGH');
  const [estimatedDelayMin, setEstimatedDelayMin] = useState(25);
  const [description, setDescription] = useState('');
  const [isWheelchairImpacted, setIsWheelchairImpacted] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  // Theme Sync
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

  const handleModeChange = (selectedMode: 'METRO' | 'BUS' | 'TRAIN') => {
    setMode(selectedMode);
    if (selectedMode === 'METRO') {
      setLineOrIdentifier('Metro Line 1 (Blue Line)');
      setStationOrLocation('Ghatkopar Metro Station');
      setDirection('Towards Andheri / Versova');
    } else if (selectedMode === 'BUS') {
      setLineOrIdentifier('BEST Bus 365');
      setStationOrLocation('Chembur Naka Bus Depot');
      setDirection('Towards Ghatkopar Station');
    } else {
      setLineOrIdentifier('Western Suburban Line (Slow)');
      setStationOrLocation('Bandra Station Platform 2');
      setDirection('Towards Churchgate');
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitted(true);

    const reportData = {
      id: `USR-${Date.now()}`,
      mode,
      anomalyType,
      lineOrIdentifier,
      stationOrLocation,
      direction,
      severity,
      estimatedDelayMin,
      description:
        description ||
        `Reported ${anomalyType.replace('_', ' ').toLowerCase()} at ${stationOrLocation}`,
      isWheelchairImpacted,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    try {
      const existing = JSON.parse(localStorage.getItem('trustroute_crowd_reports') || '[]');
      localStorage.setItem('trustroute_crowd_reports', JSON.stringify([reportData, ...existing]));
    } catch (err) {
      console.error('Could not save to localStorage', err);
    }

    setTimeout(() => {
      router.push('/');
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors p-4 sm:p-6 relative overflow-hidden">
      {/* Background Ambient Glow */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-gradient-to-tr from-indigo-500/20 to-fuchsia-500/20 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-gradient-to-br from-cyan-500/20 to-blue-600/20 rounded-full blur-[140px] pointer-events-none" />

      {/* Top Bar */}
      <header className="max-w-5xl mx-auto flex items-center justify-between pb-6 border-b border-slate-200 dark:border-slate-800">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-xs font-bold text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-white transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Route Dashboard</span>
        </Link>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={toggleTheme}
            className="p-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:scale-105 active:scale-95 transition shadow-sm"
            title="Toggle Light/Dark Theme"
          >
            {isDarkMode ? (
              <Sun className="w-4 h-4 text-amber-400" />
            ) : (
              <Moon className="w-4 h-4 text-indigo-600" />
            )}
          </button>
        </div>
      </header>

      {/* Main Content Form */}
      <main className="max-w-5xl mx-auto mt-6 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Input Form */}
        <div className="lg:col-span-7 bg-white dark:bg-slate-900/80 backdrop-blur-xl border border-slate-200 dark:border-slate-800 p-6 sm:p-8 rounded-3xl shadow-sm">
          {isSubmitted ? (
            <div className="py-16 text-center space-y-3">
              <div className="w-16 h-16 bg-emerald-500/20 text-emerald-500 rounded-full flex items-center justify-center mx-auto border border-emerald-500/30">
                <CheckCircle2 className="w-10 h-10" />
              </div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                Report Logged in Trust Engine
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
                Assigned initial crowd evidence weight (+0.8). Redirecting you back to the journey map...
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4 text-xs">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-2xl bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20">
                  <AlertTriangle className="w-5 h-5" />
                </div>
                <div>
                  <h1 className="text-lg font-bold text-slate-900 dark:text-white">
                    Report Transit Anomaly
                  </h1>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">
                    Submit real-time ground truth to help protect fellow Mumbai commuters
                  </p>
                </div>
              </div>

              {/* Transit Mode Selection */}
              <div>
                <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1.5">
                  1. Transit Mode
                </label>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    type="button"
                    onClick={() => handleModeChange('METRO')}
                    className={`py-2 px-3 rounded-xl border font-bold flex items-center justify-center gap-1.5 transition ${
                      mode === 'METRO'
                        ? 'bg-sky-600 text-white border-sky-600 shadow-sm'
                        : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700 hover:border-slate-300'
                    }`}
                  >
                    <Train className="w-4 h-4" /> Metro
                  </button>
                  <button
                    type="button"
                    onClick={() => handleModeChange('BUS')}
                    className={`py-2 px-3 rounded-xl border font-bold flex items-center justify-center gap-1.5 transition ${
                      mode === 'BUS'
                        ? 'bg-green-600 text-white border-green-600 shadow-sm'
                        : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700 hover:border-slate-300'
                    }`}
                  >
                    <Bus className="w-4 h-4" /> BEST Bus
                  </button>
                  <button
                    type="button"
                    onClick={() => handleModeChange('TRAIN')}
                    className={`py-2 px-3 rounded-xl border font-bold flex items-center justify-center gap-1.5 transition ${
                      mode === 'TRAIN'
                        ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm'
                        : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700 hover:border-slate-300'
                    }`}
                  >
                    <Train className="w-4 h-4" /> Local Train
                  </button>
                </div>
              </div>

              {/* Anomaly Category */}
              <div>
                <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">
                  2. Incident Category
                </label>
                <select
                  value={anomalyType}
                  onChange={(e) => setAnomalyType(e.target.value as AnomalyType)}
                  className="w-full px-3 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="VEHICLE_BREAKDOWN">Vehicle / Technical Breakdown</option>
                  <option value="TRIP_CANCELLED">Service / Trip Cancelled</option>
                  <option value="SEVERE_TRAFFIC">Severe Traffic Jam / Road Bottleneck</option>
                  <option value="OVERCROWDING">Station Overcrowding / Boarding Not Possible</option>
                  <option value="SIGNAL_FAILURE">Signal / Interlocking Malfunction</option>
                  <option value="WATERLOGGING">Monsoon Waterlogging / Flooded Track</option>
                  <option value="ROUTE_DIVERSION">Bus Diverted from Stated Stops</option>
                </select>
              </div>

              {/* Line and Station Details */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">
                    3. Line / Route Number
                  </label>
                  <input
                    type="text"
                    value={lineOrIdentifier}
                    onChange={(e) => setLineOrIdentifier(e.target.value)}
                    placeholder="e.g. Metro Line 1, BEST 365"
                    className="w-full px-3 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    required
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">
                    4. Station / Exact Location
                  </label>
                  <input
                    type="text"
                    value={stationOrLocation}
                    onChange={(e) => setStationOrLocation(e.target.value)}
                    placeholder="e.g. Ghatkopar West, Saki Naka"
                    className="w-full px-3 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    required
                  />
                </div>
              </div>

              {/* Direction & Delay */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">
                    5. Direction of Travel
                  </label>
                  <input
                    type="text"
                    value={direction}
                    onChange={(e) => setDirection(e.target.value)}
                    placeholder="e.g. Towards Churchgate / Versova"
                    className="w-full px-3 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">
                    6. Estimated Delay (Minutes)
                  </label>
                  <input
                    type="number"
                    value={estimatedDelayMin}
                    onChange={(e) => setEstimatedDelayMin(Number(e.target.value))}
                    min={1}
                    max={180}
                    className="w-full px-3 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    required
                  />
                </div>
              </div>

              {/* Severity Pill Selector */}
              <div>
                <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1.5">
                  7. Severity Level
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(['LOW', 'MEDIUM', 'HIGH'] as const).map((lvl) => (
                    <button
                      type="button"
                      key={lvl}
                      onClick={() => setSeverity(lvl)}
                      className={`py-2 rounded-xl font-bold border transition text-[11px] ${
                        severity === lvl
                          ? lvl === 'HIGH'
                            ? 'bg-rose-600 text-white border-rose-600'
                            : lvl === 'MEDIUM'
                            ? 'bg-amber-500 text-white border-amber-500'
                            : 'bg-emerald-600 text-white border-emerald-600'
                          : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700'
                      }`}
                    >
                      {lvl}
                    </button>
                  ))}
                </div>
              </div>

              {/* Free-text Description */}
              <div>
                <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">
                  8. Ground Truth Description
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Detail visible evidence (e.g. overhead wire snapping, escalator blocked, station master announcement)..."
                  rows={3}
                  className="w-full px-3 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                  required
                />
              </div>

              {/* Accessibility Checkbox */}
              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="wheelchair"
                  checked={isWheelchairImpacted}
                  onChange={(e) => setIsWheelchairImpacted(e.target.checked)}
                  className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 w-4 h-4 cursor-pointer"
                />
                <label htmlFor="wheelchair" className="text-slate-700 dark:text-slate-300 font-medium cursor-pointer">
                  Disruption breaks lifts, ramps, or wheelchair accessibility
                </label>
              </div>

              <button
                type="submit"
                className="w-full mt-3 py-3.5 rounded-2xl bg-gradient-to-r from-rose-600 to-indigo-600 hover:from-rose-500 hover:to-indigo-500 text-white font-bold text-xs shadow-lg shadow-rose-600/20 transition flex items-center justify-center gap-2"
              >
                <Send className="w-4 h-4" />
                <span>Submit to Trust Engine</span>
              </button>
            </form>
          )}
        </div>

        {/* Right Column: Live Trust Pipeline Inspector */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-white dark:bg-slate-900/80 backdrop-blur-xl border border-slate-200 dark:border-slate-800 p-6 rounded-3xl shadow-sm text-xs space-y-4">
            <span className="font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider flex items-center gap-1.5 text-[11px]">
              <ShieldCheck className="w-4 h-4" />
              Bayesian Evidence Pipeline Preview
            </span>

            <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
              Your report will be ingested as a raw evidence signal. Here is how the Trust Engine processes it:
            </p>

            <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-200 dark:border-slate-700/60 space-y-2">
              <div className="flex justify-between font-semibold">
                <span className="text-slate-500 dark:text-slate-400">Signal Contribution:</span>
                <span className="text-indigo-600 dark:text-indigo-400 font-bold">+0.8 Evidence Weight</span>
              </div>
              <div className="flex justify-between font-semibold">
                <span className="text-slate-500 dark:text-slate-400">Crowd Cap Guardrail:</span>
                <span className="text-slate-700 dark:text-slate-200">+2.6 Maximum Total</span>
              </div>
              <div className="flex justify-between font-semibold">
                <span className="text-slate-500 dark:text-slate-400">Confirmation Threshold:</span>
                <span className="text-emerald-600 dark:text-emerald-400">P* ≥ 0.65</span>
              </div>
              <div className="flex justify-between font-semibold">
                <span className="text-slate-500 dark:text-slate-400">Initial Status:</span>
                <span className="text-amber-500 font-bold">WATCH (Warning Only)</span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-800 dark:text-indigo-300 flex items-start gap-2 text-[11px] leading-relaxed">
              <Info className="w-4 h-4 shrink-0 mt-0.5" />
              <span>
                <strong>Sybil &amp; Rumor Protection:</strong> A single crowd report triggers a `WATCH` notice. It requires an independent corroborating report or official transit feed to reach `CONFIRMED` before any route is dynamically replanned.
              </span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
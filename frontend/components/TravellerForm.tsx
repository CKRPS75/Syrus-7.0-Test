'use client';

import React, { useState } from 'react';
import { TravellerConstraints } from '../types';
import { Search } from 'lucide-react';

interface TravellerFormProps {
  onSubmit: (constraints: TravellerConstraints) => void;
}

export default function TravellerForm({ onSubmit }: TravellerFormProps) {
  const [origin, setOrigin] = useState('Chembur');
  const [destination, setDestination] = useState('Andheri');
  const [departureTime, setDepartureTime] = useState('17:00');
  const [deadline, setDeadline] = useState('19:00');
  const [budget, setBudget] = useState(80);
  const [maxWalkingMeters, setMaxWalkingMeters] = useState(1000);
  const [accessibilityRequired, setAccessibilityRequired] = useState(false);
  const [allowedModes, setAllowedModes] = useState<('BUS' | 'METRO' | 'WALK')[]>([
    'BUS',
    'METRO',
    'WALK',
  ]);

  const toggleMode = (mode: 'BUS' | 'METRO' | 'WALK') => {
    setAllowedModes((prev) =>
      prev.includes(mode) ? prev.filter((m) => m !== mode) : [...prev, mode]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      origin,
      destination,
      departureTime,
      deadline,
      budget,
      maxWalkingMeters,
      accessibilityRequired,
      allowedModes,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 text-xs">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">
            Origin
          </label>
          <input
            type="text"
            value={origin}
            onChange={(e) => setOrigin(e.target.value)}
            className="w-full px-3 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
            required
          />
        </div>
        <div>
          <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">
            Destination
          </label>
          <input
            type="text"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            className="w-full px-3 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">
            Departure
          </label>
          <input
            type="text"
            value={departureTime}
            onChange={(e) => setDepartureTime(e.target.value)}
            className="w-full px-3 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
          />
        </div>
        <div>
          <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">
            Deadline
          </label>
          <input
            type="text"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
            className="w-full px-3 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">
            Max Budget (₹)
          </label>
          <input
            type="number"
            value={budget}
            onChange={(e) => setBudget(Number(e.target.value))}
            className="w-full px-3 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
          />
        </div>
        <div>
          <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">
            Max Walk (meters)
          </label>
          <input
            type="number"
            value={maxWalkingMeters}
            onChange={(e) => setMaxWalkingMeters(Number(e.target.value))}
            className="w-full px-3 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
          />
        </div>
      </div>

      <div>
        <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-2">
          Permitted Transit Modes
        </label>
        <div className="flex gap-2">
          {(['BUS', 'METRO', 'WALK'] as const).map((mode) => (
            <button
              type="button"
              key={mode}
              onClick={() => toggleMode(mode)}
              className={`px-4 py-2 rounded-xl font-bold transition shadow-sm ${
                allowedModes.includes(mode)
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700 hover:border-indigo-400'
              }`}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-2 pt-1">
        <input
          type="checkbox"
          id="access"
          checked={accessibilityRequired}
          onChange={(e) => setAccessibilityRequired(e.target.checked)}
          className="rounded border-slate-300 dark:border-slate-700 text-indigo-600 focus:ring-indigo-500 w-4 h-4 cursor-pointer"
        />
        <label htmlFor="access" className="text-slate-700 dark:text-slate-300 font-medium cursor-pointer">
          Require Step-Free / Wheelchair Accessibility
        </label>
      </div>

      <button
        type="submit"
        className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold py-3.5 rounded-2xl transition shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 text-xs"
      >
        <Search className="w-4 h-4" />
        Find Protected Journey
      </button>
    </form>
  );
}
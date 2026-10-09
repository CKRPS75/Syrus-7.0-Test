'use client';

import React, { useState } from 'react';
import { TravellerConstraints } from '@/types';
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
          <label className="font-semibold text-slate-700 block mb-1">Origin</label>
          <input
            type="text"
            value={origin}
            onChange={(e) => setOrigin(e.target.value)}
            className="w-full px-3 py-2 border rounded-lg focus:outline-indigo-500"
            required
          />
        </div>
        <div>
          <label className="font-semibold text-slate-700 block mb-1">Destination</label>
          <input
            type="text"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            className="w-full px-3 py-2 border rounded-lg focus:outline-indigo-500"
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="font-semibold text-slate-700 block mb-1">Departure</label>
          <input
            type="text"
            value={departureTime}
            onChange={(e) => setDepartureTime(e.target.value)}
            className="w-full px-3 py-2 border rounded-lg focus:outline-indigo-500"
          />
        </div>
        <div>
          <label className="font-semibold text-slate-700 block mb-1">Deadline</label>
          <input
            type="text"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
            className="w-full px-3 py-2 border rounded-lg focus:outline-indigo-500"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="font-semibold text-slate-700 block mb-1">Max Budget (₹)</label>
          <input
            type="number"
            value={budget}
            onChange={(e) => setBudget(Number(e.target.value))}
            className="w-full px-3 py-2 border rounded-lg focus:outline-indigo-500"
          />
        </div>
        <div>
          <label className="font-semibold text-slate-700 block mb-1">Max Walk (meters)</label>
          <input
            type="number"
            value={maxWalkingMeters}
            onChange={(e) => setMaxWalkingMeters(Number(e.target.value))}
            className="w-full px-3 py-2 border rounded-lg focus:outline-indigo-500"
          />
        </div>
      </div>

      <div>
        <label className="font-semibold text-slate-700 block mb-1.5">Transit Modes</label>
        <div className="flex gap-2">
          {(['BUS', 'METRO', 'WALK'] as const).map((mode) => (
            <button
              type="button"
              key={mode}
              onClick={() => toggleMode(mode)}
              className={`px-3 py-1.5 rounded-lg border font-medium ${
                allowedModes.includes(mode)
                  ? 'bg-indigo-600 text-white border-indigo-600'
                  : 'bg-slate-50 text-slate-600 border-slate-200'
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
          className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
        />
        <label htmlFor="access" className="text-slate-700 font-medium">
          Require Step-Free / Wheelchair Accessibility
        </label>
      </div>

      <button
        type="submit"
        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2.5 rounded-xl transition shadow-sm flex items-center justify-center gap-2 text-sm"
      >
        <Search className="w-4 h-4" />
        Find Protected Journey
      </button>
    </form>
  );
}
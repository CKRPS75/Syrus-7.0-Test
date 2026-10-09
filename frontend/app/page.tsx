'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import TravellerForm from '../components/TravellerForm';
import JourneyView from '../components/JourneyView';
import DisruptionBanner from '../components/DisruptionBanner';
import ExplainabilityModal from '../components/ExplainabilityModal';
import RouteComparison from '../components/RouteComparison';
import ConfirmPrompt from '../components/ConfirmPrompt';
import {
  MOCK_BASE_JOURNEY,
  MOCK_DISRUPTION_ALERT,
  MOCK_ALTERNATIVE_JOURNEY,
} from '../lib/mockData';
import { JourneyPlanResponse, DisruptionAlert, TravellerConstraints } from '../types';
import { Compass } from 'lucide-react';

// Dynamically import MapView to disable SSR and prevent WebGL/window crashes
const MapView = dynamic(() => import('../components/MapView'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-80 rounded-xl bg-slate-100 flex items-center justify-center text-xs text-slate-400 border border-slate-200">
      Loading interactive map...
    </div>
  ),
});

export default function Home() {
  const [journey, setJourney] = useState<JourneyPlanResponse | null>(null);
  const [disruption, setDisruption] = useState<DisruptionAlert | null>(null);
  const [showAlternative, setShowAlternative] = useState(false);
  const [isExplainOpen, setIsExplainOpen] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  // Form Submit: generates base route (Mock or Live)
  const handlePlanSubmit = (formData: TravellerConstraints) => {
    setJourney(MOCK_BASE_JOURNEY);
    setShowAlternative(false);

    // Simulate live disruption detection 1.5s after search
    setTimeout(() => {
      setDisruption(MOCK_DISRUPTION_ALERT);
      setShowAlternative(true);
    }, 1500);
  };

  // User confirms alternative reroute
  const handleAcceptReroute = () => {
    setIsUpdating(true);
    setTimeout(() => {
      setJourney(MOCK_ALTERNATIVE_JOURNEY);
      setShowAlternative(false);
      setDisruption(null);
      setIsUpdating(false);
    }, 600);
  };

  // User rejects alternative
  const handleKeepCurrent = () => {
    setShowAlternative(false);
  };

  return (
    <main className="min-h-screen bg-slate-100 py-8 px-4 sm:px-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <header className="flex items-center justify-between bg-white px-6 py-4 rounded-2xl shadow-sm border border-slate-200">
          <div className="flex items-center gap-2.5">
            <div className="bg-indigo-600 text-white p-2 rounded-xl">
              <Compass className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-900 leading-tight">TrustRoute</h1>
              <p className="text-[11px] text-slate-500 font-medium">
                Evidence-Aware Dynamic Multimodal Journey Planner
              </p>
            </div>
          </div>
          <span className="text-xs bg-indigo-50 text-indigo-700 font-semibold px-2.5 py-1 rounded-full border border-indigo-100">
            Mumbai GTFS Pilot
          </span>
        </header>

        {/* Main Grid */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
          {/* Left Column: Input Form & Alternate Decisions */}
          <div className="md:col-span-5 space-y-6">
            <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
              <h2 className="text-sm font-bold text-slate-800 mb-4">Set Constraints</h2>
              <TravellerForm onSubmit={handlePlanSubmit} />
            </div>

            {/* Dynamic Replan Card */}
            {showAlternative && disruption && journey && (
              <div className="space-y-3">
                <RouteComparison
                  currentRoute={journey}
                  alternativeRoute={MOCK_ALTERNATIVE_JOURNEY}
                  delayMin={disruption.delayEstimateMin || 35}
                />
                <ConfirmPrompt
                  onAccept={handleAcceptReroute}
                  onReject={handleKeepCurrent}
                  isLoading={isUpdating}
                />
              </div>
            )}
          </div>

          {/* Right Column: Active Journey View & Map */}
          <div className="md:col-span-7 space-y-4">
            {journey ? (
              <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 space-y-4">
                {/* Disruption Alert Bar */}
                {disruption && (
                  <DisruptionBanner
                    alert={disruption}
                    onOpenExplain={() => setIsExplainOpen(true)}
                  />
                )}

                {/* Map */}
                <MapView legs={journey.legs} />

                {/* Itinerary Steps */}
                <JourneyView journey={journey} />
              </div>
            ) : (
              <div className="bg-white p-12 rounded-2xl shadow-sm border border-dashed border-slate-300 text-center flex flex-col items-center justify-center min-h-[360px]">
                <Compass className="w-10 h-10 text-slate-300 mb-3 animate-pulse" />
                <h3 className="font-semibold text-slate-700 text-sm">No Active Journey</h3>
                <p className="text-xs text-slate-400 mt-1 max-w-xs">
                  Fill in your destination, deadline, and accessibility constraints to test disruption-aware routing.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Explanation Modal */}
      {disruption && (
        <ExplainabilityModal
          isOpen={isExplainOpen}
          onClose={() => setIsExplainOpen(false)}
          alert={disruption}
        />
      )}
    </main>
  );}
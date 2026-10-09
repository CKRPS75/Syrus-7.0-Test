'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import confetti from 'canvas-confetti';
import { motion, AnimatePresence } from 'framer-motion';

import LandingView from '../components/LandingView';
import LoginModal from '../components/LoginModal';
import TravellerForm from '../components/TravellerForm';
import JourneyView from '../components/JourneyView';
import DisruptionBanner from '../components/DisruptionBanner';
import ExplainabilityModal from '../components/ExplainabilityModal';
import RouteComparison from '../components/RouteComparison';
import ConfirmPrompt from '../components/ConfirmPrompt';
import TouristPlanner from '../components/TouristPlanner';

import {
  MOCK_BASE_JOURNEY,
  SCENARIO_CONFIRMED,
  SCENARIO_WATCH_RUMOR,
  SCENARIO_IRRELEVANT,
  MOCK_ALTERNATIVE_JOURNEY,
} from '../lib/mockData';
import { JourneyPlanResponse, DisruptionAlert, TravellerConstraints } from '../types';
import {
  Compass,
  Sun,
  Moon,
  UserCheck,
  LogOut,
  SlidersHorizontal,
  Sparkles,
  Navigation,
  AlertTriangle,
} from 'lucide-react';

const MapView = dynamic(() => import('../components/MapView'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-80 rounded-2xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex items-center justify-center text-xs text-slate-400">
      <div className="flex items-center gap-2">
        <div className="w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        <span>Loading OpenStreetMap Network...</span>
      </div>
    </div>
  ),
});

export default function Home() {
  const [viewState, setViewState] = useState<'LANDING' | 'APP'>('LANDING');
  const [activeTab, setActiveTab] = useState<'COMMUTER' | 'TOURIST_T5'>('COMMUTER');
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState<string | null>(null);
  const [isDarkMode, setIsDarkMode] = useState(true);

  const [journey, setJourney] = useState<JourneyPlanResponse | null>(null);
  const [disruption, setDisruption] = useState<DisruptionAlert | null>(null);
  const [showAlternative, setShowAlternative] = useState(false);
  const [isExplainOpen, setIsExplainOpen] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [currentScenario, setCurrentScenario] = useState<'A' | 'B' | 'C'>('B');

  // Synchronize Dark / Light mode with <html> class
  useEffect(() => {
    const root = document.documentElement;
    if (isDarkMode) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [isDarkMode]);

  const toggleTheme = () => {
    setIsDarkMode((prev) => !prev);
  };

  const handleLoginSuccess = (name: string) => {
    setCurrentUser(name);
    if (name.toLowerCase().includes('tourist') || name.toLowerCase().includes('t5')) {
      setActiveTab('TOURIST_T5');
    } else {
      setActiveTab('COMMUTER');
    }
    setViewState('APP');
  };

  const handlePlanSubmit = (formData: TravellerConstraints) => {
    setJourney(MOCK_BASE_JOURNEY);
    setShowAlternative(false);

    setTimeout(() => {
      triggerScenario(currentScenario);
    }, 800);
  };

  const triggerScenario = (scenario: 'A' | 'B' | 'C') => {
    setCurrentScenario(scenario);
    if (!journey) setJourney(MOCK_BASE_JOURNEY);

    if (scenario === 'A') {
      setDisruption(SCENARIO_CONFIRMED);
      setShowAlternative(true);
    } else if (scenario === 'B') {
      setDisruption(SCENARIO_WATCH_RUMOR);
      setShowAlternative(false);
    } else if (scenario === 'C') {
      setDisruption(SCENARIO_IRRELEVANT);
      setShowAlternative(false);
    }
  };

  const handleAcceptReroute = () => {
    setIsUpdating(true);
    setTimeout(() => {
      setJourney(MOCK_ALTERNATIVE_JOURNEY);
      setShowAlternative(false);
      setDisruption(null);
      setIsUpdating(false);

      confetti({
        particleCount: 75,
        spread: 65,
        origin: { y: 0.6 },
        colors: ['#6366f1', '#ec4899', '#10b981', '#f59e0b'],
      });
    }, 600);
  };

  const handleKeepCurrent = () => {
    setShowAlternative(false);
  };

  return (
    <div className="min-h-screen bg-slate-100 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors">
      {viewState === 'LANDING' ? (
        <LandingView
          onGetStarted={() => setViewState('APP')}
          onLoginClick={() => setIsLoginOpen(true)}
        />
      ) : (
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-6">
          {/* Header */}
          <header className="flex flex-wrap items-center justify-between bg-white dark:bg-slate-900/80 backdrop-blur-xl border border-slate-200 dark:border-slate-800 p-4 rounded-3xl shadow-sm gap-4">
            <div
              onClick={() => setViewState('LANDING')}
              className="flex items-center gap-3 cursor-pointer group"
            >
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 p-0.5 shadow-md group-hover:scale-105 transition-all">
                <div className="w-full h-full bg-white dark:bg-slate-950 rounded-[14px] flex items-center justify-center">
                  <Compass className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                </div>
              </div>
              <div>
                <h1 className="text-base font-extrabold tracking-tight text-slate-900 dark:text-white">
                  TrustRoute Engine
                </h1>
                <span className="text-[10px] font-semibold text-indigo-600 dark:text-indigo-400">
                  Mumbai Multimodal Pilot (BEST + Metro + Local Rail)
                </span>
              </div>
            </div>

            {/* Mode Tabs: Commuter vs Persona T5 Tourist */}
            <div className="flex bg-slate-100 dark:bg-slate-800/90 p-1 rounded-2xl border border-slate-200 dark:border-slate-700">
              <button
                onClick={() => setActiveTab('COMMUTER')}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold transition ${
                  activeTab === 'COMMUTER'
                    ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-sm'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
              >
                <Navigation className="w-3.5 h-3.5" /> Commuter Journey (A ➔ B)
              </button>
              <button
                onClick={() => setActiveTab('TOURIST_T5')}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold transition ${
                  activeTab === 'TOURIST_T5'
                    ? 'bg-amber-500 text-white shadow-sm'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5" /> Persona T5: Tourist Optimizer
              </button>
            </div>

            {/* Controls: Mode Toggle, Report Anomaly, User Persona, Exit */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={toggleTheme}
                className="p-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:scale-105 active:scale-95 transition-all shadow-sm"
                title="Toggle Theme"
              >
                {isDarkMode ? (
                  <Sun className="w-4 h-4 text-amber-400" />
                ) : (
                  <Moon className="w-4 h-4 text-indigo-600" />
                )}
              </button>

              {/* Direct link to Report Anomaly Page */}
              <Link
                href="/report"
                className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-600 dark:text-rose-400 border border-rose-500/30 text-xs font-bold transition shadow-xs"
                title="Report Transit Anomaly"
              >
                <AlertTriangle className="w-3.5 h-3.5 text-rose-600 dark:text-rose-400" />
                <span className="hidden sm:inline">Report Anomaly</span>
              </Link>

              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs">
                <UserCheck className="w-3.5 h-3.5 text-emerald-500" />
                <span className="font-semibold text-slate-700 dark:text-slate-200">
                  {currentUser || 'Arjun (Business)'}
                </span>
              </div>

              <button
                onClick={() => setViewState('LANDING')}
                className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-400 hover:text-slate-700 dark:hover:text-white transition"
                title="Exit to Landing"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </header>

          {/* Conditional View: Commuter Engine vs Persona T5 Tourist Optimizer */}
          {activeTab === 'COMMUTER' ? (
            <>
              {/* Clean Scenario Toolbar */}
              <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 p-3 rounded-2xl flex flex-wrap items-center justify-between gap-3 text-xs shadow-sm">
                <span className="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4 text-indigo-500" />
                  Demo Scenarios:
                </span>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => triggerScenario('A')}
                    className={`px-3.5 py-1.5 rounded-xl font-bold transition shadow-sm ${
                      currentScenario === 'A'
                        ? 'bg-rose-600 text-white'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                    }`}
                  >
                    Scenario A: Confirmed Outage (Reroute)
                  </button>
                  <button
                    onClick={() => triggerScenario('B')}
                    className={`px-3.5 py-1.5 rounded-xl font-bold transition shadow-sm ${
                      currentScenario === 'B'
                        ? 'bg-amber-500 text-white'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                    }`}
                  >
                    Scenario B: Unverified Rumor (Warn Only)
                  </button>
                  <button
                    onClick={() => triggerScenario('C')}
                    className={`px-3.5 py-1.5 rounded-xl font-bold transition shadow-sm ${
                      currentScenario === 'C'
                        ? 'bg-emerald-600 text-white'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                    }`}
                  >
                    Scenario C: Off-Route Disruption (No Impact)
                  </button>
                </div>
              </div>

              {/* Main Grid Layout */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                {/* Left: Constraints & Replanning */}
                <div className="lg:col-span-5 space-y-6">
                  <div className="bg-white dark:bg-slate-900/80 backdrop-blur-xl border border-slate-200 dark:border-slate-800 p-6 rounded-3xl shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <SlidersHorizontal className="w-4 h-4 text-indigo-500" />
                        Trip Constraints
                      </h2>
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-500/20 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/30">
                        Hard Bounds
                      </span>
                    </div>
                    <TravellerForm onSubmit={handlePlanSubmit} />
                  </div>

                  {/* Replanning Proposal Card */}
                  <AnimatePresence>
                    {showAlternative && disruption && journey && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 10 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="space-y-3"
                      >
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
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

                {/* Right: Map & Progress Steps */}
                <div className="lg:col-span-7 space-y-4">
                  {journey ? (
                    <div className="bg-white dark:bg-slate-900/80 backdrop-blur-xl border border-slate-200 dark:border-slate-800 p-6 rounded-3xl shadow-sm space-y-4">
                      {disruption && (
                        <DisruptionBanner
                          alert={disruption}
                          onOpenExplain={() => setIsExplainOpen(true)}
                        />
                      )}

                      <MapView legs={journey.legs} />
                      <JourneyView journey={journey} />
                    </div>
                  ) : (
                    <div className="bg-white dark:bg-slate-900/40 border border-dashed border-slate-300 dark:border-slate-800 p-12 rounded-3xl text-center flex flex-col items-center justify-center min-h-[440px]">
                      <div className="w-16 h-16 rounded-full bg-indigo-50 dark:bg-indigo-600/10 border border-indigo-200 dark:border-indigo-500/20 flex items-center justify-center mb-4">
                        <Compass className="w-8 h-8 text-indigo-600 dark:text-indigo-400 animate-pulse" />
                      </div>
                      <h3 className="text-slate-900 dark:text-white font-bold text-base">
                        Awaiting Route Constraints
                      </h3>
                      <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mt-1.5 leading-relaxed">
                        Set origin, destination, and budget constraints on the left. TrustRoute will compute an OpenTripPlanner multimodal route.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </>
          ) : (
            /* Persona T5 Multi-Stop Tourist Mode */
            <TouristPlanner />
          )}
        </div>
      )}

      {/* Global Modals */}
      <LoginModal
        isOpen={isLoginOpen}
        onClose={() => setIsLoginOpen(false)}
        onLoginSuccess={handleLoginSuccess}
      />

      {disruption && (
        <ExplainabilityModal
          isOpen={isExplainOpen}
          onClose={() => setIsExplainOpen(false)}
          alert={disruption}
        />
      )}
    </div>
  );
}
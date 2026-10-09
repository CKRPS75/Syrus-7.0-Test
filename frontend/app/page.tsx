'use client';

import React, { useState, useEffect } from 'react';
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
import ReportAnomaly from '../components/ReportAnomaly';

import {
  MOCK_BASE_JOURNEY,
  SCENARIO_CONFIRMED,
  SCENARIO_WATCH_RUMOR,
  SCENARIO_IRRELEVANT,
  MOCK_ALTERNATIVE_JOURNEY,
} from '../lib/mockData';
import { JourneyPlanResponse, DisruptionAlert, TravellerConstraints } from '../types';
import { fetchBaseJourney } from '../lib/api';
import { AuthenticatedUser, logout as signOut } from '../lib/auth';
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
  BarChart3,
  Leaf,
  ShieldCheck,
  Clock,
  IndianRupee,
  Train,
  Bus,
  Footprints,
  MapPin,
  AlertCircle,
  ChevronDown,
  UserRound,
  Pencil,
  CircleHelp,
  Check,
  X,
  LoaderCircle,
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
  // First page displayed after login is now ANALYTICS
  const [activeTab, setActiveTab] = useState<'ANALYTICS' | 'COMMUTER' | 'TOURIST_T5' | 'REPORT_ANOMALY'>('ANALYTICS');
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState<AuthenticatedUser | null>(null);
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const [profileDialog, setProfileDialog] = useState<'PROFILE' | 'EDIT' | 'HELP' | 'SIGN_OUT' | null>(null);
  const [profileNameDraft, setProfileNameDraft] = useState('');
  const [profileNotice, setProfileNotice] = useState('');
  const [signOutError, setSignOutError] = useState('');
  const [isSigningOut, setIsSigningOut] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [selectedRegionFilter, setSelectedRegionFilter] = useState<'ALL' | 'RAIL' | 'METRO' | 'BUS'>('ALL');
  const [isPlanning, setIsPlanning] = useState(false);
  const [planningError, setPlanningError] = useState('');

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

  const handleLoginSuccess = (user: AuthenticatedUser) => {
    setCurrentUser(user);
    // Landing directly onto Analytics dashboard upon login
    setActiveTab('ANALYTICS');
    setViewState('APP');
  };

  const handleExitDashboard = () => {
    setCurrentUser(null);
    setProfileMenuOpen(false);
    setProfileDialog(null);
    setViewState('LANDING');
  };

  const handleConfirmedSignOut = async () => {
    setIsSigningOut(true);
    setSignOutError('');
    try {
      await signOut();
      handleExitDashboard();
    } catch {
      setSignOutError('Sign out could not be completed because the authentication service is unavailable. Your account session has not been changed.');
    } finally {
      setIsSigningOut(false);
    }
  };

  const handlePlanSubmit = async (formData: TravellerConstraints) => {
    setIsPlanning(true);
    setPlanningError('');
    setShowAlternative(false);

    try {
      const plannedJourney = await fetchBaseJourney(formData);
      setJourney(plannedJourney);
      setTimeout(() => triggerScenario(currentScenario, false), 800);
    } catch {
      setJourney(MOCK_BASE_JOURNEY);
      setPlanningError(
        'Routing service is unavailable. Showing the built-in sample journey; start the backend on port 8000 for live routes.',
      );
    } finally {
      setIsPlanning(false);
    }
  };

  const triggerScenario = (scenario: 'A' | 'B' | 'C', useFallbackJourney = true) => {
    setCurrentScenario(scenario);
    if (!journey && useFallbackJourney) setJourney(MOCK_BASE_JOURNEY);

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

  // Vulnerability dataset
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
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors">
      {viewState === 'LANDING' ? (
        <LandingView
          onGetStarted={() => {
            setActiveTab('ANALYTICS');
            setViewState('APP');
          }}
          onLoginClick={() => setIsLoginOpen(true)}
        />
      ) : (
        <div className="flex flex-col md:flex-row min-h-screen">
          {/* ==================== UNIFIED PERSISTENT SIDEBAR ==================== */}
          <aside className="w-full md:w-64 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border-r border-slate-200/80 dark:border-slate-800/80 p-5 flex flex-col justify-between shrink-0 shadow-sm z-20">
            <div className="space-y-6">
              {/* Brand Logo */}
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
                    TrustRoute
                  </h1>
                  <span className="text-[10px] font-semibold text-indigo-600 dark:text-indigo-400 block -mt-0.5">
                    Mumbai Mobility Lab
                  </span>
                </div>
              </div>

              {/* Navigation Tabs */}
              <nav className="space-y-1.5 text-xs font-semibold">
                <button
                  type="button"
                  onClick={() => setActiveTab('ANALYTICS')}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition ${
                    activeTab === 'ANALYTICS'
                      ? 'bg-indigo-600 text-white shadow-sm font-bold'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <BarChart3 className="w-4 h-4" />
                  <span>Analytics &amp; Stats</span>
                </button>

                <button
                  type="button"
                  onClick={() => setActiveTab('COMMUTER')}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition ${
                    activeTab === 'COMMUTER'
                      ? 'bg-indigo-600 text-white shadow-sm font-bold'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <Navigation className="w-4 h-4" />
                  <span>Route Planner</span>
                </button>

                <button
                  type="button"
                  onClick={() => setActiveTab('TOURIST_T5')}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition ${
                    activeTab === 'TOURIST_T5'
                      ? 'bg-amber-500 text-white shadow-sm font-bold'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <Sparkles className="w-4 h-4 text-amber-500" />
                  <span>Tourist Day Optimizer</span>
                </button>

                <button
                  type="button"
                  onClick={() => setActiveTab('REPORT_ANOMALY')}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition ${
                    activeTab === 'REPORT_ANOMALY'
                      ? 'bg-rose-600 text-white shadow-sm font-bold'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <AlertTriangle className="w-4 h-4 text-rose-500" />
                  <span>Report Anomaly</span>
                </button>
              </nav>
            </div>

            {/* Sidebar User & Controls */}
            <div className="pt-5 border-t border-slate-200 dark:border-slate-800 space-y-3">
              <button
                type="button"
                aria-haspopup="menu"
                aria-expanded={profileMenuOpen}
                onClick={() => setProfileMenuOpen((open) => !open)}
                className="flex w-full items-center gap-2 rounded-xl px-2 py-2 text-left text-xs transition hover:bg-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 dark:hover:bg-slate-800"
              >
                <UserCheck className="w-4 h-4 shrink-0 text-emerald-500" />
                <span className="min-w-0 flex-1 truncate font-bold text-slate-700 dark:text-slate-300">
                  {currentUser?.name || currentUser?.email || 'Guest'}
                </span>
                <ChevronDown className={`h-4 w-4 shrink-0 text-slate-400 transition-transform ${profileMenuOpen ? 'rotate-180' : ''}`} />
              </button>
              {profileMenuOpen && (
                <div role="menu" aria-label="Profile menu" className="absolute bottom-24 left-4 right-4 z-30 rounded-2xl border border-slate-200 bg-white p-2 shadow-xl dark:border-slate-700 dark:bg-slate-900 md:left-4 md:right-auto md:w-56">
                  <button type="button" role="menuitem" onClick={() => { setProfileDialog('PROFILE'); setProfileMenuOpen(false); setProfileNotice(''); }} className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-xs font-semibold text-slate-700 hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800">
                    <UserRound className="h-4 w-4 text-indigo-500" /> My Profile
                  </button>
                  <button type="button" role="menuitem" onClick={() => { setProfileNameDraft(currentUser?.name || ''); setProfileDialog('EDIT'); setProfileMenuOpen(false); setProfileNotice(''); }} className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-xs font-semibold text-slate-700 hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800">
                    <Pencil className="h-4 w-4 text-indigo-500" /> Edit Profile
                  </button>
                  <button type="button" role="menuitem" onClick={() => { setProfileDialog('HELP'); setProfileMenuOpen(false); }} className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-xs font-semibold text-slate-700 hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800">
                    <CircleHelp className="h-4 w-4 text-indigo-500" /> Help &amp; Support
                  </button>
                  <div className="my-1 border-t border-slate-100 dark:border-slate-800" />
                  <button type="button" role="menuitem" onClick={() => { setSignOutError(''); setProfileDialog('SIGN_OUT'); setProfileMenuOpen(false); }} className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-xs font-semibold text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40">
                    <LogOut className="h-4 w-4" /> {currentUser ? 'Log out' : 'Return to home'}
                  </button>
                </div>
              )}

              <div className="flex items-center justify-between pt-1">
                <span className="text-[10px] text-slate-400 font-medium">MMRDA GTFS 2026</span>
                <button
                  type="button"
                  onClick={toggleTheme}
                  className="p-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:scale-105 transition"
                  title="Toggle Light/Dark Theme"
                >
                  {isDarkMode ? <Sun className="w-3.5 h-3.5 text-amber-400" /> : <Moon className="w-3.5 h-3.5 text-indigo-600" />}
                </button>
              </div>
            </div>
          </aside>

          {/* ==================== MAIN CONTENT AREA ==================== */}
          <main className="flex-1 p-4 sm:p-7 overflow-y-auto max-w-7xl mx-auto w-full space-y-6">
            {/* VIEW 1: ANALYTICS & STATS (DEFAULT POST-LOGIN) */}
            {activeTab === 'ANALYTICS' && (
              <div className="space-y-6 animate-fadeIn">
                <div>
                  <h2 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white tracking-tight">
                    Multimodal Transit Analytics &amp; Vulnerability Matrix
                  </h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                    Real-time Bayesian reliability tracking, SDG 13 carbon abatement metrics, and corridor-level fault profiling.
                  </p>
                </div>

                {/* 4 COLOR-TINTED TRANSLUCENT STATS BOXES */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  {/* Card 1: Emerald/Mint Tint */}
                  <div className="bg-emerald-500/10 dark:bg-emerald-500/[0.07] backdrop-blur-md p-5 rounded-3xl border border-emerald-500/20 shadow-xs space-y-1.5 hover:border-emerald-500/40 transition">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-300 flex items-center gap-1.5">
                      <Leaf className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" /> Net CO₂ Abatement
                    </span>
                    <div className="text-2xl font-extrabold text-slate-900 dark:text-white">
                      -1,842 <span className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">kg</span>
                    </div>
                    <p className="text-[10px] text-slate-600 dark:text-slate-400 leading-tight">
                      Equivalent to <strong>88 trees planted</strong> vs. private cab baselines.
                    </p>
                  </div>

                  {/* Card 2: Amber/Gold Tint */}
                  <div className="bg-amber-500/10 dark:bg-amber-500/[0.07] backdrop-blur-md p-5 rounded-3xl border border-amber-500/20 shadow-xs space-y-1.5 hover:border-amber-500/40 transition">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-amber-700 dark:text-amber-300 flex items-center gap-1.5">
                      <ShieldCheck className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" /> Rumors Filtered
                    </span>
                    <div className="text-2xl font-extrabold text-slate-900 dark:text-white">
                      47 <span className="text-sm font-semibold text-amber-600 dark:text-amber-400">Blocked</span>
                    </div>
                    <p className="text-[10px] text-slate-600 dark:text-slate-400 leading-tight">
                      Crowd reports capped at +2.6 to prevent unverified panic detours.
                    </p>
                  </div>

                  {/* Card 3: Sky/Cyan Tint */}
                  <div className="bg-sky-500/10 dark:bg-sky-500/[0.07] backdrop-blur-md p-5 rounded-3xl border border-sky-500/20 shadow-xs space-y-1.5 hover:border-sky-500/40 transition">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-sky-700 dark:text-sky-300 flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-sky-600 dark:text-sky-400" /> Commute Delay Averted
                    </span>
                    <div className="text-2xl font-extrabold text-slate-900 dark:text-white">
                      27.4 <span className="text-sm font-semibold text-sky-600 dark:text-sky-400">min/rider</span>
                    </div>
                    <p className="text-[10px] text-slate-600 dark:text-slate-400 leading-tight">
                      Average delay saved when passengers accept dynamic rerouting.
                    </p>
                  </div>

                  {/* Card 4: Purple/Indigo Tint */}
                  <div className="bg-purple-500/10 dark:bg-purple-500/[0.07] backdrop-blur-md p-5 rounded-3xl border border-purple-500/20 shadow-xs space-y-1.5 hover:border-purple-500/40 transition">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-purple-700 dark:text-purple-300 flex items-center gap-1.5">
                      <IndianRupee className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" /> Avg Commute Cost
                    </span>
                    <div className="text-2xl font-extrabold text-slate-900 dark:text-white">
                      ₹38.50 <span className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">-78% vs Cab</span>
                    </div>
                    <p className="text-[10px] text-slate-600 dark:text-slate-400 leading-tight">
                      Public bus + train integration guarantees hard budget constraints.
                    </p>
                  </div>
                </div>

                {/* MIDDLE ROW: EMISSION BARS & BAYESIAN MECHANICS */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                  {/* Translucent Green/Emerald Box */}
                  <div className="lg:col-span-7 bg-emerald-500/[0.04] dark:bg-emerald-500/[0.03] backdrop-blur-xl p-6 rounded-3xl border border-emerald-500/20 shadow-sm space-y-5">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                          <Leaf className="w-4 h-4 text-emerald-500" />
                          SDG 13: Emissions by Mode of Transport
                        </h3>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400">
                          Grams of CO₂ generated per passenger per kilometer across Mumbai.
                        </p>
                      </div>
                      <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30">
                        -81.3% Eco-Efficiency
                      </span>
                    </div>

                    <div className="space-y-3.5 text-xs">
                      <div>
                        <div className="flex justify-between font-semibold mb-1">
                          <span className="flex items-center gap-1.5 text-rose-600 dark:text-rose-400 font-bold">
                            Ride-Hail Cab / Private Car (Baseline)
                          </span>
                          <span className="font-bold">150 g CO₂/km</span>
                        </div>
                        <div className="w-full h-3 bg-slate-200/60 dark:bg-slate-800 rounded-full overflow-hidden">
                          <div className="h-full bg-rose-500 rounded-full w-full" />
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between font-semibold mb-1">
                          <span className="flex items-center gap-1.5 text-amber-600 dark:text-amber-400 font-bold">
                            <Bus className="w-3.5 h-3.5" /> BEST Diesel/CNG Bus
                          </span>
                          <span>38 g CO₂/km</span>
                        </div>
                        <div className="w-full h-3 bg-slate-200/60 dark:bg-slate-800 rounded-full overflow-hidden">
                          <div className="h-full bg-amber-500 rounded-full w-[25%]" />
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between font-semibold mb-1">
                          <span className="flex items-center gap-1.5 text-sky-600 dark:text-sky-400 font-bold">
                            <Train className="w-3.5 h-3.5" /> Mumbai Metro (Line 1/2A/7)
                          </span>
                          <span>22 g CO₂/km</span>
                        </div>
                        <div className="w-full h-3 bg-slate-200/60 dark:bg-slate-800 rounded-full overflow-hidden">
                          <div className="h-full bg-sky-500 rounded-full w-[14.6%]" />
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between font-semibold mb-1">
                          <span className="flex items-center gap-1.5 text-indigo-600 dark:text-indigo-400 font-bold">
                            <Train className="w-3.5 h-3.5" /> Suburban Electric Railway
                          </span>
                          <span>18 g CO₂/km</span>
                        </div>
                        <div className="w-full h-3 bg-slate-200/60 dark:bg-slate-800 rounded-full overflow-hidden">
                          <div className="h-full bg-indigo-500 rounded-full w-[12%]" />
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between font-semibold mb-1">
                          <span className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400 font-bold">
                            <Footprints className="w-3.5 h-3.5" /> Pedestrian / Walking
                          </span>
                          <span>0 g CO₂/km</span>
                        </div>
                        <div className="w-full h-3 bg-slate-200/60 dark:bg-slate-800 rounded-full overflow-hidden">
                          <div className="h-full bg-emerald-500 rounded-full w-[2%]" />
                        </div>
                      </div>
                    </div>

                    <div className="p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-[11px] text-emerald-800 dark:text-emerald-300 leading-relaxed">
                      <strong>Environmental Impact:</strong> TrustRoute journeys route <strong>94%</strong> of user kilometers onto electrified rail, metro, or clean walking corridors, cutting emissions by over 80%.
                    </div>
                  </div>

                  {/* Translucent Violet/Indigo Box */}
                  <div className="lg:col-span-5 bg-indigo-500/[0.04] dark:bg-indigo-500/[0.03] backdrop-blur-xl p-6 rounded-3xl border border-indigo-500/20 shadow-sm space-y-4">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4 text-indigo-500" />
                        Bayesian Confidence Mechanics
                      </h3>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400">
                        Logit evidence accumulation curve and rumor prevention cap.
                      </p>
                    </div>

                    <div className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm p-3 rounded-2xl border border-indigo-100 dark:border-indigo-900/40 space-y-2 text-xs">
                      <div className="flex justify-between items-center py-1 border-b border-slate-200/60 dark:border-slate-700/60">
                        <span className="text-slate-500 dark:text-slate-400">Base Prior ($P_0$):</span>
                        <span className="font-mono font-bold">10% ($L_0 = -2.197$)</span>
                      </div>
                      <div className="flex justify-between items-center py-1 border-b border-slate-200/60 dark:border-slate-700/60">
                        <span className="text-slate-500 dark:text-slate-400">1 Crowd Report:</span>
                        <span className="font-mono font-bold text-amber-500">+0.8 weight (P* ≈ 42%)</span>
                      </div>
                      <div className="flex justify-between items-center py-1 border-b border-slate-200/60 dark:border-slate-700/60">
                        <span className="text-slate-500 dark:text-slate-400">Crowd Cap Guardrail:</span>
                        <span className="font-mono font-bold text-rose-500">+2.6 Max (P* ≤ 59.9%)</span>
                      </div>
                      <div className="flex justify-between items-center py-1">
                        <span className="text-slate-500 dark:text-slate-400">Reroute Threshold:</span>
                        <span className="font-mono font-bold text-emerald-500">P* ≥ 0.65 (65%)</span>
                      </div>
                    </div>

                    <div className="p-3.5 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-[11px] text-indigo-800 dark:text-indigo-300 space-y-1">
                      <p className="font-bold">Why Passengers Never Suffer Rumor Reroutes:</p>
                      <p className="leading-relaxed">
                        Because crowd submissions are mathematically capped at +2.6, no matter how many duplicate reports are filed, the posterior probability can never exceed 59.9% without corroboration from official transit advisory feeds (+3.0) or local news GDELT sensors (+1.5).
                      </p>
                    </div>
                  </div>
                </div>

                {/* BOTTOM ROW: VULNERABILITY MATRIX TABLE */}
                <div className="bg-rose-500/[0.03] dark:bg-rose-500/[0.02] backdrop-blur-xl p-6 rounded-3xl border border-rose-500/20 shadow-sm space-y-5">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <AlertCircle className="w-4 h-4 text-rose-500" />
                        Vulnerability Matrix: Mode vs. Regional Problem Types
                      </h3>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400">
                        Historical fault profiling across Mumbai’s critical transit corridors (MMRDA CTS &amp; GTFS telemetry).
                      </p>
                    </div>

                    {/* Filter Tabs */}
                    <div className="flex bg-white/70 dark:bg-slate-800/80 p-1 rounded-xl text-xs font-bold border border-slate-200/60 dark:border-slate-700/60">
                      {(['ALL', 'RAIL', 'METRO', 'BUS'] as const).map((filter) => (
                        <button
                          key={filter}
                          onClick={() => setSelectedRegionFilter(filter)}
                          className={`px-3 py-1.5 rounded-lg transition ${
                            selectedRegionFilter === filter
                              ? 'bg-indigo-600 text-white shadow-xs'
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
                        <tr className="border-b border-slate-200/80 dark:border-slate-800 text-[11px] text-slate-400 font-bold uppercase tracking-wider">
                          <th className="py-3 px-3">Corridor / Hub</th>
                          <th className="py-3 px-3">Mode</th>
                          <th className="py-3 px-3">Dominant Failure Pattern</th>
                          <th className="py-3 px-3">Risk Level</th>
                          <th className="py-3 px-3">Avg Delay</th>
                          <th className="py-3 px-3">Root Cause</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-200/50 dark:divide-slate-800/60 font-medium">
                        {filteredVulnerabilities.map((row, idx) => (
                          <tr key={idx} className="hover:bg-white/50 dark:hover:bg-slate-800/40 transition">
                            <td className="py-3 px-3 font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                              <MapPin className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
                              <span>{row.corridor}</span>
                            </td>
                            <td className="py-3 px-3">
                              <span
                                className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                  row.mode === 'METRO'
                                    ? 'bg-sky-500/10 text-sky-600 dark:text-sky-300 border border-sky-500/20'
                                    : row.mode === 'RAIL'
                                    ? 'bg-indigo-500/10 text-indigo-600 dark:text-indigo-300 border border-indigo-500/20'
                                    : 'bg-green-500/10 text-green-600 dark:text-green-300 border border-green-500/20'
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
                                    ? 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/30'
                                    : row.riskLevel === 'HIGH'
                                    ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30'
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
              </div>
            )}

            {/* VIEW 2: COMMUTER ROUTE PLANNER */}
            {activeTab === 'COMMUTER' && (
              <div className="space-y-6 animate-fadeIn">
                {/* Scenario Toolbar */}
                <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border border-slate-200 dark:border-slate-800 p-3.5 rounded-2xl flex flex-wrap items-center justify-between gap-3 text-xs shadow-xs">
                  <span className="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                    <Sparkles className="w-4 h-4 text-indigo-500" />
                    Demo Scenarios:
                  </span>
                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => triggerScenario('A')}
                      className={`px-3.5 py-1.5 rounded-xl font-bold transition shadow-xs ${
                        currentScenario === 'A'
                          ? 'bg-rose-600 text-white'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                      }`}
                    >
                      Scenario A: Confirmed Outage (Reroute)
                    </button>
                    <button
                      onClick={() => triggerScenario('B')}
                      className={`px-3.5 py-1.5 rounded-xl font-bold transition shadow-xs ${
                        currentScenario === 'B'
                          ? 'bg-amber-500 text-white'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                      }`}
                    >
                      Scenario B: Unverified Rumor (Warn Only)
                    </button>
                    <button
                      onClick={() => triggerScenario('C')}
                      className={`px-3.5 py-1.5 rounded-xl font-bold transition shadow-xs ${
                        currentScenario === 'C'
                          ? 'bg-emerald-600 text-white'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                      }`}
                    >
                      Scenario C: Off-Route Disruption (No Impact)
                    </button>
                  </div>
                </div>

                {/* Main 2-Column Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                  {/* Left Column: Form & Dynamic Alternatives */}
                  <div className="lg:col-span-5 space-y-6">
                    <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border border-slate-200 dark:border-slate-800 p-6 rounded-3xl shadow-xs">
                      <div className="flex items-center justify-between mb-4">
                        <h2 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                          <SlidersHorizontal className="w-4 h-4 text-indigo-500" />
                          Trip Constraints
                        </h2>
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-500/20 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/30">
                          Hard Bounds
                        </span>
                      </div>
                      <TravellerForm
                        onSubmit={handlePlanSubmit}
                        isSubmitting={isPlanning}
                        submitError={planningError}
                      />
                    </div>

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

                  {/* Right Column: Map & Step Breakdown */}
                  <div className="lg:col-span-7 space-y-4">
                    {journey ? (
                      <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border border-slate-200 dark:border-slate-800 p-6 rounded-3xl shadow-xs space-y-4">
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
                      <div className="bg-white/50 dark:bg-slate-900/40 border border-dashed border-slate-300 dark:border-slate-800 p-12 rounded-3xl text-center flex flex-col items-center justify-center min-h-[440px]">
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
              </div>
            )}

            {/* VIEW 3: TOURIST DAY OPTIMIZER */}
            {activeTab === 'TOURIST_T5' && (
              <div className="animate-fadeIn">
                <TouristPlanner />
              </div>
            )}
            {activeTab === 'REPORT_ANOMALY' && <ReportAnomaly />}
          </main>
        </div>
      )}

      {/* Global Modals */}
      <LoginModal
        isOpen={isLoginOpen}
        onClose={() => setIsLoginOpen(false)}
        onLoginSuccess={handleLoginSuccess}
      />

      {profileDialog && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget && !isSigningOut) setProfileDialog(null);
          }}
        >
          <section role="dialog" aria-modal="true" aria-labelledby="profile-dialog-title" className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-6 shadow-2xl dark:border-slate-700 dark:bg-slate-900">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 id="profile-dialog-title" className="text-lg font-bold text-slate-900 dark:text-white">
                  {profileDialog === 'PROFILE' ? 'My Profile' : profileDialog === 'EDIT' ? 'Edit Profile' : profileDialog === 'HELP' ? 'Help & Support' : 'Sign out?'}
                </h2>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  {profileDialog === 'HELP'
                    ? 'For help with routes, choose Route Planner and submit your journey constraints. Transit anomaly reports are reviewed by the Trust Engine.'
                    : profileDialog === 'SIGN_OUT'
                      ? 'You will be returned to the TrustRoute home page.'
                      : 'Your account information for this session.'}
                </p>
              </div>
              <button type="button" onClick={() => setProfileDialog(null)} disabled={isSigningOut} aria-label="Close dialog" className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700 disabled:opacity-50 dark:hover:bg-slate-800 dark:hover:text-white">
                <X className="h-4 w-4" />
              </button>
            </div>

            {(profileDialog === 'PROFILE' || profileDialog === 'EDIT') && (
              <div className="mt-5 space-y-3 text-sm">
                {profileDialog === 'EDIT' ? (
                  <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300">
                    Display name
                    <input value={profileNameDraft} onChange={(event) => setProfileNameDraft(event.target.value)} className="mt-1.5 w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white" />
                  </label>
                ) : (
                  <div className="rounded-xl bg-slate-50 px-4 py-3 dark:bg-slate-800">
                    <p className="text-[11px] text-slate-500">Name</p>
                    <p className="mt-1 font-semibold text-slate-800 dark:text-slate-100">{currentUser?.name || 'Guest user'}</p>
                  </div>
                )}
                <div className="rounded-xl bg-slate-50 px-4 py-3 dark:bg-slate-800">
                  <p className="text-[11px] text-slate-500">Email</p>
                  <p className="mt-1 font-semibold text-slate-800 dark:text-slate-100">{currentUser?.email || 'Not signed in'}</p>
                </div>
                {profileNotice && <p role="status" className="text-xs text-amber-700 dark:text-amber-300">{profileNotice}</p>}
              </div>
            )}

            {signOutError && <p role="alert" className="mt-4 rounded-xl bg-rose-50 px-3 py-2 text-sm text-rose-700 dark:bg-rose-950/40 dark:text-rose-300">{signOutError}</p>}
            <div className="mt-6 flex justify-end gap-2">
              <button type="button" onClick={() => setProfileDialog(null)} disabled={isSigningOut} className="rounded-xl px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100 disabled:opacity-50 dark:text-slate-300 dark:hover:bg-slate-800">
                Cancel
              </button>
              {profileDialog === 'EDIT' && (
                <button type="button" onClick={() => {
                  const name = profileNameDraft.trim();
                  if (name.length < 2) {
                    setProfileNotice('Enter a name with at least two characters.');
                    return;
                  }
                  setCurrentUser((user) => ({ name, email: user?.email }));
                  setProfileNotice('Name updated for this session only.');
                }} className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700">
                  <Check className="h-4 w-4" /> Save
                </button>
              )}
              {profileDialog === 'SIGN_OUT' && (
                <button type="button" onClick={() => {
                  if (currentUser) void handleConfirmedSignOut();
                  else handleExitDashboard();
                }} disabled={isSigningOut} className="inline-flex items-center gap-2 rounded-xl bg-rose-600 px-4 py-2 text-sm font-semibold text-white hover:bg-rose-700 disabled:opacity-60">
                  {isSigningOut && <LoaderCircle className="h-4 w-4 animate-spin" />}
                  {currentUser ? 'Sign out' : 'Return home'}
                </button>
              )}
            </div>
          </section>
        </div>
      )}

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

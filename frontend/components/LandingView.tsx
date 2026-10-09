'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Compass, ShieldCheck, Zap, ArrowRight, Sparkles, Navigation } from 'lucide-react';

interface LandingViewProps {
  onGetStarted: () => void;
  onLoginClick: () => void;
}

export default function LandingView({ onGetStarted, onLoginClick }: LandingViewProps) {
  return (
    <div className="relative overflow-hidden min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors">
      {/* Background Ambient Glow */}
      <div className="absolute top-[-10%] left-[-10%] w-[520px] h-[520px] bg-gradient-to-tr from-indigo-500/20 to-fuchsia-500/20 dark:from-indigo-600/30 dark:to-fuchsia-600/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-[35%] right-[-10%] w-[480px] h-[480px] bg-gradient-to-br from-cyan-400/20 to-indigo-500/20 dark:from-cyan-500/20 dark:to-blue-600/20 rounded-full blur-[140px] pointer-events-none" />

      {/* Top Navigation */}
      <header className="relative z-10 flex items-center justify-between px-6 py-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 p-0.5 shadow-lg shadow-indigo-500/20">
            <div className="w-full h-full bg-white dark:bg-slate-950 rounded-[14px] flex items-center justify-center">
              <Compass className="w-5 h-5 text-indigo-600 dark:text-indigo-400 animate-spin-slow" />
            </div>
          </div>
          <div>
            <span className="text-xl font-extrabold tracking-tight text-slate-900 dark:text-white">
              Trust<span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">Route</span>
            </span>
            <span className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 block tracking-wider uppercase">
              Mobility AI
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onLoginClick}
            className="text-xs font-bold text-slate-700 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-white px-4 py-2 transition"
          >
            Sign In
          </button>
          <button
            onClick={onGetStarted}
            className="text-xs font-bold text-white bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 px-5 py-2.5 rounded-full shadow-lg shadow-purple-600/30 hover:scale-105 active:scale-95 transition-all duration-300"
          >
            Launch Pilot
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 max-w-5xl mx-auto px-6 pt-12 pb-20 text-center">
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 dark:bg-indigo-500/20 backdrop-blur-md mb-6"
        >
          <Sparkles className="w-4 h-4 text-pink-500" />
          <span className="text-xs font-bold text-indigo-800 dark:text-indigo-200">
            Evidence-Aware Dynamic Multimodal Engine
          </span>
        </motion.div>

        {/* Clear Contrast Title */}
        <motion.h1
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-4xl sm:text-6xl md:text-7xl font-black tracking-tight leading-[1.15] mb-6 text-slate-900 dark:text-white"
        >
          Plan for the journey.{' '}
          <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-500 bg-clip-text text-transparent">
            Adapt to reality.
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="max-w-2xl mx-auto text-sm sm:text-base text-slate-600 dark:text-slate-300 leading-relaxed mb-10 font-medium"
        >
          Stop getting stranded by stale transit timetables. TrustRoute correlates verified official alerts,
          GDELT news, and crowdsourced incident feeds to protect your deadlines in real time.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <button
            onClick={onGetStarted}
            className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white font-bold text-sm shadow-xl shadow-indigo-600/30 hover:scale-105 active:scale-95 transition-all flex items-center justify-center gap-2 group"
          >
            <span>Plan My Protected Journey</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
          <button
            onClick={onLoginClick}
            className="w-full sm:w-auto px-6 py-4 rounded-2xl bg-white dark:bg-slate-900/80 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800 font-semibold text-sm backdrop-blur-md transition shadow-md"
          >
            Explore Personas &amp; Ground Truth
          </button>
        </motion.div>

        {/* Feature Cards with Unified Theme Colors */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-16 text-left">
          <div className="p-6 rounded-3xl bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 backdrop-blur-xl shadow-lg hover:shadow-indigo-500/10 transition-all">
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 dark:bg-indigo-500/20 border border-indigo-500/20 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mb-4">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base mb-1.5 text-slate-900 dark:text-white">Evidence-Aware Trust</h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed font-normal">
              Calculates Bayesian confidence (P*). Weak crowd reports alone are capped and cannot trigger an unwanted reroute.
            </p>
          </div>

          <div className="p-6 rounded-3xl bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 backdrop-blur-xl shadow-lg hover:shadow-purple-500/10 transition-all">
            <div className="w-12 h-12 rounded-2xl bg-fuchsia-500/10 dark:bg-fuchsia-500/20 border border-fuchsia-500/20 flex items-center justify-center text-fuchsia-600 dark:text-fuchsia-400 mb-4">
              <Zap className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base mb-1.5 text-slate-900 dark:text-white">Safe Dynamic Replanning</h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed font-normal">
              Only proposes alternatives when disruptions breach safety buffers by at least 8 mins or 15% remaining journey.
            </p>
          </div>

          <div className="p-6 rounded-3xl bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 backdrop-blur-xl shadow-lg hover:shadow-emerald-500/10 transition-all">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 dark:bg-emerald-500/20 border border-emerald-500/20 flex items-center justify-center text-emerald-600 dark:text-emerald-400 mb-4">
              <Navigation className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base mb-1.5 text-slate-900 dark:text-white">Binding Constraints</h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed font-normal">
              Budget caps (₹), step-free access, and walking boundaries remain strictly respected during any route adjustment.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
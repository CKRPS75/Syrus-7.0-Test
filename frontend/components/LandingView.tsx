'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Compass, ShieldCheck, Zap, ArrowRight, Sparkles, Navigation, CheckCircle2 } from 'lucide-react';

interface LandingViewProps {
  onGetStarted: () => void;
  onLoginClick: () => void;
}

export default function LandingView({ onGetStarted, onLoginClick }: LandingViewProps) {
  return (
    <div className="relative overflow-hidden">
      {/* Background Animated Gradient Blobs */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-gradient-to-tr from-violet-600/30 to-fuchsia-600/20 rounded-full blur-[120px] pointer-events-none animate-pulse" />
      <div className="absolute top-[30%] right-[-10%] w-[450px] h-[450px] bg-gradient-to-br from-cyan-500/25 to-blue-600/20 rounded-full blur-[140px] pointer-events-none" />

      {/* Top Navigation */}
      <header className="relative z-10 flex items-center justify-between px-6 py-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 p-0.5 shadow-lg shadow-indigo-500/20">
            <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
              <Compass className="w-5 h-5 text-indigo-400 animate-spin-slow" />
            </div>
          </div>
          <div>
            <span className="text-xl font-black bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
              TrustRoute
            </span>
            <span className="text-[10px] font-semibold text-indigo-400 block tracking-wider uppercase">
              Mobility AI
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onLoginClick}
            className="text-xs font-semibold text-slate-300 hover:text-white px-4 py-2 transition"
          >
            Sign In
          </button>
          <button
            onClick={onGetStarted}
            className="text-xs font-bold text-white bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 px-5 py-2.5 rounded-full shadow-lg shadow-purple-600/30 hover:shadow-purple-600/50 hover:scale-105 active:scale-95 transition-all duration-300"
          >
            Launch Pilot
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 max-w-5xl mx-auto px-6 pt-16 pb-20 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 backdrop-blur-md mb-8"
        >
          <Sparkles className="w-4 h-4 text-pink-400" />
          <span className="text-xs font-semibold text-indigo-200">
            Evidence-Aware Dynamic Multimodal Engine
          </span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-4xl sm:text-6xl md:text-7xl font-black text-white tracking-tight leading-[1.1] mb-6"
        >
          Plan for the journey.{' '}
          <span className="bg-gradient-to-r from-cyan-400 via-fuchsia-400 to-amber-300 bg-clip-text text-transparent">
            Adapt to reality.
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="max-w-2xl mx-auto text-sm sm:text-base text-slate-400 leading-relaxed mb-10"
        >
          Stop getting stranded by stale transit schedules. TrustRoute analyzes verified
          official alerts, GDELT news, and crowdsourced incident streams to protect your
          deadlines in real-time.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <button
            onClick={onGetStarted}
            className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white font-bold text-sm shadow-xl shadow-indigo-500/30 hover:shadow-indigo-500/50 hover:scale-105 active:scale-95 transition-all flex items-center justify-center gap-2 group"
          >
            <span>Plan My Protected Journey</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
          <button
            onClick={onLoginClick}
            className="w-full sm:w-auto px-6 py-4 rounded-2xl bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-800 font-semibold text-sm backdrop-blur-md transition"
          >
            Explore Personas & Ground Truth
          </button>
        </motion.div>

        {/* Feature Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-20 text-left">
          <motion.div
            whileHover={{ y: -5 }}
            className="p-6 rounded-3xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl relative overflow-hidden group"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-2xl group-hover:bg-indigo-500/20 transition-all" />
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 mb-4">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-white font-bold text-base mb-1">Evidence-Aware Trust Engine</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Calculates Bayesian uncalibrated trust confidence ($P^*$). Crowd rumors alone cannot force an unwanted reroute.
            </p>
          </motion.div>

          <motion.div
            whileHover={{ y: -5 }}
            className="p-6 rounded-3xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl relative overflow-hidden group"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-fuchsia-500/10 rounded-full blur-2xl group-hover:bg-fuchsia-500/20 transition-all" />
            <div className="w-12 h-12 rounded-2xl bg-fuchsia-500/20 border border-fuchsia-500/30 flex items-center justify-center text-fuchsia-400 mb-4">
              <Zap className="w-6 h-6" />
            </div>
            <h3 className="text-white font-bold text-base mb-1">Dynamic Replanning (OTP)</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              When confirmed disruptions breach your arrival buffer, counterfactual multimodal alternatives are generated with your confirmation.
            </p>
          </motion.div>

          <motion.div
            whileHover={{ y: -5 }}
            className="p-6 rounded-3xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl relative overflow-hidden group"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-2xl group-hover:bg-emerald-500/20 transition-all" />
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-4">
              <Navigation className="w-6 h-6" />
            </div>
            <h3 className="text-white font-bold text-base mb-1">Strict Constraint Bounds</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Budget caps (₹), step-free accessibility flags, and maximum walking distances remain unbreakable during rerouting.
            </p>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
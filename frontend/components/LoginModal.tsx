'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { X, Sparkles, User, Lock, ArrowRight, ShieldCheck } from 'lucide-react';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginSuccess: (userName: string) => void;
}

export default function LoginModal({ isOpen, onClose, onLoginSuccess }: LoginModalProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  if (!isOpen) return null;

  const handlePresetPersona = (name: string) => {
    onLoginSuccess(name);
    onClose();
  };

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onLoginSuccess(email.split('@')[0] || 'Rushil');
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="relative w-full max-w-md bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl shadow-purple-950/50 overflow-hidden"
      >
        {/* Glow Accent */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-48 h-1 bg-gradient-to-r from-cyan-500 via-fuchsia-500 to-amber-500 rounded-full blur-sm" />

        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-full text-slate-400 hover:text-white hover:bg-slate-800 transition"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-indigo-600/20 text-indigo-400 mb-3 border border-indigo-500/30">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-white">Access TrustRoute Hub</h2>
          <p className="text-xs text-slate-400 mt-1">Authenticate or choose an evaluation persona</p>
        </div>

        {/* Demo Personas for Quick Hackathon Judging */}
        <div className="mb-6">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
            One-Click Test Personas
          </span>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => handlePresetPersona('Arjun (Business)')}
              className="p-2.5 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 text-left text-xs transition group"
            >
              <span className="font-semibold text-indigo-300 block group-hover:text-indigo-200">
                Arjun • Deadline
              </span>
              <span className="text-[10px] text-slate-400">Time-critical meeting</span>
            </button>
            <button
              type="button"
              onClick={() => handlePresetPersona('Pooja (Student)')}
              className="p-2.5 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 text-left text-xs transition group"
            >
              <span className="font-semibold text-pink-300 block group-hover:text-pink-200">
                Pooja • Budget
              </span>
              <span className="text-[10px] text-slate-400">Strict ₹50 constraint</span>
            </button>
            <button
              type="button"
              onClick={() => handlePresetPersona('Sunita (Elderly)')}
              className="p-2.5 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 text-left text-xs transition group"
            >
              <span className="font-semibold text-amber-300 block group-hover:text-amber-200">
                Sunita • Low Walking
              </span>
              <span className="text-[10px] text-slate-400">Max 500m walking</span>
            </button>
            <button
              type="button"
              onClick={() => handlePresetPersona('Karan (Wheelchair)')}
              className="p-2.5 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 text-left text-xs transition group"
            >
              <span className="font-semibold text-emerald-300 block group-hover:text-emerald-200">
                Karan • Accessible
              </span>
              <span className="text-[10px] text-slate-400">Elevator-only routing</span>
            </button>
            <button
              type="button"
              onClick={() => handlePresetPersona('T5 Tourist (Multi-Stop)')}
              className="p-2.5 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-amber-500/40 text-left text-xs transition group col-span-2 sm:col-span-1"
            >
              <span className="font-semibold text-amber-300 block group-hover:text-amber-200 flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-amber-400" /> T5 • Tourist Day
              </span>
              <span className="text-[10px] text-slate-400">Multi-stop day tour</span>
            </button>
          </div>
        </div>

        <div className="relative flex py-2 items-center mb-4">
          <div className="flex-grow border-t border-slate-800"></div>
          <span className="flex-shrink mx-2 text-[10px] uppercase font-bold text-slate-500">
            or sign in
          </span>
          <div className="flex-grow border-t border-slate-800"></div>
        </div>

        {/* Regular Sign-In */}
        <form onSubmit={handleManualSubmit} className="space-y-3">
          <div className="space-y-1 text-left">
            <label className="text-[11px] font-semibold text-slate-300">Email Address</label>
            <div className="relative">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="rushil@trustroute.io"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500"
              />
              <User className="absolute right-3 top-2.5 w-4 h-4 text-slate-600" />
            </div>
          </div>

          <div className="space-y-1 text-left">
            <label className="text-[11px] font-semibold text-slate-300">Password</label>
            <div className="relative">
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500"
              />
              <Lock className="absolute right-3 top-2.5 w-4 h-4 text-slate-600" />
            </div>
          </div>

          <button
            type="submit"
            className="w-full mt-2 py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-1.5"
          >
            <span>Proceed to Dashboard</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </form>
      </motion.div>
    </div>
  );
}
'use client';

import React from 'react';
import { Check, X } from 'lucide-react';

interface ConfirmPromptProps {
  onAccept: () => void;
  onReject: () => void;
  isLoading: boolean;
}

export default function ConfirmPrompt({ onAccept, onReject, isLoading }: ConfirmPromptProps) {
  return (
    <div className="flex gap-2">
      <button
        onClick={onReject}
        disabled={isLoading}
        className="flex-1 border border-slate-300 hover:bg-slate-100 text-slate-700 text-xs font-semibold py-2.5 rounded-xl transition flex items-center justify-center gap-1.5"
      >
        <X className="w-4 h-4 text-slate-400" />
        Keep Current Route
      </button>

      <button
        onClick={onAccept}
        disabled={isLoading}
        className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold py-2.5 rounded-xl transition shadow-sm flex items-center justify-center gap-1.5 disabled:opacity-50"
      >
        <Check className="w-4 h-4" />
        {isLoading ? 'Updating...' : 'Accept New Route'}
      </button>
    </div>
  );
}
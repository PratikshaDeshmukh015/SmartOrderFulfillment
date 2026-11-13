import React from 'react';
import { Calendar, RefreshCw, PlusCircle, CheckCircle2 } from 'lucide-react';

export function Navbar({ onRefresh, onNewOrder, isRefreshing }) {
  return (
    <header className="h-16 bg-slate-900/60 backdrop-blur border-b border-slate-800 flex items-center justify-between px-8 shrink-0 sticky top-0 z-20">
      <div className="flex items-center gap-3">
        <span className="text-xs text-slate-400">Environment:</span>
        <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
          Production Simulated (v2.0.0)
        </span>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center text-xs text-slate-400 font-mono gap-1.5 bg-slate-800/50 px-3 py-1.5 rounded-lg border border-slate-700/50">
          <Calendar className="w-3.5 h-3.5 text-sky-400" />
          <span>Operational Epoch: Q4 2026</span>
        </div>

        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-sky-400' : ''}`} />
          <span>Sync Data</span>
        </button>

        <button
          onClick={onNewOrder}
          className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-sky-500 hover:bg-sky-400 text-slate-950 transition shadow-sm"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Create Order</span>
        </button>
      </div>
    </header>
  );
}

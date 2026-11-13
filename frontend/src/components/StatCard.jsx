import React from 'react';

export function StatCard({ title, value, subtitle, icon: Icon, color = 'blue', trend }) {
  const colorMap = {
    blue: 'from-blue-600/20 to-blue-600/5 text-blue-400 border-blue-500/20',
    emerald: 'from-emerald-600/20 to-emerald-600/5 text-emerald-400 border-emerald-500/20',
    amber: 'from-amber-600/20 to-amber-600/5 text-amber-400 border-amber-500/20',
    rose: 'from-rose-600/20 to-rose-600/5 text-rose-400 border-rose-500/20',
    purple: 'from-purple-600/20 to-purple-600/5 text-purple-400 border-purple-500/20',
    indigo: 'from-indigo-600/20 to-indigo-600/5 text-indigo-400 border-indigo-500/20',
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition shadow-sm relative overflow-hidden">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{title}</p>
          <h3 className="text-2xl font-bold text-white mt-1">{value}</h3>
          {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
        </div>
        {Icon && (
          <div className={`p-3 rounded-lg border bg-gradient-to-br ${colorMap[color] || colorMap.blue}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      {trend && (
        <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center text-xs">
          <span className={trend > 0 ? 'text-emerald-400 font-semibold' : 'text-slate-400'}>
            {trend > 0 ? `+${trend}%` : `${trend}%`}
          </span>
          <span className="text-slate-500 ml-1.5">vs baseline</span>
        </div>
      )}
    </div>
  );
}

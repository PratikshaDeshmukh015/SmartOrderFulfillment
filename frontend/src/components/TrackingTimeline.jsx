import React from 'react';
import { CheckCircle2, Clock, Truck, Package, AlertCircle } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

export function TrackingTimeline({ events = [] }) {
  if (!events || events.length === 0) {
    return (
      <div className="p-6 text-center text-xs text-slate-500">
        No tracking events logged yet for this shipment.
      </div>
    );
  }

  const getIcon = (status) => {
    const s = String(status).toUpperCase();
    if (s === 'DELIVERED') return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
    if (s.includes('DELAY') || s.includes('FAIL')) return <AlertCircle className="w-4 h-4 text-rose-400" />;
    if (s === 'IN_TRANSIT' || s === 'OUT_FOR_DELIVERY') return <Truck className="w-4 h-4 text-blue-400" />;
    return <Package className="w-4 h-4 text-amber-400" />;
  };

  return (
    <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
      {events.map((ev, idx) => (
        <div key={ev.event_id || idx} className="relative group">
          <div className="absolute -left-6 mt-1 w-4 h-4 rounded-full bg-slate-900 border border-slate-700 flex items-center justify-center">
            <span className="w-1.5 h-1.5 rounded-full bg-sky-400"></span>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-3 text-xs">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <StatusBadge status={ev.event_status} />
                <span className="font-semibold text-slate-200">{ev.location}</span>
              </div>
              <span className="font-mono text-[11px] text-slate-400">{ev.event_timestamp}</span>
            </div>
            <p className="text-slate-300 mt-1">{ev.description}</p>
            {ev.is_delayed && (
              <p className="text-rose-400 font-medium mt-1">Delay note: {ev.delay_reason || 'Operational delay encountered'}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

import React from 'react';

export function StatusBadge({ status, type = 'status' }) {
  if (!status) return null;

  const getStyle = () => {
    const s = String(status).toUpperCase();

    // Order / Shipment Status
    if (s === 'DELIVERED' || s === 'FULFILLED' || s === 'RESOLVED') {
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    }
    if (s === 'IN_TRANSIT' || s === 'OUT_FOR_DELIVERY' || s === 'SHIPPED') {
      return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
    }
    if (s === 'ALLOCATED' || s === 'PROCESSING' || s === 'PICKING' || s === 'PACKED' || s === 'READY_FOR_DISPATCH') {
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    }
    if (s === 'PARTIALLY_DELIVERED' || s === 'PARTIALLY_ALLOCATED' || s === 'INVESTIGATING') {
      return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
    }
    if (s === 'EXCEPTION' || s === 'CRITICAL' || s === 'DELIVERY_FAILED' || s === 'FAILED') {
      return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
    }
    if (s === 'HIGH' || s === 'DELIVERY_DELAYED' || s === 'CANCELLED') {
      return 'bg-orange-500/10 text-orange-400 border-orange-500/20';
    }
    if (s === 'MEDIUM' || s === 'OPEN') {
      return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
    }
    if (s === 'LOW' || s === 'CREATED' || s === 'STANDARD') {
      return 'bg-slate-500/10 text-slate-300 border-slate-500/20';
    }
    if (s === 'URGENT' || s === 'EXPRESS') {
      return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20';
    }
    return 'bg-slate-800 text-slate-400 border-slate-700';
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStyle()}`}>
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 bg-current opacity-75"></span>
      {String(status).replace(/_/g, ' ')}
    </span>
  );
}

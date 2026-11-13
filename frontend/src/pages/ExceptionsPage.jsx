import React, { useState, useEffect } from 'react';
import { AlertTriangle, Filter, CheckCircle2, ShieldAlert, Check, RefreshCw } from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';
import { ResolveModal } from '../components/ResolveModal';
import { api } from '../services/api';

export function ExceptionsPage() {
  const [exceptions, setExceptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedException, setSelectedException] = useState(null);

  const fetchExceptions = async () => {
    setLoading(true);
    try {
      const params = { limit: 100 };
      if (severityFilter) params.severity = severityFilter;
      if (statusFilter) params.resolution_status = statusFilter;
      const data = await api.getExceptions(params);
      setExceptions(data);
    } catch (err) {
      console.error('Failed to fetch exceptions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExceptions();
  }, [severityFilter, statusFilter]);

  const handleResolutionSuccess = (resolved) => {
    setExceptions((prev) =>
      prev.map((e) => (e.exception_id === resolved.exception_id ? resolved : e))
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">Exception & Anomaly Control Center</h2>
          <p className="text-xs text-slate-400">
            Automated detection and resolution workflow for warehouse shortages, cutoff violations, and status anomalies.
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-wrap gap-4 items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Filter className="w-3.5 h-3.5" />
            <span>Severity:</span>
          </div>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          <div className="flex items-center gap-2 text-xs text-slate-400 ml-2">
            <span>Status:</span>
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
          >
            <option value="">All Statuses</option>
            <option value="OPEN">Open</option>
            <option value="INVESTIGATING">Investigating</option>
            <option value="RESOLVED">Resolved</option>
            <option value="IGNORED">Ignored</option>
          </select>
        </div>

        <button
          onClick={fetchExceptions}
          className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs flex items-center gap-1.5"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-950 text-slate-400 border-b border-slate-800">
                <th className="py-3 px-4 font-semibold">Exception ID</th>
                <th className="py-3 px-4 font-semibold">Order / Shipment</th>
                <th className="py-3 px-4 font-semibold">Issue Type</th>
                <th className="py-3 px-4 font-semibold">Severity</th>
                <th className="py-3 px-4 font-semibold">Description</th>
                <th className="py-3 px-4 font-semibold">Status</th>
                <th className="py-3 px-4 font-semibold text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {loading ? (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-slate-500 font-sans">
                    Loading exceptions...
                  </td>
                </tr>
              ) : exceptions.length === 0 ? (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-slate-500 font-sans">
                    No exceptions matching criteria.
                  </td>
                </tr>
              ) : (
                exceptions.map((exc) => (
                  <tr key={exc.exception_id} className="hover:bg-slate-800/40">
                    <td className="py-3 px-4 font-bold text-sky-400">{exc.exception_id}</td>
                    <td className="py-3 px-4 text-slate-300">{exc.order_id || exc.shipment_id || '-'}</td>
                    <td className="py-3 px-4 font-sans text-white font-medium">{exc.issue_type.replace(/_/g, ' ')}</td>
                    <td className="py-3 px-4 font-sans"><StatusBadge status={exc.severity} /></td>
                    <td className="py-3 px-4 font-sans text-slate-300 max-w-xs truncate" title={exc.description}>
                      {exc.description}
                    </td>
                    <td className="py-3 px-4 font-sans"><StatusBadge status={exc.resolution_status} /></td>
                    <td className="py-3 px-4 text-center font-sans">
                      {exc.resolution_status === 'RESOLVED' ? (
                        <span className="text-emerald-400 text-xs font-semibold flex items-center justify-center gap-1">
                          <Check className="w-3.5 h-3.5" />
                          <span>Resolved</span>
                        </span>
                      ) : (
                        <button
                          onClick={() => setSelectedException(exc)}
                          className="px-3 py-1 rounded bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 border border-sky-500/30 text-xs font-semibold transition"
                        >
                          Resolve
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Resolve Modal */}
      <ResolveModal
        exception={selectedException}
        isOpen={!!selectedException}
        onClose={() => setSelectedException(null)}
        onSuccess={handleResolutionSuccess}
      />
    </div>
  );
}

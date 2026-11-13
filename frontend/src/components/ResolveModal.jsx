import React, { useState } from 'react';
import { X, CheckCircle, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';

export function ResolveModal({ exception, isOpen, onClose, onSuccess }) {
  if (!isOpen || !exception) return null;

  const [notes, setNotes] = useState('');
  const [resolvedBy, setResolvedBy] = useState('SupplyChainOps');
  const [status, setStatus] = useState('RESOLVED');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const res = await api.resolveException(exception.exception_id, {
        resolution_notes: notes || 'Resolved via manual operational intervention.',
        resolved_by: resolvedBy,
        resolution_status: status,
      });
      setIsSubmitting(false);
      onSuccess(res);
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to resolve exception');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-slate-400 hover:text-white p-1 rounded-lg"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2 mb-2">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          <h2 className="text-base font-bold text-white">Resolve Exception</h2>
        </div>
        <p className="text-xs font-mono text-slate-400 mb-4">{exception.exception_id}</p>

        <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs mb-4">
          <p className="text-slate-300 font-medium">{exception.description}</p>
          <p className="text-slate-500 mt-1">Expected: {exception.expected_behavior}</p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Resolution Status</label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
            >
              <option value="RESOLVED">Resolved</option>
              <option value="INVESTIGATING">Under Investigation</option>
              <option value="IGNORED">Ignored (Expected Anomaly)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Resolved By</label>
            <input
              type="text"
              required
              value={resolvedBy}
              onChange={(e) => setResolvedBy(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Resolution Notes</label>
            <textarea
              rows="3"
              required
              placeholder="Explain the corrective action taken..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
            ></textarea>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 rounded-lg text-xs font-semibold bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition flex items-center gap-1.5"
            >
              <CheckCircle className="w-4 h-4" />
              <span>{isSubmitting ? 'Saving...' : 'Confirm Resolution'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

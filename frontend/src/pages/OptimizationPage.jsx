import React, { useState, useEffect } from 'react';
import {
  Cpu,
  Sliders,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  TrendingDown,
  Layers,
  ShieldCheck,
  Truck,
  RotateCcw
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';
import { StatusBadge } from '../components/StatusBadge';
import { api } from '../services/api';

export function OptimizationPage({ selectedOrderId, setSelectedOrderId }) {
  const [orderId, setOrderId] = useState(selectedOrderId || 'ORD-2026-000001');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [baselineData, setBaselineData] = useState(null);
  const [error, setError] = useState(null);

  // Optimization Factor Weights (Sum = 1.0)
  const [weights, setWeights] = useState({
    inventory: 0.30,
    speed: 0.25,
    capacity: 0.15,
    cost: 0.15,
    reliability: 0.10,
    risk: 0.05,
  });

  const resetWeights = () => {
    setWeights({
      inventory: 0.30,
      speed: 0.25,
      capacity: 0.15,
      cost: 0.15,
      reliability: 0.10,
      risk: 0.05,
    });
  };

  const handleOptimize = async () => {
    setLoading(true);
    setError(null);
    setBaselineData(null);
    try {
      const data = await api.optimizeOrder(orderId, weights);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to optimize order fulfillment');
    } finally {
      setLoading(false);
    }
  };

  const handleCompareBaseline = async () => {
    try {
      const comp = await api.compareBaseline(orderId);
      setBaselineData(comp);
    } catch (err) {
      console.error('Failed to compare baseline:', err);
    }
  };

  useEffect(() => {
    if (orderId) {
      handleOptimize();
    }
  }, [orderId]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white">Fulfillment Decision Engine</h2>
        <p className="text-xs text-slate-400">
          Simulate multi-criteria warehouse selection, dynamic split allocation, and delivery promise calculations.
        </p>
      </div>

      {/* Simulator Control Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Order Selector & Weight Adjustment */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Sliders className="w-4 h-4 text-sky-400" />
              <span>Weight Configuration</span>
            </h3>
            <button
              onClick={resetWeights}
              className="text-[11px] text-slate-400 hover:text-white flex items-center gap-1"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Reset</span>
            </button>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Target Order ID</label>
            <div className="flex gap-2">
              <input
                type="text"
                value={orderId}
                onChange={(e) => setOrderId(e.target.value)}
                placeholder="e.g. ORD-2026-000001"
                className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-sky-500"
              />
              <button
                onClick={handleOptimize}
                disabled={loading}
                className="px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-bold transition shrink-0"
              >
                {loading ? 'Optimizing...' : 'Run'}
              </button>
            </div>
          </div>

          {/* Sliders */}
          <div className="space-y-3 pt-2 border-t border-slate-800 text-xs">
            <div>
              <div className="flex justify-between text-slate-300 mb-1">
                <span>Inventory Availability:</span>
                <span className="font-mono text-sky-400 font-semibold">{Math.round(weights.inventory * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="0.6"
                step="0.05"
                value={weights.inventory}
                onChange={(e) => setWeights({ ...weights, inventory: parseFloat(e.target.value) })}
                className="w-full accent-sky-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-slate-300 mb-1">
                <span>Delivery Speed:</span>
                <span className="font-mono text-sky-400 font-semibold">{Math.round(weights.speed * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="0.6"
                step="0.05"
                value={weights.speed}
                onChange={(e) => setWeights({ ...weights, speed: parseFloat(e.target.value) })}
                className="w-full accent-sky-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-slate-300 mb-1">
                <span>Warehouse Capacity:</span>
                <span className="font-mono text-sky-400 font-semibold">{Math.round(weights.capacity * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="0.4"
                step="0.05"
                value={weights.capacity}
                onChange={(e) => setWeights({ ...weights, capacity: parseFloat(e.target.value) })}
                className="w-full accent-sky-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-slate-300 mb-1">
                <span>Shipping Cost:</span>
                <span className="font-mono text-sky-400 font-semibold">{Math.round(weights.cost * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="0.4"
                step="0.05"
                value={weights.cost}
                onChange={(e) => setWeights({ ...weights, cost: parseFloat(e.target.value) })}
                className="w-full accent-sky-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-slate-300 mb-1">
                <span>Carrier Reliability:</span>
                <span className="font-mono text-sky-400 font-semibold">{Math.round(weights.reliability * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="0.3"
                step="0.05"
                value={weights.reliability}
                onChange={(e) => setWeights({ ...weights, reliability: parseFloat(e.target.value) })}
                className="w-full accent-sky-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-slate-300 mb-1">
                <span>Operational Risk:</span>
                <span className="font-mono text-sky-400 font-semibold">{Math.round(weights.risk * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="0.2"
                step="0.05"
                value={weights.risk}
                onChange={(e) => setWeights({ ...weights, risk: parseFloat(e.target.value) })}
                className="w-full accent-sky-500"
              />
            </div>
          </div>
        </div>

        {/* Selected Decision Outcome Card */}
        <div className="lg:col-span-2 space-y-4">
          {error && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
              {error}
            </div>
          )}

          {result && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-5">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[11px] font-mono text-sky-400 uppercase tracking-wider block">
                    Optimized Fulfillment Decision
                  </span>
                  <h3 className="text-lg font-bold text-white mt-0.5">
                    {result.strategy === 'EXCEPTION_NO_NODE' ? 'Fulfillment Exception' : result.selected_node_name}
                  </h3>
                  <p className="text-xs text-slate-400 font-mono">Decision ID: {result.decision_id || 'N/A'}</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-black text-sky-400 font-mono">
                    {result.weighted_score > 0 ? `${result.weighted_score}/100` : '0/100'}
                  </div>
                  <span className="text-[10px] text-slate-400 uppercase tracking-widest">Weighted Score</span>
                </div>
              </div>

              {/* Decision Factor Breakdown Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs">
                <div>
                  <span className="text-slate-500 block">Warehouse Node</span>
                  <span className="font-semibold text-slate-200">{result.selected_node_id || 'None'}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Carrier & Service</span>
                  <span className="font-semibold text-slate-200">
                    {result.selected_carrier ? `${result.selected_carrier} (${result.selected_service})` : 'None'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block">Shipping Cost</span>
                  <span className="font-mono font-bold text-white">${result.shipping_cost.toFixed(2)}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Engine Latency</span>
                  <span className="font-mono text-emerald-400 font-semibold">{result.execution_time_ms} ms</span>
                </div>
              </div>

              {/* Explainability Section */}
              <div className="bg-sky-950/20 border border-sky-900/30 rounded-xl p-4 text-xs">
                <h4 className="text-xs font-bold text-sky-300 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-sky-400" />
                  <span>Explainability & Decision Audit</span>
                </h4>
                <p className="text-slate-300 leading-relaxed">{result.decision_reason}</p>
              </div>

              {/* Split Fulfillment Notice */}
              {result.is_split && result.split_details && (
                <div className="p-4 rounded-xl bg-purple-500/10 border border-purple-500/20 text-xs space-y-2">
                  <div className="flex items-center gap-2 text-purple-400 font-bold">
                    <Layers className="w-4 h-4" />
                    <span>Split Fulfillment Activated</span>
                  </div>
                  <p className="text-slate-300">
                    Order lines split across multiple fulfillment nodes to satisfy demand:
                  </p>
                  <div className="grid grid-cols-2 gap-2 mt-2">
                    {result.split_details.map((sp, idx) => (
                      <div key={idx} className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                        <span className="font-semibold text-white block">{sp.node_name} ({sp.city})</span>
                        <span className="text-slate-400 text-[11px]">
                          Items: {sp.items.map((it) => `${it.sku_id} (${it.allocated_quantity}u)`).join(', ')}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Compare with Baseline Button */}
              <div className="flex justify-between items-center pt-2">
                <button
                  onClick={handleCompareBaseline}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sky-400 text-xs font-semibold border border-slate-700 flex items-center gap-2 transition"
                >
                  <TrendingDown className="w-4 h-4" />
                  <span>Compare with Baseline (Nearest Warehouse)</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Head-to-Head Baseline Comparison Card */}
      {baselineData && (
        <div className="bg-slate-900 border border-sky-900/40 rounded-xl p-5 shadow-lg space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Head-to-Head Strategy Benchmark</span>
            </h3>
            <span className="text-xs font-mono text-emerald-400 font-bold bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
              {baselineData.risk_reduction_pct}% Risk Reduction
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl text-xs space-y-2">
              <span className="text-slate-400 font-bold uppercase tracking-wider block">
                {baselineData.baseline.strategy_name}
              </span>
              <p className="text-slate-300">Selected: {baselineData.baseline.node_name}</p>
              <p className="text-slate-400">Distance: {baselineData.baseline.distance_km} km</p>
              <p className="text-slate-300">Transit Days: {baselineData.baseline.transit_days} days</p>
              <p className="text-slate-300">Shipping Cost: ${baselineData.baseline.shipping_cost.toFixed(2)}</p>
              <p className="text-rose-400 font-medium">Risk Score: {baselineData.baseline.risk_score}/100 (High Risk)</p>
            </div>

            <div className="bg-sky-950/20 border border-sky-800/40 p-4 rounded-xl text-xs space-y-2">
              <span className="text-sky-400 font-bold uppercase tracking-wider block">
                {baselineData.optimized.strategy_name}
              </span>
              <p className="text-slate-200">Selected: {baselineData.optimized.node_name}</p>
              <p className="text-slate-300">Carrier: {baselineData.optimized.carrier} ({baselineData.optimized.service})</p>
              <p className="text-slate-200">Transit Days: {baselineData.optimized.transit_days} days</p>
              <p className="text-slate-200">Shipping Cost: ${baselineData.optimized.shipping_cost.toFixed(2)}</p>
              <p className="text-emerald-400 font-semibold">Risk Score: {baselineData.optimized.risk_score}/100 (Optimal)</p>
            </div>
          </div>

          <p className="text-xs text-slate-300 bg-slate-950 p-3 rounded-lg border border-slate-800">
            {baselineData.improvement_summary}
          </p>
        </div>
      )}

      {/* Candidate Warehouse Options Comparison Table */}
      {result && result.candidate_options && result.candidate_options.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <div className="p-4 border-b border-slate-800">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              Eligible Candidate Warehouses & Service Levels
            </h3>
            <p className="text-xs text-slate-400">Ranked by weighted multi-factor composite score</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-slate-950 text-slate-400">
                  <th className="py-2.5 px-4 font-semibold">Rank</th>
                  <th className="py-2.5 px-4 font-semibold">Fulfillment Center</th>
                  <th className="py-2.5 px-4 font-semibold">Carrier & Service</th>
                  <th className="py-2.5 px-4 font-semibold">Transit</th>
                  <th className="py-2.5 px-4 font-semibold">Shipping Cost</th>
                  <th className="py-2.5 px-4 font-semibold">Speed Score</th>
                  <th className="py-2.5 px-4 font-semibold">Capacity Score</th>
                  <th className="py-2.5 px-4 font-semibold text-right">Composite Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {result.candidate_options.map((opt, idx) => (
                  <tr
                    key={idx}
                    className={`hover:bg-slate-800/40 ${idx === 0 ? 'bg-sky-500/5 font-medium' : ''}`}
                  >
                    <td className="py-2.5 px-4 font-mono font-bold text-slate-400">#{idx + 1}</td>
                    <td className="py-2.5 px-4 font-medium text-white">{opt.node_name}</td>
                    <td className="py-2.5 px-4 text-slate-300">{opt.carrier_name} - {opt.service_name}</td>
                    <td className="py-2.5 px-4 font-mono text-slate-300">{opt.transit_days}d</td>
                    <td className="py-2.5 px-4 font-mono text-slate-200">${opt.shipping_cost.toFixed(2)}</td>
                    <td className="py-2.5 px-4 text-slate-300">{opt.factor_scores.delivery_speed}/100</td>
                    <td className="py-2.5 px-4 text-slate-300">{opt.factor_scores.warehouse_capacity}/100</td>
                    <td className="py-2.5 px-4 text-right font-mono font-bold text-sky-400">
                      {opt.weighted_score}/100
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

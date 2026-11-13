import React, { useEffect, useState } from 'react';
import {
  ShoppingCart,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Truck,
  Percent,
  TrendingUp,
  Cpu,
  Layers,
  ArrowRight
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  CartesianGrid,
  LineChart,
  Line
} from 'recharts';
import { StatCard } from '../components/StatCard';
import { StatusBadge } from '../components/StatusBadge';
import { api } from '../services/api';

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ef4444'];

export function DashboardPage({ setTab, setSelectedOrder }) {
  const [overview, setOverview] = useState(null);
  const [carrierData, setCarrierData] = useState([]);
  const [exceptions, setExceptions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [ov, cars, excs] = await Promise.all([
          api.getOverviewMetrics(),
          api.getCarrierAnalytics(),
          api.getExceptions({ limit: 5 }),
        ]);
        setOverview(ov);
        setCarrierData(cars);
        setExceptions(excs);
      } catch (err) {
        console.error('Dashboard load failed:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading || !overview) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex items-center gap-3 text-sky-400 font-mono text-sm">
          <span className="w-3 h-3 rounded-full bg-sky-400 animate-ping"></span>
          Loading Supply Chain Intelligence...
        </div>
      </div>
    );
  }

  const statusDistribution = [
    { name: 'Delivered', value: overview.fulfilled_orders },
    { name: 'Pending / In Transit', value: overview.pending_orders },
    { name: 'Delayed', value: overview.delayed_orders },
    { name: 'Exceptions', value: overview.active_exceptions },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-sky-950/60 via-slate-900 to-indigo-950/40 border border-sky-900/30 rounded-2xl p-6 flex items-center justify-between shadow-lg">
        <div>
          <span className="text-xs font-mono font-semibold text-sky-400 uppercase tracking-widest">
            Fulfillment Optimization Platform
          </span>
          <h2 className="text-2xl font-black text-white mt-1">Global Fulfillment Command Center</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Real-time multi-echelon order routing, warehouse capacity balancing, carrier transit evaluation,
            and promise date optimization with deterministic reproducibility.
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setTab('optimization')}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-bold transition shadow-md"
          >
            <Cpu className="w-4 h-4" />
            <span>Launch Optimizer</span>
          </button>
        </div>
      </div>

      {/* 8 Core Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Orders"
          value={overview.total_orders.toLocaleString()}
          subtitle="Processed across 20 nodes"
          icon={ShoppingCart}
          color="blue"
        />
        <StatCard
          title="Fulfilled Orders"
          value={overview.fulfilled_orders.toLocaleString()}
          subtitle={`${overview.fulfillment_success_rate}% success rate`}
          icon={CheckCircle2}
          color="emerald"
        />
        <StatCard
          title="On-Time Delivery Rate"
          value={`${overview.on_time_delivery_pct}%`}
          subtitle="Promised vs Actual accuracy"
          icon={Percent}
          color="emerald"
          trend={+12.4}
        />
        <StatCard
          title="Avg Delivery Time"
          value={`${overview.avg_delivery_days} days`}
          subtitle="Transit from order dispatch"
          icon={Clock}
          color="indigo"
          trend={-53.0}
        />
        <StatCard
          title="Split Shipment Rate"
          value={`${overview.split_shipment_pct}%`}
          subtitle="Multi-warehouse fulfillment"
          icon={Layers}
          color="purple"
        />
        <StatCard
          title="Avg Shipping Cost"
          value={`$${overview.avg_shipping_cost.toFixed(2)}`}
          subtitle="Per fulfilled order"
          icon={Truck}
          color="blue"
        />
        <StatCard
          title="Active Exceptions"
          value={overview.active_exceptions}
          subtitle={`${overview.total_exceptions} total detected`}
          icon={AlertTriangle}
          color={overview.active_exceptions > 0 ? 'rose' : 'emerald'}
        />
        <StatCard
          title="Network Inventory"
          value={overview.total_inventory_units.toLocaleString()}
          subtitle="Units across all SKUs"
          icon={TrendingUp}
          color="amber"
        />
      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Carrier Scorecard Bar Chart */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white">Carrier Performance Scorecard</h3>
              <p className="text-xs text-slate-400">On-time delivery percentage by logistics carrier</p>
            </div>
            <button
              onClick={() => setTab('analytics')}
              className="text-xs text-sky-400 hover:text-sky-300 flex items-center gap-1 font-medium"
            >
              <span>Full Analytics</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={carrierData.slice(0, 7)} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="carrier_name" stroke="#64748b" fontSize={10} angle={-15} textAnchor="end" />
                <YAxis stroke="#64748b" fontSize={11} domain={[70, 100]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="on_time_pct" name="On-Time %" fill="#0284c7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Fulfillment Status Pie Chart */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-sm">
          <h3 className="text-sm font-bold text-white mb-1">Fulfillment Status Rollup</h3>
          <p className="text-xs text-slate-400 mb-4">Network-wide order allocation lifecycle</p>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statusDistribution}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={70}
                  paddingAngle={4}
                >
                  {statusDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-2">
            {statusDistribution.map((item, idx) => (
              <div key={item.name} className="flex items-center gap-2 text-xs">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }}></span>
                <span className="text-slate-400">{item.name}:</span>
                <span className="font-semibold text-slate-200">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Active Exceptions Watchlist */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400" />
            <h3 className="text-sm font-bold text-white">Active Fulfillment Exceptions Watchlist</h3>
          </div>
          <button
            onClick={() => setTab('exceptions')}
            className="text-xs text-sky-400 hover:text-sky-300 font-medium"
          >
            View All Exceptions ({overview.active_exceptions})
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-2 font-medium">Exception ID</th>
                <th className="pb-2 font-medium">Order / Shipment</th>
                <th className="pb-2 font-medium">Issue Type</th>
                <th className="pb-2 font-medium">Severity</th>
                <th className="pb-2 font-medium">Status</th>
                <th className="pb-2 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {exceptions.map((exc) => (
                <tr key={exc.exception_id} className="hover:bg-slate-800/30">
                  <td className="py-2.5 font-mono text-sky-400">{exc.exception_id}</td>
                  <td className="py-2.5 font-mono text-slate-300">{exc.order_id || exc.shipment_id || '-'}</td>
                  <td className="py-2.5 text-slate-300">{exc.issue_type.replace(/_/g, ' ')}</td>
                  <td className="py-2.5"><StatusBadge status={exc.severity} /></td>
                  <td className="py-2.5"><StatusBadge status={exc.resolution_status} /></td>
                  <td className="py-2.5 text-right">
                    <button
                      onClick={() => setTab('exceptions')}
                      className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] font-medium"
                    >
                      Resolve
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { Warehouse, MapPin, Clock, Calendar, CheckCircle, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';

export function WarehousesPage() {
  const [nodes, setNodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [capacities, setCapacities] = useState([]);

  useEffect(() => {
    async function fetchNodes() {
      try {
        const data = await api.getNodes();
        setNodes(data);
        if (data && data.length > 0) {
          setSelectedNodeId(data[0].node_id);
        }
      } catch (err) {
        console.error('Failed to fetch nodes:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchNodes();
  }, []);

  useEffect(() => {
    if (selectedNodeId) {
      api.getNodeCapacity(selectedNodeId)
        .then((data) => setCapacities(data))
        .catch((e) => console.error(e));
    }
  }, [selectedNodeId]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white">Fulfillment Center Network</h2>
        <p className="text-xs text-slate-400">
          Manage 20 regional hubs, distribution facilities, operating schedules, and daily throughput capacity.
        </p>
      </div>

      {/* Grid of Warehouses */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {nodes.map((n) => {
          const isSelected = selectedNodeId === n.node_id;
          return (
            <div
              key={n.node_id}
              onClick={() => setSelectedNodeId(n.node_id)}
              className={`p-4 rounded-xl border cursor-pointer transition ${
                isSelected
                  ? 'bg-slate-900 border-sky-500 shadow-md ring-1 ring-sky-500/50'
                  : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <span className="text-[10px] font-mono text-sky-400 uppercase tracking-widest">{n.node_id}</span>
                  <h3 className="text-sm font-bold text-white">{n.node_name}</h3>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                  {n.node_type.replace(/_/g, ' ')}
                </span>
              </div>

              <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-3">
                <MapPin className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                <span>{n.address}, {n.city}, {n.state} {n.zip_code}</span>
              </div>

              <div className="grid grid-cols-2 gap-2 bg-slate-950 p-2.5 rounded-lg border border-slate-800/80 text-[11px] mb-3">
                <div>
                  <span className="text-slate-500 block">Daily Order Cap</span>
                  <span className="font-mono font-semibold text-slate-200">{n.daily_order_capacity} orders</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Cutoff Time</span>
                  <span className="font-mono font-semibold text-sky-400">{n.processing_cutoff_time}</span>
                </div>
              </div>

              <div className="flex items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-slate-800">
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3 text-slate-400" />
                  <span>{n.operating_hours_start} - {n.operating_hours_end}</span>
                </div>
                <span>{n.weekend_operations ? '7-Day Ops' : 'Mon - Fri'}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Node Daily Capacity Utilization View */}
      {selectedNodeId && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white">Daily Throughput & Capacity Utilization</h3>
              <p className="text-xs text-slate-400">Node: {selectedNodeId} - Historical Capacity Headroom</p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-slate-950 text-slate-400 border-b border-slate-800">
                  <th className="py-2.5 px-4 font-semibold">Date</th>
                  <th className="py-2.5 px-4 font-semibold">Max Orders</th>
                  <th className="py-2.5 px-4 font-semibold">Utilized Orders</th>
                  <th className="py-2.5 px-4 font-semibold">Order Utilization</th>
                  <th className="py-2.5 px-4 font-semibold">Max Units</th>
                  <th className="py-2.5 px-4 font-semibold">Utilized Units</th>
                  <th className="py-2.5 px-4 font-semibold text-right">Headroom Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {capacities.slice(0, 10).map((c) => (
                  <tr key={c.capacity_id} className="hover:bg-slate-800/30">
                    <td className="py-2 px-4 text-slate-300">{c.date}</td>
                    <td className="py-2 px-4 text-slate-400">{c.max_orders}</td>
                    <td className="py-2 px-4 text-white font-semibold">{c.utilized_orders}</td>
                    <td className="py-2 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                          <div
                            className={`h-full ${c.order_utilization_pct > 80 ? 'bg-rose-500' : 'bg-sky-500'}`}
                            style={{ width: `${Math.min(100, c.order_utilization_pct)}%` }}
                          ></div>
                        </div>
                        <span className="text-slate-300">{c.order_utilization_pct}%</span>
                      </div>
                    </td>
                    <td className="py-2 px-4 text-slate-400">{c.max_units}</td>
                    <td className="py-2 px-4 text-white">{c.utilized_units}</td>
                    <td className="py-2 px-4 text-right">
                      {c.order_utilization_pct > 85 ? (
                        <span className="text-rose-400 font-sans text-[11px] font-bold">Near Capacity</span>
                      ) : (
                        <span className="text-emerald-400 font-sans text-[11px] font-bold">Available</span>
                      )}
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

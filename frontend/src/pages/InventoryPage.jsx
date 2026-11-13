import React, { useState, useEffect } from 'react';
import { Package, AlertCircle, Search, Filter, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';

export function InventoryPage() {
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [lowStockOnly, setLowStockOnly] = useState(false);

  const fetchInventory = async () => {
    setLoading(true);
    try {
      const params = {};
      if (lowStockOnly) params.low_stock_only = true;
      const data = await api.getInventory(params);
      setInventory(data);
    } catch (err) {
      console.error('Failed to fetch inventory:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInventory();
  }, [lowStockOnly]);

  const filtered = inventory.filter((item) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      item.sku_id.toLowerCase().includes(q) ||
      (item.sku_name && item.sku_name.toLowerCase().includes(q)) ||
      (item.node_name && item.node_name.toLowerCase().includes(q)) ||
      (item.city && item.city.toLowerCase().includes(q))
    );
  });

  const lowStockCount = inventory.filter((i) => i.is_low_stock).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">Network Inventory Management</h2>
          <p className="text-xs text-slate-400">
            Real-time multi-warehouse SKU availability, reserved quantities, and safety buffer thresholds.
          </p>
        </div>
        {lowStockCount > 0 && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold">
            <AlertTriangle className="w-4 h-4" />
            <span>{lowStockCount} Low-Stock Alerts</span>
          </div>
        )}
      </div>

      {/* Filters */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row gap-3 items-center justify-between">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-2.5" />
          <input
            type="text"
            placeholder="Search by SKU ID, Product Name, Warehouse, or City..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
          />
        </div>

        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={lowStockOnly}
              onChange={(e) => setLowStockOnly(e.target.checked)}
              className="accent-sky-500 rounded"
            />
            <span>Show Low-Stock Only</span>
          </label>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-950 text-slate-400 border-b border-slate-800">
                <th className="py-3 px-4 font-semibold">SKU ID</th>
                <th className="py-3 px-4 font-semibold">Product Name</th>
                <th className="py-3 px-4 font-semibold">Category</th>
                <th className="py-3 px-4 font-semibold">Fulfillment Node</th>
                <th className="py-3 px-4 font-semibold text-right">Available</th>
                <th className="py-3 px-4 font-semibold text-right">Reserved</th>
                <th className="py-3 px-4 font-semibold text-right">Reorder Threshold</th>
                <th className="py-3 px-4 font-semibold text-center">Stock Health</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan="8" className="py-12 text-center text-slate-500">
                    Loading inventory data...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan="8" className="py-12 text-center text-slate-500">
                    No matching inventory records.
                  </td>
                </tr>
              ) : (
                filtered.map((item) => (
                  <tr key={item.inventory_id} className="hover:bg-slate-800/40">
                    <td className="py-3 px-4 font-mono font-semibold text-sky-400">{item.sku_id}</td>
                    <td className="py-3 px-4 text-white font-medium">{item.sku_name}</td>
                    <td className="py-3 px-4 text-slate-400">{item.category}</td>
                    <td className="py-3 px-4 text-slate-300">{item.node_name} ({item.city})</td>
                    <td className="py-3 px-4 text-right font-mono font-bold text-slate-200">
                      {item.available_quantity}
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-slate-400">
                      {item.reserved_quantity}
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-slate-400">
                      {item.reorder_threshold}
                    </td>
                    <td className="py-3 px-4 text-center">
                      {item.is_low_stock ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                          Low Stock
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          Healthy
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

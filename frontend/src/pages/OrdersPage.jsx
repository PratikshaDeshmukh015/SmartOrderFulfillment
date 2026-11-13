import React, { useEffect, useState } from 'react';
import { Search, Filter, ShoppingCart, Eye, Cpu, ChevronRight, X, Package } from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';
import { api } from '../services/api';

export function OrdersPage({ setTab, setSelectedOrderId, onNewOrder }) {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [activePromise, setActivePromise] = useState(null);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const params = { limit: 100 };
      if (statusFilter) params.status = statusFilter;
      if (search) params.search = search;
      const data = await api.getOrders(params);
      setOrders(data);
    } catch (err) {
      console.error('Failed to fetch orders:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, [statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchOrders();
  };

  const openOrderDetail = async (order) => {
    setSelectedOrder(order);
    try {
      const promises = await api.getOrderPromises(order.order_id);
      setActivePromise(promises && promises.length > 0 ? promises[0] : null);
    } catch (e) {
      setActivePromise(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">Order Management</h2>
          <p className="text-xs text-slate-400">
            Monitor incoming demand, order priorities, line allocations, and promised delivery windows.
          </p>
        </div>
        <button
          onClick={onNewOrder}
          className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-semibold self-start sm:self-auto"
        >
          <ShoppingCart className="w-4 h-4" />
          <span>New Customer Order</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row gap-3 items-center justify-between">
        <form onSubmit={handleSearchSubmit} className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-2.5" />
          <input
            type="text"
            placeholder="Search by Order ID, Customer Name, or City..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
          />
        </form>

        <div className="flex items-center gap-3 w-full md:w-auto">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Filter className="w-3.5 h-3.5" />
            <span>Status:</span>
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
          >
            <option value="">All Statuses</option>
            <option value="CREATED">Created</option>
            <option value="ALLOCATED">Allocated</option>
            <option value="PROCESSING">Processing</option>
            <option value="SHIPPED">Shipped</option>
            <option value="DELIVERED">Delivered</option>
            <option value="EXCEPTION">Exception</option>
          </select>
        </div>
      </div>

      {/* Orders Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-950/60 border-b border-slate-800 text-slate-400">
                <th className="py-3 px-4 font-semibold">Order ID</th>
                <th className="py-3 px-4 font-semibold">Customer</th>
                <th className="py-3 px-4 font-semibold">Destination</th>
                <th className="py-3 px-4 font-semibold">Zone</th>
                <th className="py-3 px-4 font-semibold">Priority</th>
                <th className="py-3 px-4 font-semibold">Status</th>
                <th className="py-3 px-4 font-semibold">Promised Delivery</th>
                <th className="py-3 px-4 font-semibold text-right">Total</th>
                <th className="py-3 px-4 font-semibold text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan="9" className="py-12 text-center text-slate-500">
                    Loading orders...
                  </td>
                </tr>
              ) : orders.length === 0 ? (
                <tr>
                  <td colSpan="9" className="py-12 text-center text-slate-500">
                    No matching orders found.
                  </td>
                </tr>
              ) : (
                orders.map((o) => (
                  <tr key={o.order_id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-4 font-mono font-semibold text-sky-400">{o.order_id}</td>
                    <td className="py-3 px-4 text-slate-200">{o.customer_name}</td>
                    <td className="py-3 px-4 text-slate-300">{o.destination_city}, {o.destination_state}</td>
                    <td className="py-3 px-4 text-slate-400 font-mono">{o.destination_zone}</td>
                    <td className="py-3 px-4"><StatusBadge status={o.order_priority} /></td>
                    <td className="py-3 px-4"><StatusBadge status={o.order_status} /></td>
                    <td className="py-3 px-4 font-mono text-slate-300">
                      {o.promised_delivery_date ? o.promised_delivery_date.split('T')[0] : 'Calculating...'}
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-slate-200 font-semibold">
                      ${o.total_amount.toFixed(2)}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <div className="flex items-center justify-center gap-1.5">
                        <button
                          onClick={() => openOrderDetail(o)}
                          className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition"
                          title="View Details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => {
                            setSelectedOrderId(o.order_id);
                            setTab('optimization');
                          }}
                          className="p-1.5 rounded bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 border border-sky-500/20 transition"
                          title="Run Optimizer"
                        >
                          <Cpu className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Order Details Drawer / Modal */}
      {selectedOrder && (
        <div className="fixed inset-0 z-50 flex items-center justify-end bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-xl h-full bg-slate-900 border-l border-slate-800 p-6 overflow-y-auto shadow-2xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <div>
                  <h3 className="text-base font-bold text-white font-mono">{selectedOrder.order_id}</h3>
                  <p className="text-xs text-slate-400 mt-0.5">Placed: {selectedOrder.placed_at}</p>
                </div>
                <button
                  onClick={() => setSelectedOrder(null)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-white"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Order Metadata */}
              <div className="grid grid-cols-2 gap-4 py-4 text-xs border-b border-slate-800">
                <div>
                  <span className="text-slate-500 block mb-1">Customer Information</span>
                  <p className="font-semibold text-slate-200">{selectedOrder.customer_name}</p>
                  <p className="text-slate-400">{selectedOrder.customer_email}</p>
                </div>
                <div>
                  <span className="text-slate-500 block mb-1">Delivery Destination</span>
                  <p className="font-semibold text-slate-200">{selectedOrder.destination_address}</p>
                  <p className="text-slate-400">{selectedOrder.destination_city}, {selectedOrder.destination_state} {selectedOrder.destination_zip}</p>
                  <span className="inline-block mt-1 text-[11px] font-mono text-sky-400">{selectedOrder.destination_zone}</span>
                </div>
              </div>

              {/* Order Status & Promise */}
              <div className="py-4 space-y-3 border-b border-slate-800 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Order Status:</span>
                  <StatusBadge status={selectedOrder.order_status} />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Fulfillment Mode:</span>
                  <span className="font-semibold text-slate-200">
                    {selectedOrder.is_split ? 'Split Fulfillment (Multi-Warehouse)' : 'Single Warehouse'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Promised Delivery Date:</span>
                  <span className="font-mono text-emerald-400 font-semibold">
                    {selectedOrder.promised_delivery_date || 'Pending Calculation'}
                  </span>
                </div>
              </div>

              {/* Order Lines Table */}
              <div className="py-4">
                <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">Order Line Items</h4>
                <div className="space-y-2">
                  {selectedOrder.lines && selectedOrder.lines.map((l) => (
                    <div key={l.order_line_id} className="bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Package className="w-4 h-4 text-sky-400" />
                        <div>
                          <p className="font-mono text-slate-200 font-semibold">{l.sku_id}</p>
                          <p className="text-slate-400 text-[11px]">Quantity: {l.quantity} units</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-mono text-white font-semibold">${l.line_total.toFixed(2)}</p>
                        <p className="text-[11px] text-slate-400">${l.unit_price.toFixed(2)} / unit</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Action buttons */}
            <div className="pt-6 border-t border-slate-800 flex gap-3">
              <button
                onClick={() => {
                  setSelectedOrderId(selectedOrder.order_id);
                  setTab('optimization');
                  setSelectedOrder(null);
                }}
                className="w-full py-2.5 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-bold transition flex items-center justify-center gap-2"
              >
                <Cpu className="w-4 h-4" />
                <span>Simulate & Optimize Fulfillment</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

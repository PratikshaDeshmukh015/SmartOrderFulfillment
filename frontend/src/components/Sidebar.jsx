import React from 'react';
import {
  LayoutDashboard,
  ShoppingCart,
  Cpu,
  Package,
  Warehouse,
  Truck,
  AlertTriangle,
  BarChart3,
  Layers
} from 'lucide-react';

export function Sidebar({ currentTab, setTab, activeExceptionsCount = 0 }) {
  const navItems = [
    { id: 'dashboard', label: 'Executive Dashboard', icon: LayoutDashboard },
    { id: 'orders', label: 'Order Management', icon: ShoppingCart },
    { id: 'optimization', label: 'Fulfillment Optimizer', icon: Cpu },
    { id: 'inventory', label: 'Inventory Network', icon: Package },
    { id: 'warehouses', label: 'Warehouse Centers', icon: Warehouse },
    { id: 'shipments', label: 'Shipment Tracking', icon: Truck },
    { id: 'exceptions', label: 'Exception Control', icon: AlertTriangle, badge: activeExceptionsCount },
    { id: 'analytics', label: 'Benchmarks & Reports', icon: BarChart3 },
  ];

  return (
    <aside className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col shrink-0 min-h-screen">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-3">
        <div className="w-9 h-9 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400">
          <Layers className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-sm font-bold text-white tracking-wide">SMART FULFILLMENT</h1>
          <p className="text-[10px] text-sky-400 font-mono tracking-widest uppercase">Decision Engine 2.0</p>
        </div>
      </div>

      {/* Nav List */}
      <nav className="p-3 space-y-1 flex-1 overflow-y-auto">
        <div className="px-3 py-2 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
          Supply Chain Core
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setTab(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? 'bg-sky-500/15 text-sky-400 border border-sky-500/30 font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-sky-400' : 'text-slate-500'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge > 0 && (
                <span className="px-1.5 py-0.5 text-[10px] rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30 font-bold">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950 text-xs text-slate-500">
        <div className="flex items-center justify-between">
          <span className="flex items-center gap-1.5 text-emerald-400 font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            ENGINE READY
          </span>
          <span className="font-mono text-[10px]">SEED: 20261022</span>
        </div>
      </div>
    </aside>
  );
}

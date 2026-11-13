import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { OrderModal } from './components/OrderModal';
import { DashboardPage } from './pages/DashboardPage';
import { OrdersPage } from './pages/OrdersPage';
import { OptimizationPage } from './pages/OptimizationPage';
import { InventoryPage } from './pages/InventoryPage';
import { WarehousesPage } from './pages/WarehousesPage';
import { ShipmentsPage } from './pages/ShipmentsPage';
import { ExceptionsPage } from './pages/ExceptionsPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { api } from './services/api';

export default function App() {
  const [currentTab, setTab] = useState('dashboard');
  const [selectedOrderId, setSelectedOrderId] = useState('ORD-2026-000001');
  const [isOrderModalOpen, setOrderModalOpen] = useState(false);
  const [activeExceptionsCount, setActiveExceptionsCount] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const fetchGlobalState = async () => {
    setIsRefreshing(true);
    try {
      const ov = await api.getOverviewMetrics();
      if (ov) {
        setActiveExceptionsCount(ov.active_exceptions);
      }
      setRefreshKey((prev) => prev + 1);
    } catch (e) {
      console.error('Failed to sync state:', e);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchGlobalState();
  }, []);

  const handleOrderCreated = (newOrder) => {
    setSelectedOrderId(newOrder.order_id);
    fetchGlobalState();
    setTab('orders');
  };

  const renderActivePage = () => {
    switch (currentTab) {
      case 'dashboard':
        return <DashboardPage key={refreshKey} setTab={setTab} setSelectedOrder={setSelectedOrderId} />;
      case 'orders':
        return (
          <OrdersPage
            key={refreshKey}
            setTab={setTab}
            setSelectedOrderId={setSelectedOrderId}
            onNewOrder={() => setOrderModalOpen(true)}
          />
        );
      case 'optimization':
        return (
          <OptimizationPage
            key={`${refreshKey}-${selectedOrderId}`}
            selectedOrderId={selectedOrderId}
            setSelectedOrderId={setSelectedOrderId}
          />
        );
      case 'inventory':
        return <InventoryPage key={refreshKey} />;
      case 'warehouses':
        return <WarehousesPage key={refreshKey} />;
      case 'shipments':
        return <ShipmentsPage key={refreshKey} />;
      case 'exceptions':
        return <ExceptionsPage key={refreshKey} />;
      case 'analytics':
        return <AnalyticsPage key={refreshKey} />;
      default:
        return <DashboardPage key={refreshKey} setTab={setTab} setSelectedOrder={setSelectedOrderId} />;
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-sky-500 selection:text-slate-950">
      {/* Navigation Sidebar */}
      <Sidebar
        currentTab={currentTab}
        setTab={setTab}
        activeExceptionsCount={activeExceptionsCount}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar
          onRefresh={fetchGlobalState}
          onNewOrder={() => setOrderModalOpen(true)}
          isRefreshing={isRefreshing}
        />

        <main className="flex-1 p-8 overflow-y-auto max-w-7xl w-full mx-auto">
          {renderActivePage()}
        </main>
      </div>

      {/* New Order Modal */}
      <OrderModal
        isOpen={isOrderModalOpen}
        onClose={() => setOrderModalOpen(false)}
        onSuccess={handleOrderCreated}
      />
    </div>
  );
}

const API_BASE = '/api';

export async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const res = await fetch(url, config);
    if (!res.ok) {
      let errDetail = 'Request failed';
      try {
        const errJson = await res.json();
        errDetail = errJson.detail || JSON.stringify(errJson);
      } catch (e) {
        errDetail = res.statusText;
      }
      throw new Error(errDetail);
    }
    return await res.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

export const api = {
  // Orders
  getOrders: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/orders?${q}`);
  },
  getOrder: (id) => request(`/orders/${id}`),
  getOrderStatus: (id) => request(`/orders/${id}/status`),
  createOrder: (data) => request('/orders', { method: 'POST', body: JSON.stringify(data) }),

  // Optimization
  optimizeOrder: (id, weights) => request(`/fulfillment/optimize/${id}`, {
    method: 'POST',
    body: weights ? JSON.stringify(weights) : undefined,
  }),
  getDecision: (id) => request(`/fulfillment/decision/${id}`),
  getOptions: (id) => request(`/fulfillment/options/${id}`),
  compareBaseline: (id) => request(`/fulfillment/compare-baseline/${id}`),

  // Inventory
  getInventory: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/inventory?${q}`);
  },
  getInventoryBySku: (skuId) => request(`/inventory/${skuId}`),

  // Nodes & Capacities
  getNodes: () => request('/nodes'),
  getNodeCapacity: (nodeId) => request(`/nodes/${nodeId}/capacity`),

  // Shipments & Tracking
  getShipments: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/shipments?${q}`);
  },
  getShipment: (id) => request(`/shipments/${id}`),
  getShipmentTracking: (id) => request(`/shipments/${id}/tracking`),
  addTrackingEvent: (id, data) => request(`/shipments/${id}/events`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  // Exceptions
  getExceptions: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/exceptions?${q}`);
  },
  resolveException: (id, data) => request(`/exceptions/${id}/resolve`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  }),

  // Analytics
  getOverviewMetrics: () => request('/analytics/overview'),
  getCarrierAnalytics: () => request('/analytics/carriers'),
  getFulfillmentAnalytics: () => request('/analytics/fulfillment'),
  getDeliveryPerformance: () => request('/analytics/delivery-performance'),
};

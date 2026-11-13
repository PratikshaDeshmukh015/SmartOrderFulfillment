# REST API DOCUMENTATION
## Smart Order Fulfillment and Delivery Promise Optimization System

Base URL: `http://localhost:8000/api`
Interactive Swagger UI: `http://localhost:8000/docs`

---

### 1. Order Endpoints

#### `POST /api/orders`
Create a new customer order and register demand in the fulfillment network.
- **Request Body:**
```json
{
  "customer_id": "CUST-1045",
  "customer_name": "Jane Miller",
  "customer_email": "jane@example.com",
  "destination_address": "789 Broadway Ave",
  "destination_city": "New York",
  "destination_state": "NY",
  "destination_zip": "10003",
  "destination_zone": "Zone 1",
  "order_priority": "STANDARD",
  "lines": [
    {
      "sku_id": "SKU-2026-00001",
      "quantity": 2
    }
  ]
}
```
- **Response (201 Created):** Order object with assigned `order_id` e.g. `ORD-2026-001001`.

#### `GET /api/orders`
List orders with optional query filtering.
- **Query Params:** `status`, `priority`, `search`, `limit` (default 50), `offset` (default 0).

#### `GET /api/orders/{order_id}`
Retrieve order header and nested line items.

#### `GET /api/orders/{order_id}/status`
Get order fulfillment progress and associated shipments rollup.

---

### 2. Fulfillment Optimization Endpoints

#### `POST /api/fulfillment/optimize/{order_id}`
Execute the 12-step multi-factor weighted optimization algorithm for the specified order.
- **Optional Request Body (Custom Weights):**
```json
{
  "inventory": 0.35,
  "speed": 0.25,
  "capacity": 0.15,
  "cost": 0.15,
  "reliability": 0.05,
  "risk": 0.05
}
```
- **Response (200 OK):**
```json
{
  "decision_id": "DEC-OPT-000001-123456",
  "order_id": "ORD-2026-000001",
  "strategy": "OPTIMIZED_WEIGHTED",
  "is_split": false,
  "selected_node_id": "FUL-2026-000003",
  "selected_node_name": "Atlanta Regional Hub #03",
  "selected_carrier": "Apex Logistics",
  "selected_service": "2-Day Express",
  "shipping_cost": 15.50,
  "weighted_score": 92.4,
  "decision_reason": "Selected node FUL-2026-000003 based on top composite multi-factor score...",
  "execution_time_ms": 14.8
}
```

#### `GET /api/fulfillment/decision/{order_id}`
Retrieve the historical decision record and explainability parameters.

#### `GET /api/fulfillment/options/{order_id}`
Retrieve all candidate warehouse options ranked by composite score.

#### `GET /api/fulfillment/compare-baseline/{order_id}`
Head-to-head comparison between the Multi-Factor Weighted Optimizer and the Nearest-Warehouse Baseline strategy.

---

### 3. Inventory & Warehouse Endpoints

#### `GET /api/inventory`
Query network inventory across all facilities. Filters: `sku_id`, `node_id`, `low_stock_only`.

#### `GET /api/inventory/{sku_id}`
Get SKU stock distribution across all 20 fulfillment nodes.

#### `GET /api/nodes`
List all 20 fulfillment centers, operating cutoffs, and daily throughput limits.

#### `GET /api/nodes/{node_id}/capacity`
Retrieve daily capacity utilization and headroom history for a facility.

---

### 4. Shipment Tracking Endpoints

#### `GET /api/shipments`
List shipments. Filters: `order_id`, `node_id`, `status`.

#### `GET /api/shipments/{shipment_id}`
Get shipment details, packed line items, and tracking timeline.

#### `POST /api/shipments/{shipment_id}/events`
Record a new tracking milestone. Validates lifecycle state transition rules.

---

### 5. Exception Management Endpoints

#### `GET /api/exceptions`
List fulfillment exceptions. Filters: `severity`, `issue_type`, `resolution_status`.

#### `PATCH /api/exceptions/{exception_id}/resolve`
Resolve an open exception with audit notes and operator identity.

# DATA DICTIONARY
## Smart Order Fulfillment and Delivery Promise Optimization System

This document provides a comprehensive data dictionary for all 18 normalized entities in the fulfillment system.

---

### 1. Order (`orders`)
Represents a customer purchase order demanding fulfillment across network nodes.

| Column | Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `order_id` | VARCHAR(50) | NO | PK, Index | Deterministic Order ID format `ORD-2026-XXXXXX` |
| `customer_id` | VARCHAR(50) | NO | Index | Unique customer reference identifier |
| `customer_name` | VARCHAR(100) | NO | - | Full name of recipient |
| `customer_email` | VARCHAR(150) | NO | - | Recipient contact email address |
| `destination_address` | VARCHAR(255) | NO | - | Street shipping address |
| `destination_city` | VARCHAR(100) | NO | - | Destination city |
| `destination_state` | VARCHAR(50) | NO | - | Destination state abbreviation |
| `destination_zip` | VARCHAR(20) | NO | - | Destination postal ZIP code |
| `destination_zone` | VARCHAR(20) | NO | Index | Shipping Zone designation (`Zone 1` through `Zone 8`) |
| `order_priority` | ENUM | NO | - | Order priority: `STANDARD`, `EXPRESS`, `URGENT` |
| `order_status` | ENUM | NO | Index | Lifecycle status (`CREATED`, `ALLOCATED`, `PROCESSING`, `SHIPPED`, `PARTIALLY_DELIVERED`, `DELIVERED`, `EXCEPTION`, `CANCELLED`) |
| `total_amount` | FLOAT | NO | - | Total dollar amount for goods purchased |
| `shipping_fee` | FLOAT | NO | - | Shipping surcharge paid by customer |
| `placed_at` | DATETIME | NO | Index | Timestamp when order was placed |
| `promised_delivery_date` | DATETIME | YES | - | Current promised delivery timestamp |
| `actual_delivery_date` | DATETIME | YES | - | Timestamp when all packages were delivered |
| `is_split` | BOOLEAN | NO | - | Flag indicating split multi-warehouse fulfillment |
| `created_at` | DATETIME | NO | - | Record creation timestamp |
| `updated_at` | DATETIME | NO | - | Last modification timestamp |

---

### 2. OrderLine (`order_lines`)
Individual SKU item demanded within an order.

| Column | Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `order_line_id` | VARCHAR(60) | NO | PK, Index | Unique line ID `ORD-2026-XXXXXX-YY` |
| `order_id` | VARCHAR(50) | NO | FK (`orders.order_id`), Index | Parent order reference |
| `sku_id` | VARCHAR(50) | NO | FK (`skus.sku_id`), Index | Product SKU reference |
| `quantity` | INTEGER | NO | - | Demanded unit quantity |
| `unit_price` | FLOAT | NO | - | Price per unit at purchase |
| `line_total` | FLOAT | NO | - | `quantity * unit_price` |
| `allocated_quantity` | INTEGER | NO | - | Units committed by fulfillment nodes |
| `created_at` | DATETIME | NO | - | Creation timestamp |
| `updated_at` | DATETIME | NO | - | Update timestamp |

---

### 3. SKU (`skus`)
Product catalog master record defining physical dimensions and handling constraints.

| Column | Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `sku_id` | VARCHAR(50) | NO | PK, Index | Deterministic SKU ID `SKU-2026-XXXXX` |
| `sku_name` | VARCHAR(150) | NO | - | Display product title |
| `category` | VARCHAR(100) | NO | Index | Merchandising category |
| `weight_kg` | FLOAT | NO | - | Unit package weight in kilograms |
| `volume_m3` | FLOAT | NO | - | Unit volume in cubic meters |
| `unit_price` | FLOAT | NO | - | Base retail price |
| `handling_type` | ENUM | NO | - | `STANDARD`, `FRAGILE`, `COLD_CHAIN`, `HAZMAT` |
| `is_active` | BOOLEAN | NO | - | Active sellable status |

---

### 4. FulfillmentNode (`fulfillment_nodes`)
Physical distribution center, regional hub, or warehouse facility.

| Column | Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `node_id` | VARCHAR(50) | NO | PK, Index | Deterministic Node ID `FUL-2026-XXXXXX` |
| `node_name` | VARCHAR(150) | NO | - | Facility name |
| `node_type` | ENUM | NO | - | `WAREHOUSE`, `FULFILLMENT_CENTER`, `REGIONAL_HUB` |
| `address` | VARCHAR(255) | NO | - | Street address |
| `city` | VARCHAR(100) | NO | - | City location |
| `state` | VARCHAR(50) | NO | - | State |
| `zip_code` | VARCHAR(20) | NO | - | ZIP postal code |
| `latitude` | FLOAT | NO | - | Geographic latitude coordinate |
| `longitude` | FLOAT | NO | - | Geographic longitude coordinate |
| `daily_order_capacity` | INTEGER | NO | - | Maximum processing capacity in orders/day |
| `daily_unit_capacity` | INTEGER | NO | - | Maximum unit pick/pack capacity per day |
| `processing_cutoff_time` | VARCHAR(10) | NO | - | Daily same-day cutoff time (`14:00` or `15:00`) |
| `operating_hours_start` | VARCHAR(10) | NO | - | Facility open time |
| `operating_hours_end` | VARCHAR(10) | NO | - | Facility close time |
| `weekend_operations` | BOOLEAN | NO | - | True if facility processes orders on weekends |
| `is_active` | BOOLEAN | NO | - | Operating status |

---

### 5. Inventory (`inventories`)
Per-node stock levels for each SKU.

| Column | Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `inventory_id` | VARCHAR(50) | NO | PK, Index | ID format `INV-2026-XXXXXX` |
| `node_id` | VARCHAR(50) | NO | FK (`fulfillment_nodes.node_id`), Unique (`node_id`, `sku_id`) | Fulfillment node |
| `sku_id` | VARCHAR(50) | NO | FK (`skus.sku_id`) | SKU reference |
| `available_quantity` | INTEGER | NO | - | Uncommitted units available to promise |
| `reserved_quantity` | INTEGER | NO | - | Committed units held for allocated orders |
| `reorder_threshold` | INTEGER | NO | - | Low stock replenishment alert threshold |
| `safety_stock` | INTEGER | NO | - | Buffer stock reserved for surge demand |
| `last_restocked_at` | DATETIME | NO | - | Restock timestamp |

---

### 6. WarehouseCapacity (`warehouse_capacities`)
Daily utilized vs maximum order and unit throughput.

| Column | Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `capacity_id` | VARCHAR(50) | NO | PK, Index | ID format `CAP-2026-XXXXXX` |
| `node_id` | VARCHAR(50) | NO | FK, Unique (`node_id`, `date`) | Warehouse facility reference |
| `date` | DATE | NO | Index | Operational calendar date |
| `max_orders` | INTEGER | NO | - | Maximum order limit for date |
| `utilized_orders` | INTEGER | NO | - | Allocated order count for date |
| `max_units` | INTEGER | NO | - | Maximum unit capacity for date |
| `utilized_units` | INTEGER | NO | - | Picked/packed unit count for date |

---

### 7. Carrier (`carriers`)
Logistics freight and parcel shipping partner.

| Column | Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `carrier_id` | VARCHAR(50) | NO | PK, Index | Deterministic Carrier ID `CAR-2026-XXX` |
| `carrier_name` | VARCHAR(100) | NO | - | Carrier corporate title |
| `contact_email` | VARCHAR(150) | NO | - | Dispatch contact email |
| `phone` | VARCHAR(50) | NO | - | Dispatch phone number |
| `reliability_score` | FLOAT | NO | - | Historical delivery compliance score `0.0 - 1.0` |
| `is_active` | BOOLEAN | NO | - | Operational carrier status |

---

### 8. ServiceLevel (`service_levels`)
Carrier delivery tier (Air, Express, Ground, Economy).

| Column | Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `service_id` | VARCHAR(50) | NO | PK, Index | Deterministic Service ID `SRV-2026-XXX` |
| `carrier_id` | VARCHAR(50) | NO | FK (`carriers.carrier_id`) | Associated carrier |
| `service_name` | VARCHAR(100) | NO | - | Service name |
| `service_code` | VARCHAR(50) | NO | Index | Unique service code |
| `base_rate` | FLOAT | NO | - | Base package rate |
| `rate_per_kg` | FLOAT | NO | - | Weight rate per kilogram |
| `rate_per_zone` | FLOAT | NO | - | Distance surcharge per destination zone |
| `guaranteed_delivery` | BOOLEAN | NO | - | Guaranteed SLA flag |

---

### 9. CarrierServiceZone (`carrier_service_zones`)
Transit duration and routing support matrix between origin nodes and destination zones.

| Column | Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `zone_id` | VARCHAR(50) | NO | PK, Index | Format `CSZ-2026-XXXXX` |
| `service_id` | VARCHAR(50) | NO | FK, Unique (`service_id`, `origin_node_id`, `destination_zone`) | Service level |
| `origin_node_id` | VARCHAR(50) | NO | FK (`fulfillment_nodes.node_id`) | Origin dispatch node |
| `destination_zone` | VARCHAR(20) | NO | Index | Destination `Zone 1` to `Zone 8` |
| `transit_days` | INTEGER | NO | - | Expected transit duration in business days |
| `is_supported` | BOOLEAN | NO | - | Carrier operational coverage flag |
| `pickup_time` | VARCHAR(10) | NO | - | Daily carrier cutoff/pickup time (`17:00`) |

---

### 10. CarrierCalendar (`carrier_calendars`)
Carrier operational operating schedule and holiday shutdowns.

| Column | Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `calendar_id` | VARCHAR(50) | NO | PK, Index | Format `CCAL-2026-XXXXX` |
| `carrier_id` | VARCHAR(50) | NO | FK, Unique (`carrier_id`, `date`) | Carrier reference |
| `date` | DATE | NO | Index | Calendar date |
| `is_operating` | BOOLEAN | NO | - | True if carrier conducts pickups/deliveries |
| `holiday_name` | VARCHAR(100) | YES | - | National holiday description if closed |

---

### 11. WarehouseCalendar (`warehouse_calendars`)
Warehouse facility operating schedule and state/federal holidays.

| Column | Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `calendar_id` | VARCHAR(50) | NO | PK, Index | Format `WCAL-2026-XXXXX` |
| `node_id` | VARCHAR(50) | NO | FK, Unique (`node_id`, `date`) | Warehouse facility reference |
| `date` | DATE | NO | Index | Calendar date |
| `is_operating` | BOOLEAN | NO | - | True if facility is staffed and operating |
| `holiday_name` | VARCHAR(100) | YES | - | Holiday name if closed |

---

### 12. Shipment (`shipments`)
A physical parcel package dispatched from a specific warehouse to fulfill order lines.

| Column | Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `shipment_id` | VARCHAR(50) | NO | PK, Index | Format `SHP-2026-XXXXXX` |
| `order_id` | VARCHAR(50) | NO | FK (`orders.order_id`), Index | Originating customer order |
| `node_id` | VARCHAR(50) | NO | FK (`fulfillment_nodes.node_id`) | Dispatch warehouse |
| `carrier_id` | VARCHAR(50) | NO | FK (`carriers.carrier_id`) | Logistics carrier |
| `service_id` | VARCHAR(50) | NO | FK (`service_levels.service_id`) | Service level |
| `shipment_status` | ENUM | NO | Index | Current shipment state |
| `tracking_number` | VARCHAR(100) | NO | Unique, Index | External barcode tracking number |
| `shipping_cost` | FLOAT | NO | - | Incurred shipping cost |
| `total_weight_kg` | FLOAT | NO | - | Package weight |
| `scheduled_dispatch_date`| DATETIME | NO | - | Planned dispatch timestamp |
| `actual_dispatch_date` | DATETIME | YES | - | Actual carrier handover timestamp |
| `promised_delivery_date` | DATETIME | NO | - | Promised delivery date |
| `actual_delivery_date` | DATETIME | YES | - | Actual customer delivery timestamp |
| `is_split` | BOOLEAN | NO | - | Split parcel indicator |

---

### 13. ShipmentLine (`shipment_lines`)
SKU quantity packed into an individual shipment.

| Column | Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `shipment_line_id` | VARCHAR(60) | NO | PK, Index | Format `SHPL-2026-XXXXXX-YY` |
| `shipment_id` | VARCHAR(50) | NO | FK (`shipments.shipment_id`) | Parent shipment |
| `order_line_id` | VARCHAR(60) | NO | FK (`order_lines.order_line_id`) | Order line fulfilled |
| `sku_id` | VARCHAR(50) | NO | FK (`skus.sku_id`) | Product SKU |
| `quantity` | INTEGER | NO | - | Packed quantity |

---

### 14. TrackingEvent (`tracking_events`)
Immutable audit log of package milestone state transitions.

| Column | Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `event_id` | VARCHAR(60) | NO | PK, Index | Format `TRK-SHP-XXXXXX-YYY` |
| `shipment_id` | VARCHAR(50) | NO | FK (`shipments.shipment_id`), Index | Shipment reference |
| `event_status` | ENUM | NO | Index | Milestone status |
| `location` | VARCHAR(150) | NO | - | Physical facility / city scan location |
| `description` | TEXT | NO | - | Human-readable progress description |
| `event_timestamp` | DATETIME | NO | Index | Exact scan timestamp |
| `is_delayed` | BOOLEAN | NO | - | Delay flag |
| `delay_reason` | VARCHAR(255) | YES | - | Reason for delivery postponement |

---

### 15. DeliveryPromise (`delivery_promises`)
Audit trail of calculated delivery promises and subsequent revisions.

| Column | Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `promise_id` | VARCHAR(60) | NO | PK, Index | Format `PROM-ORD-XXXXXX-YY` |
| `order_id` | VARCHAR(50) | NO | FK (`orders.order_id`), Index | Order reference |
| `shipment_id` | VARCHAR(50) | YES | FK (`shipments.shipment_id`) | Specific shipment promise |
| `original_promised_date`| DATETIME | NO | - | Baseline promised delivery date |
| `revised_promised_date` | DATETIME | YES | - | Revised delivery date if altered |
| `promise_version` | INTEGER | NO | - | Revision increment `1, 2, ...` |
| `is_active` | BOOLEAN | NO | - | Current binding promise flag |
| `confidence_score` | FLOAT | NO | - | Machine confidence `0.0 - 1.0` |
| `calculation_factors` | TEXT | YES | - | JSON factors (cutoffs, transit, holidays) |
| `reason` | TEXT | NO | - | Natural language calculation explanation |

---

### 16. Allocation (`allocations`)
Inventory reservation binding between an order line item and a fulfillment center.

| Column | Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `allocation_id` | VARCHAR(60) | NO | PK, Index | Format `ALC-2026-XXXXXX-YY` |
| `order_id` | VARCHAR(50) | NO | FK (`orders.order_id`), Index | Order reference |
| `order_line_id` | VARCHAR(60) | NO | FK (`order_lines.order_line_id`) | Line item reference |
| `node_id` | VARCHAR(50) | NO | FK (`fulfillment_nodes.node_id`) | Fulfilling node |
| `sku_id` | VARCHAR(50) | NO | FK (`skus.sku_id`) | SKU reference |
| `allocated_quantity` | INTEGER | NO | - | Reserved quantity |
| `allocation_status` | ENUM | NO | - | `RESERVED`, `FULFILLED`, `RELEASED`, `FAILED` |

---

### 17. FulfillmentException (`fulfillment_exceptions`)
Structured log of supply chain operational anomalies and resolution actions.

| Column | Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `exception_id` | VARCHAR(50) | NO | PK, Index | Format `EXC-2026-XXXXXX` |
| `order_id` | VARCHAR(50) | YES | FK (`orders.order_id`), Index | Affected order |
| `shipment_id` | VARCHAR(50) | YES | FK (`shipments.shipment_id`) | Affected shipment |
| `issue_type` | VARCHAR(100) | NO | Index | Issue classification |
| `severity` | ENUM | NO | Index | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `description` | TEXT | NO | - | Problem explanation |
| `detection_timestamp` | DATETIME | NO | - | Automated detection timestamp |
| `expected_behavior` | TEXT | NO | - | Expected business outcome |
| `resolution_status` | ENUM | NO | Index | `OPEN`, `INVESTIGATING`, `RESOLVED`, `IGNORED` |
| `resolution_notes` | TEXT | YES | - | Operator notes upon resolution |
| `resolved_at` | DATETIME | YES | - | Timestamp when resolved |
| `resolved_by` | VARCHAR(100) | YES | - | Operator identifier |
| `ground_truth_label` | VARCHAR(100) | YES | - | Benchmarking validation label |

---

### 18. OptimizationDecision (`optimization_decisions`)
Immutable historical log of optimizer executions and explainability scores.

| Column | Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `decision_id` | VARCHAR(50) | NO | PK, Index | Format `DEC-2026-XXXXXX` |
| `order_id` | VARCHAR(50) | NO | FK (`orders.order_id`), Index | Order optimized |
| `strategy` | ENUM | NO | - | `OPTIMIZED_WEIGHTED`, `BASELINE_NEAREST`, `SPLIT_FULFILLMENT`, `EXCEPTION_NO_NODE` |
| `selected_nodes` | TEXT | NO | - | JSON array of node IDs selected |
| `candidate_scores` | TEXT | NO | - | JSON score breakdown of top candidates |
| `weights_used` | TEXT | NO | - | JSON weights applied in scoring formula |
| `total_cost` | FLOAT | NO | - | Projected shipping cost |
| `estimated_delivery_days`| FLOAT | NO | - | Transit duration in days |
| `decision_reason` | TEXT | NO | - | Natural language explanation |
| `execution_time_ms` | FLOAT | NO | - | Optimization algorithm runtime in milliseconds |
| `is_split` | BOOLEAN | NO | - | Split fulfillment indicator |

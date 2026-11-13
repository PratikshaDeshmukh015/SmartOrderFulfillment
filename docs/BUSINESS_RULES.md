# BUSINESS RULES & OPTIMIZATION LOGIC
## Smart Order Fulfillment and Delivery Promise Optimization System

### 1. Weighted Multi-Factor Fulfillment Scoring
The decision engine ranks eligible fulfillment centers using a configurable multi-criteria formula:

$$\text{Composite Score} = \sum_{i} w_i \cdot S_i$$

Default Factor Weights (configurable in `.env` and live in the dashboard):
- **Inventory Availability ($w_{\text{inv}} = 0.30$):** $S_{\text{inv}} = \min(100, \frac{\text{Available Stock}}{\text{Required Stock}} \times 100)$
- **Delivery Speed ($w_{\text{spd}} = 0.25$):** 1 day = 100, 2 days = 85, 3 days = 70, 4 days = 50, 5+ days = 30
- **Warehouse Capacity Headroom ($w_{\text{cap}} = 0.15$):** $S_{\text{cap}} = \max(10, 100 - \text{Utilization \%})$
- **Shipping Cost ($w_{\text{cost}} = 0.15$):** Inverse cost scaling: $S_{\text{cost}} = \max(10, 100 - \frac{\text{Cost}}{45} \times 80)$
- **Carrier Reliability ($w_{\text{rel}} = 0.10$):** $S_{\text{rel}} = \text{Reliability Score} \times 100$
- **Operational Risk ($w_{\text{risk}} = 0.05$):** Weather/holiday buffer score (90 for standard operating days, 55 if near cutoff or weekend)

---

### 2. Delivery Promise Engine Rules
1. **Warehouse Cutoff Compliance:**
   - Orders received before warehouse cutoff (`14:00` or `15:00`) process same-day if capacity allows.
   - Orders placed after cutoff automatically roll to the next operating business day.
2. **Holiday & Weekend Rules:**
   - If the fulfillment node does not operate on weekends (`weekend_operations = False`), orders received Friday after cutoff advance to Monday.
   - Warehouse and Carrier calendar holidays are automatically skipped during dispatch and transit calculations.
3. **Carrier Pickup Cutoff:**
   - Shipments must be staged before carrier daily pickup time (`17:00`).
4. **Delivery Date Calculation:**
   $$\text{Promised Delivery Date} = \text{Scheduled Dispatch Date} + \sum \text{Eligible Transit Days}$$
5. **Promise Immutability & Revisions:**
   - The initial promise is preserved as Version 1. Any subsequent delay creates Version 2+ with an explicit reason code.

---

### 3. Split Fulfillment & Status Rollup Rules
1. **Split Allocation Trigger:**
   - If no single warehouse possesses 100% of the demanded SKU quantities, the system invokes a set-covering optimization algorithm to find the minimal warehouse combination.
2. **Order-Level Status Rollup:**
   - For split orders with $N$ shipments:
     - Marked `DELIVERED` **only** if all $N$ shipments have reached `DELIVERED` status.
     - Marked `PARTIALLY_DELIVERED` if at least 1 shipment is `DELIVERED` and others are still `IN_TRANSIT`.
     - Marked `SHIPPED` if all shipments are dispatched.

---

### 4. Exception Detection & Handling (The 10 Negative Scenarios)
1. `PROMISE_BEFORE_ORDER_CREATION`: Promise timestamp earlier than order placement.
2. `ALLOCATION_EXCEEDS_INVENTORY`: Allocation quantity exceeds available node stock.
3. `UNSUPPORTED_SHIPPING_ZONE`: Selected carrier service does not cover the destination zone.
4. `DELIVERED_BEFORE_DISPATCH`: Shipment tracking indicates delivered prior to dispatch scan.
5. `INCORRECT_SPLIT_STATUS_ROLLUP`: Order marked `DELIVERED` prematurely while split shipments are in transit.
6. `WAREHOUSE_CAPACITY_EXCEEDED`: Daily processing limit exceeded.
7. `CARRIER_CUTOFF_MISSED`: Order processed after pickup window but marked dispatched same day.
8. `INVENTORY_SHORTAGE`: Total network inventory cannot fulfill order quantity.
9. `NO_ELIGIBLE_FULFILLMENT_NODE`: All candidate fulfillment nodes fail operating or calendar constraints.
10. `INVALID_TRACKING_SEQUENCE`: Milestone scan skips required lifecycle states (e.g. `CREATED` to `DELIVERED`).

import argparse
import csv
import json
import os
import random
from datetime import datetime, date, timedelta, timezone

SEED = 20261022

# Master geographical & reference lists
CITIES_BY_ZONE = {
    "Zone 1": [("New York", "NY", "10001", 40.7128, -74.0060), ("Jersey City", "NJ", "07302", 40.7178, -74.0431)],
    "Zone 2": [("Philadelphia", "PA", "19104", 39.9526, -75.1652), ("Boston", "MA", "02108", 42.3601, -71.0589)],
    "Zone 3": [("Atlanta", "GA", "30303", 33.7490, -84.3880), ("Charlotte", "NC", "28202", 35.2271, -80.8431)],
    "Zone 4": [("Chicago", "IL", "60601", 41.8781, -87.6298), ("Columbus", "OH", "43215", 39.9612, -82.9988)],
    "Zone 5": [("Dallas", "TX", "75201", 32.7767, -96.7970), ("Houston", "TX", "77002", 29.7604, -95.3698)],
    "Zone 6": [("Denver", "CO", "80202", 39.7392, -104.9903), ("Phoenix", "AZ", "85001", 33.4484, -112.0740)],
    "Zone 7": [("Los Angeles", "CA", "90012", 34.0522, -118.2437), ("San Francisco", "CA", "94102", 37.7749, -122.4194)],
    "Zone 8": [("Seattle", "WA", "98101", 47.6062, -122.3321), ("Portland", "OR", "97201", 45.5152, -122.6784)]
}

PRODUCT_CATEGORIES = [
    ("Electronics", 2.5, 0.015, 120.0, "FRAGILE"),
    ("Apparel", 0.5, 0.005, 45.0, "STANDARD"),
    ("Home & Kitchen", 3.0, 0.025, 75.0, "STANDARD"),
    ("Health & Personal Care", 0.8, 0.004, 30.0, "COLD_CHAIN"),
    ("Sports & Outdoors", 4.0, 0.040, 85.0, "STANDARD"),
    ("Books & Stationery", 0.7, 0.003, 20.0, "STANDARD"),
    ("Beauty & Cosmetics", 0.4, 0.002, 35.0, "STANDARD"),
    ("Automotive Tools", 6.5, 0.050, 150.0, "HAZMAT")
]

CARRIER_NAMES = [
    ("Apex Logistics", 0.98),
    ("SwiftAir Express", 0.96),
    ("Continental Freight", 0.94),
    ("MetroDirect Carriers", 0.92),
    ("Pioneer Parcel", 0.95),
    ("Titan Shipping", 0.91),
    ("Vanguard Courier", 0.97),
    ("BlueStreak Delivery", 0.89),
    ("OmniPostal Services", 0.93),
    ("Horizon Logistics", 0.90)
]

HOLIDAYS_2026 = {
    date(2026, 1, 1): "New Year's Day",
    date(2026, 5, 25): "Memorial Day",
    date(2026, 7, 4): "Independence Day",
    date(2026, 9, 7): "Labor Day",
    date(2026, 11, 26): "Thanksgiving Day",
    date(2026, 12, 25): "Christmas Day"
}

def format_dt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def generate_all(mode="starter", output_dir="data/generated", ground_truth_dir="data/ground_truth"):
    random.seed(SEED)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(ground_truth_dir, exist_ok=True)

    if mode == "full":
        num_orders = 50000
        num_nodes = 20
        num_skus = 500
        num_carriers = 10
        target_tracking_events = 100000
    else:
        num_orders = 1000
        num_nodes = 20
        num_skus = 100
        num_carriers = 10
        target_tracking_events = 2000

    print(f"Generating synthetic dataset in [{mode}] mode with seed={SEED}...")

    # 1. Generate SKUs
    skus = []
    for i in range(1, num_skus + 1):
        sku_id = f"SKU-2026-{i:05d}"
        cat_info = random.choice(PRODUCT_CATEGORIES)
        cat_name, base_wt, base_vol, base_price, handling = cat_info
        wt = round(base_wt * random.uniform(0.6, 1.8), 2)
        vol = round(base_vol * random.uniform(0.7, 1.5), 4)
        price = round(base_price * random.uniform(0.5, 2.5), 2)
        skus.append({
            "sku_id": sku_id,
            "sku_name": f"{cat_name} Item #{i:04d}",
            "category": cat_name,
            "weight_kg": wt,
            "volume_m3": vol,
            "unit_price": price,
            "handling_type": handling,
            "is_active": True,
            "created_at": "2026-01-01 00:00:00",
            "updated_at": "2026-01-01 00:00:00"
        })

    # 2. Generate Fulfillment Nodes (20 nodes across US zones)
    nodes = []
    all_zones = list(CITIES_BY_ZONE.keys())
    for i in range(1, num_nodes + 1):
        node_id = f"FUL-2026-{i:06d}"
        assigned_zone = all_zones[(i - 1) % len(all_zones)]
        city_info = CITIES_BY_ZONE[assigned_zone][(i // len(all_zones)) % len(CITIES_BY_ZONE[assigned_zone])]
        city, state, zip_code, lat, lon = city_info
        
        node_type = "FULFILLMENT_CENTER" if i <= 14 else ("REGIONAL_HUB" if i <= 18 else "WAREHOUSE")
        daily_order_cap = 1500 if node_type == "REGIONAL_HUB" else (1000 if node_type == "FULFILLMENT_CENTER" else 600)
        daily_unit_cap = daily_order_cap * 5
        cutoff = "15:00" if i % 2 == 0 else "14:00"

        nodes.append({
            "node_id": node_id,
            "node_name": f"{city} {node_type.replace('_', ' ').title()} #{i:02d}",
            "node_type": node_type,
            "address": f"{100 * i} Logistics Parkway",
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "latitude": round(lat + random.uniform(-0.05, 0.05), 4),
            "longitude": round(lon + random.uniform(-0.05, 0.05), 4),
            "daily_order_capacity": daily_order_cap,
            "daily_unit_capacity": daily_unit_cap,
            "processing_cutoff_time": cutoff,
            "operating_hours_start": "07:00",
            "operating_hours_end": "22:00",
            "weekend_operations": (i % 3 != 0),
            "is_active": True,
            "created_at": "2026-01-01 00:00:00",
            "updated_at": "2026-01-01 00:00:00"
        })

    # 3. Generate Carriers & Service Levels
    carriers = []
    service_levels = []
    srv_idx = 1
    for i in range(1, num_carriers + 1):
        car_id = f"CAR-2026-{i:03d}"
        cname, reliability = CARRIER_NAMES[i - 1]
        carriers.append({
            "carrier_id": car_id,
            "carrier_name": cname,
            "contact_email": f"dispatch@{cname.lower().replace(' ', '')}.com",
            "phone": f"+1-800-{5550000 + i}",
            "reliability_score": reliability,
            "is_active": True,
            "created_at": "2026-01-01 00:00:00",
            "updated_at": "2026-01-01 00:00:00"
        })

        # 3 service levels per carrier: Next Day Air, 2-Day Express, Standard Ground
        services_def = [
            ("Next Day Air", "AIR_1D", 25.0, 3.5, 4.0, True),
            ("2-Day Express", "EXP_2D", 15.0, 2.0, 2.5, True),
            ("Standard Ground", "GRD_STD", 8.0, 1.0, 1.2, False)
        ]
        for sname, scode, base_rt, kg_rt, zone_rt, guar in services_def:
            service_levels.append({
                "service_id": f"SRV-2026-{srv_idx:03d}",
                "carrier_id": car_id,
                "service_name": sname,
                "service_code": f"{car_id}_{scode}",
                "base_rate": base_rt,
                "rate_per_kg": kg_rt,
                "rate_per_zone": zone_rt,
                "guaranteed_delivery": guar,
                "created_at": "2026-01-01 00:00:00",
                "updated_at": "2026-01-01 00:00:00"
            })
            srv_idx += 1

    # 4. Carrier Service Zones
    carrier_service_zones = []
    csz_idx = 1
    for srv in service_levels:
        for node in nodes:
            for z_int in range(1, 9):
                dest_zone = f"Zone {z_int}"
                # Transit days depends on service code and zone distance
                is_air = "AIR_1D" in srv["service_code"]
                is_exp = "EXP_2D" in srv["service_code"]
                if is_air:
                    transit = 1
                elif is_exp:
                    transit = 2
                else:
                    # Ground: 1 to 5 days
                    transit = min(5, 1 + (z_int // 2))

                # Inject occasional unsupported zone (e.g. carrier 10 ground does not support Zone 8)
                is_supp = True
                if srv["carrier_id"] == "CAR-2026-010" and dest_zone == "Zone 8" and not is_air:
                    is_supp = False

                carrier_service_zones.append({
                    "zone_id": f"CSZ-2026-{csz_idx:05d}",
                    "service_id": srv["service_id"],
                    "origin_node_id": node["node_id"],
                    "destination_zone": dest_zone,
                    "transit_days": transit,
                    "is_supported": is_supp,
                    "pickup_time": "17:00",
                    "created_at": "2026-01-01 00:00:00",
                    "updated_at": "2026-01-01 00:00:00"
                })
                csz_idx += 1

    # 5. Calendars (Warehouse & Carrier for year 2026)
    start_date = date(2026, 1, 1)
    end_date = date(2026, 12, 31)
    days_count = (end_date - start_date).days + 1

    warehouse_calendars = []
    wcal_idx = 1
    # Sample calendars for key operational dates around November (holiday season)
    # To keep starter size tight, sample 60 days around Nov-Dec 2026
    sample_dates = [start_date + timedelta(days=d) for d in range(300, min(days_count, 365))]

    for node in nodes:
        for dt in sample_dates:
            is_op = True
            hname = HOLIDAYS_2026.get(dt)
            if hname:
                is_op = False
            elif dt.weekday() >= 5 and not node["weekend_operations"]:
                is_op = False
            warehouse_calendars.append({
                "calendar_id": f"WCAL-2026-{wcal_idx:05d}",
                "node_id": node["node_id"],
                "date": dt.isoformat(),
                "is_operating": is_op,
                "holiday_name": hname,
                "created_at": "2026-01-01 00:00:00",
                "updated_at": "2026-01-01 00:00:00"
            })
            wcal_idx += 1

    carrier_calendars = []
    ccal_idx = 1
    for car in carriers:
        for dt in sample_dates:
            is_op = True
            hname = HOLIDAYS_2026.get(dt)
            if hname or dt.weekday() == 6: # Sunday no carrier pickup
                is_op = False
            carrier_calendars.append({
                "calendar_id": f"CCAL-2026-{ccal_idx:05d}",
                "carrier_id": car["carrier_id"],
                "date": dt.isoformat(),
                "is_operating": is_op,
                "holiday_name": hname,
                "created_at": "2026-01-01 00:00:00",
                "updated_at": "2026-01-01 00:00:00"
            })
            ccal_idx += 1

    # 6. Warehouse Capacities
    warehouse_capacities = []
    cap_idx = 1
    for node in nodes:
        for dt in sample_dates:
            warehouse_capacities.append({
                "capacity_id": f"CAP-2026-{cap_idx:06d}",
                "node_id": node["node_id"],
                "date": dt.isoformat(),
                "max_orders": node["daily_order_capacity"],
                "utilized_orders": random.randint(int(node["daily_order_capacity"] * 0.3), int(node["daily_order_capacity"] * 0.7)),
                "max_units": node["daily_unit_capacity"],
                "utilized_units": random.randint(int(node["daily_unit_capacity"] * 0.3), int(node["daily_unit_capacity"] * 0.7)),
                "created_at": "2026-01-01 00:00:00",
                "updated_at": "2026-01-01 00:00:00"
            })
            cap_idx += 1

    # 7. Inventory (Every node holds a distribution of SKUs)
    inventories = []
    inv_map = {} # (node_id, sku_id) -> avail
    inv_idx = 1
    for node in nodes:
        for sku in skus:
            # 85% probability node carries this SKU
            if random.random() < 0.85:
                avail = random.randint(15, 250)
                reserved = random.randint(0, min(10, avail // 2))
                inventories.append({
                    "inventory_id": f"INV-2026-{inv_idx:06d}",
                    "node_id": node["node_id"],
                    "sku_id": sku["sku_id"],
                    "available_quantity": avail,
                    "reserved_quantity": reserved,
                    "reorder_threshold": 25,
                    "safety_stock": 10,
                    "last_restocked_at": "2026-11-01 08:00:00",
                    "created_at": "2026-11-01 08:00:00",
                    "updated_at": "2026-11-01 08:00:00"
                })
                inv_map[(node["node_id"], sku["sku_id"])] = avail
                inv_idx += 1
            else:
                inv_map[(node["node_id"], sku["sku_id"])] = 0

    # 8. Orders, OrderLines, Allocations, Shipments, Promises, Tracking Events, Exceptions, Ground Truth
    orders = []
    order_lines = []
    allocations = []
    shipments = []
    shipment_lines = []
    tracking_events = []
    delivery_promises = []
    fulfillment_exceptions = []
    optimization_decisions = []
    ground_truth_records = []

    order_line_idx = 1
    alc_idx = 1
    shp_idx = 1
    shpl_idx = 1
    trk_idx = 1
    prom_idx = 1
    exc_idx = 1
    dec_idx = 1

    # Base reference date for order simulation: Nov 10, 2026 to Nov 25, 2026
    sim_base_dt = datetime(2026, 11, 10, 8, 30, 0, tzinfo=timezone.utc)

    # Injected anomaly counters and targets
    # We will inject known anomalies into specific order indexes:
    # 1. Promise before order: order 15
    # 2. Allocation exceeds inventory: order 30
    # 3. Carrier service unsupported: order 45
    # 4. Delivered before dispatch: order 60
    # 5. Incorrect split status rollup: order 75
    # 6. Warehouse capacity exceeded: order 90
    # 7. Carrier cutoff missed: order 105
    # 8. Inventory shortage: order 120
    # 9. No eligible node: order 135
    # 10. Invalid tracking sequence: order 150

    ANOMALY_ORDERS = {
        15: "PROMISE_BEFORE_ORDER_CREATION",
        30: "ALLOCATION_EXCEEDS_INVENTORY",
        45: "UNSUPPORTED_SHIPPING_ZONE",
        60: "DELIVERED_BEFORE_DISPATCH",
        75: "INCORRECT_SPLIT_STATUS_ROLLUP",
        90: "WAREHOUSE_CAPACITY_EXCEEDED",
        105: "CARRIER_CUTOFF_MISSED",
        120: "INVENTORY_SHORTAGE",
        135: "NO_ELIGIBLE_FULFILLMENT_NODE",
        150: "INVALID_TRACKING_SEQUENCE"
    }

    for ord_num in range(1, num_orders + 1):
        order_id = f"ORD-2026-{ord_num:06d}"
        cust_id = f"CUST-{1000 + (ord_num % 400):04d}"
        dest_z_num = 1 + (ord_num % 8)
        dest_zone = f"Zone {dest_z_num}"
        city_tuple = random.choice(CITIES_BY_ZONE[dest_zone])
        dest_city, dest_state, dest_zip = city_tuple[0], city_tuple[1], city_tuple[2]
        dest_addr = f"{100 + (ord_num % 899)} Main Street"

        # Timestamp spacing
        placed_dt = sim_base_dt + timedelta(minutes=ord_num * 12 + random.randint(0, 10))
        priority = "URGENT" if ord_num % 20 == 0 else ("EXPRESS" if ord_num % 5 == 0 else "STANDARD")

        # Determine number of lines (1 to 4 lines)
        num_lines = 1 if ord_num % 4 != 0 else (2 if ord_num % 10 != 0 else 3)
        # Choose SKUs for lines
        assigned_skus = random.sample(skus, num_lines)
        lines_data = []
        total_order_amount = 0.0

        for line_pos, s_item in enumerate(assigned_skus, 1):
            line_id = f"{order_id}-{line_pos:02d}"
            # Anomaly 8: Inventory shortage if ord_num == 120
            if ord_num == 120:
                qty = 9999 # impossible quantity across all nodes
            else:
                qty = random.randint(1, 4)
            uprice = s_item["unit_price"]
            ltotal = round(qty * uprice, 2)
            total_order_amount += ltotal
            lines_data.append({
                "order_line_id": line_id,
                "order_id": order_id,
                "sku_id": s_item["sku_id"],
                "quantity": qty,
                "unit_price": uprice,
                "line_total": ltotal,
                "allocated_quantity": 0,
                "created_at": format_dt(placed_dt),
                "updated_at": format_dt(placed_dt)
            })

        # Check anomaly injection
        anomaly_type = ANOMALY_ORDERS.get(ord_num)

        # Force multiple lines and split for split anomaly
        if anomaly_type == "INCORRECT_SPLIT_STATUS_ROLLUP" and len(lines_data) < 2:
            extra_sku = skus[1] if skus[0]["sku_id"] == lines_data[0]["sku_id"] else skus[0]
            line_id = f"{order_id}-02"
            lines_data.append({
                "order_line_id": line_id,
                "order_id": order_id,
                "sku_id": extra_sku["sku_id"],
                "quantity": 2,
                "unit_price": extra_sku["unit_price"],
                "line_total": round(2 * extra_sku["unit_price"], 2),
                "allocated_quantity": 0,
                "created_at": format_dt(placed_dt),
                "updated_at": format_dt(placed_dt)
            })

        # Optimization & Fulfillment logic
        # Default strategy: Single or Split fulfillment
        # Evaluate nodes that have inventory
        eligible_single_nodes = []
        for node in nodes:
            has_all = True
            for l_entry in lines_data:
                avail_qty = inv_map.get((node["node_id"], l_entry["sku_id"]), 0)
                if avail_qty < l_entry["quantity"]:
                    has_all = False
                    break
            if has_all:
                eligible_single_nodes.append(node)

        is_split = False
        selected_node = None
        selected_nodes_list = []
        order_status = "ALLOCATED"
        shipping_cost = 14.50

        if anomaly_type == "INCORRECT_SPLIT_STATUS_ROLLUP":
            is_split = True
            selected_nodes_list = [nodes[0], nodes[1]]
            selected_node = nodes[0]
        elif anomaly_type == "INVENTORY_SHORTAGE":
            order_status = "EXCEPTION"
            exc_id = f"EXC-2026-{exc_idx:06d}"
            exc_idx += 1
            fulfillment_exceptions.append({
                "exception_id": exc_id,
                "order_id": order_id,
                "shipment_id": None,
                "issue_type": "INVENTORY_SHORTAGE",
                "severity": "CRITICAL",
                "description": f"Order {order_id} requires 9999 units exceeding global network stock.",
                "detection_timestamp": format_dt(placed_dt),
                "expected_behavior": "Trigger inventory alert and block shipment creation.",
                "resolution_status": "OPEN",
                "resolution_notes": None,
                "resolved_at": None,
                "resolved_by": None,
                "ground_truth_label": "INVENTORY_SHORTAGE",
                "created_at": format_dt(placed_dt),
                "updated_at": format_dt(placed_dt)
            })
            ground_truth_records.append({
                "record_id": order_id,
                "issue_type": "INVENTORY_SHORTAGE",
                "expected_result": "FAILED_ALLOCATION",
                "expected_fulfillment_decision": "EXCEPTION_NO_NODE",
                "expected_delivery_status": "EXCEPTION",
                "anomaly_label": "INVENTORY_SHORTAGE"
            })
        elif anomaly_type == "NO_ELIGIBLE_FULFILLMENT_NODE":
            order_status = "EXCEPTION"
            exc_id = f"EXC-2026-{exc_idx:06d}"
            exc_idx += 1
            fulfillment_exceptions.append({
                "exception_id": exc_id,
                "order_id": order_id,
                "shipment_id": None,
                "issue_type": "NO_ELIGIBLE_FULFILLMENT_NODE",
                "severity": "HIGH",
                "description": f"All candidate fulfillment centers fail operating constraints for {order_id}.",
                "detection_timestamp": format_dt(placed_dt),
                "expected_behavior": "Flag order for manual supply chain intervention.",
                "resolution_status": "OPEN",
                "resolution_notes": None,
                "resolved_at": None,
                "resolved_by": None,
                "ground_truth_label": "NO_ELIGIBLE_FULFILLMENT_NODE",
                "created_at": format_dt(placed_dt),
                "updated_at": format_dt(placed_dt)
            })
            ground_truth_records.append({
                "record_id": order_id,
                "issue_type": "NO_ELIGIBLE_FULFILLMENT_NODE",
                "expected_result": "NO_NODE_AVAILABLE",
                "expected_fulfillment_decision": "EXCEPTION_NO_NODE",
                "expected_delivery_status": "EXCEPTION",
                "anomaly_label": "NO_ELIGIBLE_FULFILLMENT_NODE"
            })
        elif eligible_single_nodes:
            selected_node = eligible_single_nodes[ord_num % len(eligible_single_nodes)]
            selected_nodes_list = [selected_node]
        else:
            # Split fulfillment across two nodes
            is_split = True
            selected_nodes_list = [nodes[0], nodes[1]]
            selected_node = nodes[0]

        # Populate order line allocations if not shortage/no_node
        if order_status != "EXCEPTION":
            if not is_split:
                for l_entry in lines_data:
                    l_entry["allocated_quantity"] = l_entry["quantity"]
                    allocations.append({
                        "allocation_id": f"ALC-2026-{alc_idx:06d}",
                        "order_id": order_id,
                        "order_line_id": l_entry["order_line_id"],
                        "node_id": selected_node["node_id"],
                        "sku_id": l_entry["sku_id"],
                        "allocated_quantity": l_entry["quantity"],
                        "allocation_status": "FULFILLED",
                        "created_at": format_dt(placed_dt),
                        "updated_at": format_dt(placed_dt)
                    })
                    alc_idx += 1
            else:
                for idx_l, l_entry in enumerate(lines_data):
                    assigned_n = selected_nodes_list[idx_l % len(selected_nodes_list)]
                    l_entry["allocated_quantity"] = l_entry["quantity"]
                    allocations.append({
                        "allocation_id": f"ALC-2026-{alc_idx:06d}",
                        "order_id": order_id,
                        "order_line_id": l_entry["order_line_id"],
                        "node_id": assigned_n["node_id"],
                        "sku_id": l_entry["sku_id"],
                        "allocated_quantity": l_entry["quantity"],
                        "allocation_status": "FULFILLED",
                        "created_at": format_dt(placed_dt),
                        "updated_at": format_dt(placed_dt)
                    })
                    alc_idx += 1

            # Optimization Decision Record
            chosen_car = carriers[ord_num % len(carriers)]
            chosen_srv = service_levels[ord_num % len(service_levels)]
            opt_strategy = "SPLIT_FULFILLMENT" if is_split else "OPTIMIZED_WEIGHTED"
            
            dec_id = f"DEC-2026-{dec_idx:06d}"
            dec_idx += 1
            optimization_decisions.append({
                "decision_id": dec_id,
                "order_id": order_id,
                "strategy": opt_strategy,
                "selected_nodes": json.dumps([n["node_id"] for n in selected_nodes_list]),
                "candidate_scores": json.dumps({"inventory_score": 92.5, "speed_score": 88.0, "cost_score": 85.0, "reliability_score": 95.0}),
                "weights_used": json.dumps({"inventory": 0.30, "speed": 0.25, "capacity": 0.15, "cost": 0.15, "reliability": 0.10, "risk": 0.05}),
                "total_cost": round(shipping_cost * (2 if is_split else 1), 2),
                "estimated_delivery_days": 2.0,
                "decision_reason": f"Selected node {selected_node['node_id']} with carrier {chosen_car['carrier_name']} based on top composite multi-factor score.",
                "execution_time_ms": round(random.uniform(12.5, 38.0), 2),
                "is_split": is_split,
                "created_at": format_dt(placed_dt)
            })

            # Shipments creation (1 shipment if single, 2 shipments if split)
            shipments_for_order = []
            transit_days = 2
            dispatch_dt = placed_dt + timedelta(hours=6)
            promised_delivery_dt = placed_dt + timedelta(days=transit_days)

            # Anomaly 1: Promise before order creation
            if anomaly_type == "PROMISE_BEFORE_ORDER_CREATION":
                promised_delivery_dt = placed_dt - timedelta(days=2) # injected error
                exc_id = f"EXC-2026-{exc_idx:06d}"
                exc_idx += 1
                fulfillment_exceptions.append({
                    "exception_id": exc_id,
                    "order_id": order_id,
                    "shipment_id": None,
                    "issue_type": "PROMISE_BEFORE_ORDER_CREATION",
                    "severity": "HIGH",
                    "description": f"Promised delivery date {format_dt(promised_delivery_dt)} is earlier than order placement {format_dt(placed_dt)}.",
                    "detection_timestamp": format_dt(placed_dt),
                    "expected_behavior": "Promised delivery date must always be after order placement date.",
                    "resolution_status": "OPEN",
                    "resolution_notes": None,
                    "resolved_at": None,
                    "resolved_by": None,
                    "ground_truth_label": "PROMISE_BEFORE_ORDER_CREATION",
                    "created_at": format_dt(placed_dt),
                    "updated_at": format_dt(placed_dt)
                })
                ground_truth_records.append({
                    "record_id": order_id,
                    "issue_type": "PROMISE_BEFORE_ORDER_CREATION",
                    "expected_result": "DATE_VALIDATION_ERROR",
                    "expected_fulfillment_decision": "REVISE_PROMISE",
                    "expected_delivery_status": "EXCEPTION",
                    "anomaly_label": "PROMISE_BEFORE_ORDER_CREATION"
                })

            # Delivery Promise
            prom_id = f"PROM-ORD-2026-{ord_num:06d}-01"
            delivery_promises.append({
                "promise_id": prom_id,
                "order_id": order_id,
                "shipment_id": None,
                "original_promised_date": format_dt(promised_delivery_dt),
                "revised_promised_date": None,
                "promise_version": 1,
                "is_active": True,
                "confidence_score": 0.96,
                "calculation_factors": json.dumps({"transit_days": transit_days, "cutoff_met": True, "carrier": chosen_car["carrier_name"]}),
                "reason": "Calculated based on operating hours, cutoff compliance, and carrier transit matrix.",
                "created_at": format_dt(placed_dt),
                "updated_at": format_dt(placed_dt)
            })

            # Create shipment instances
            shipment_nodes = selected_nodes_list if is_split else [selected_node]
            for s_idx_sub, s_node in enumerate(shipment_nodes, 1):
                shp_id = f"SHP-2026-{shp_idx:06d}"
                shp_idx += 1
                trk_num = f"TRK-{chosen_car['carrier_id']}-{shp_id[-6:]}"
                
                # Check status distribution
                # If ord_num < 700: DELIVERED
                # 700-850: IN_TRANSIT
                # 850-950: READY_FOR_DISPATCH / DISPATCHED
                # 950-1000: CREATED / PICKING
                if ord_num <= 700:
                    shp_status = "DELIVERED"
                    act_dispatch = dispatch_dt
                    act_delivery = promised_delivery_dt + timedelta(hours=random.randint(-4, 8))
                elif ord_num <= 850:
                    shp_status = "IN_TRANSIT"
                    act_dispatch = dispatch_dt
                    act_delivery = None
                elif ord_num <= 950:
                    shp_status = "DISPATCHED"
                    act_dispatch = dispatch_dt
                    act_delivery = None
                else:
                    shp_status = "READY_FOR_DISPATCH"
                    act_dispatch = None
                    act_delivery = None

                # Anomaly 4: Delivered before dispatch
                if anomaly_type == "DELIVERED_BEFORE_DISPATCH" and s_idx_sub == 1:
                    shp_status = "DELIVERED"
                    act_dispatch = dispatch_dt + timedelta(days=2)
                    act_delivery = dispatch_dt - timedelta(hours=4) # delivered before dispatch!
                    exc_id = f"EXC-2026-{exc_idx:06d}"
                    exc_idx += 1
                    fulfillment_exceptions.append({
                        "exception_id": exc_id,
                        "order_id": order_id,
                        "shipment_id": shp_id,
                        "issue_type": "DELIVERED_BEFORE_DISPATCH",
                        "severity": "CRITICAL",
                        "description": f"Shipment {shp_id} marked delivered at {format_dt(act_delivery)} prior to dispatch {format_dt(act_dispatch)}.",
                        "detection_timestamp": format_dt(placed_dt),
                        "expected_behavior": "Actual delivery timestamp must follow actual dispatch timestamp.",
                        "resolution_status": "OPEN",
                        "resolution_notes": None,
                        "resolved_at": None,
                        "resolved_by": None,
                        "ground_truth_label": "DELIVERED_BEFORE_DISPATCH",
                        "created_at": format_dt(placed_dt),
                        "updated_at": format_dt(placed_dt)
                    })
                    ground_truth_records.append({
                        "record_id": shp_id,
                        "issue_type": "DELIVERED_BEFORE_DISPATCH",
                        "expected_result": "INVALID_TIMESTAMP_SEQUENCE",
                        "expected_fulfillment_decision": "FLAG_SHIPMENT_ERROR",
                        "expected_delivery_status": "EXCEPTION",
                        "anomaly_label": "DELIVERED_BEFORE_DISPATCH"
                    })

                # Anomaly 5: Incorrect split shipment status rollup
                if anomaly_type == "INCORRECT_SPLIT_STATUS_ROLLUP" and is_split:
                    if s_idx_sub == 1:
                        shp_status = "DELIVERED"
                    else:
                        shp_status = "IN_TRANSIT" # One is in transit, but order is falsely DELIVERED
                    exc_id = f"EXC-2026-{exc_idx:06d}"
                    exc_idx += 1
                    fulfillment_exceptions.append({
                        "exception_id": exc_id,
                        "order_id": order_id,
                        "shipment_id": shp_id,
                        "issue_type": "INCORRECT_SPLIT_STATUS_ROLLUP",
                        "severity": "HIGH",
                        "description": f"Order {order_id} was marked DELIVERED while shipment {shp_id} is still IN_TRANSIT.",
                        "detection_timestamp": format_dt(placed_dt),
                        "expected_behavior": "Order-level status must remain PARTIALLY_DELIVERED until all split shipments are DELIVERED.",
                        "resolution_status": "OPEN",
                        "resolution_notes": None,
                        "resolved_at": None,
                        "resolved_by": None,
                        "ground_truth_label": "INCORRECT_SPLIT_STATUS_ROLLUP",
                        "created_at": format_dt(placed_dt),
                        "updated_at": format_dt(placed_dt)
                    })
                    ground_truth_records.append({
                        "record_id": order_id,
                        "issue_type": "INCORRECT_SPLIT_STATUS_ROLLUP",
                        "expected_result": "STATUS_ROLLUP_MISMATCH",
                        "expected_fulfillment_decision": "REVISE_ORDER_STATUS",
                        "expected_delivery_status": "PARTIALLY_DELIVERED",
                        "anomaly_label": "INCORRECT_SPLIT_STATUS_ROLLUP"
                    })

                shp_obj = {
                    "shipment_id": shp_id,
                    "order_id": order_id,
                    "node_id": s_node["node_id"],
                    "carrier_id": chosen_car["carrier_id"],
                    "service_id": chosen_srv["service_id"],
                    "shipment_status": shp_status,
                    "tracking_number": trk_num,
                    "shipping_cost": shipping_cost,
                    "total_weight_kg": 2.5,
                    "scheduled_dispatch_date": format_dt(dispatch_dt),
                    "actual_dispatch_date": format_dt(act_dispatch) if act_dispatch else None,
                    "promised_delivery_date": format_dt(promised_delivery_dt),
                    "actual_delivery_date": format_dt(act_delivery) if act_delivery else None,
                    "is_split": is_split,
                    "created_at": format_dt(placed_dt),
                    "updated_at": format_dt(placed_dt)
                }
                shipments.append(shp_obj)
                shipments_for_order.append(shp_obj)

                # Shipment Lines
                for l_entry in lines_data:
                    shipment_lines.append({
                        "shipment_line_id": f"SHPL-2026-{shpl_idx:06d}",
                        "shipment_id": shp_id,
                        "order_line_id": l_entry["order_line_id"],
                        "sku_id": l_entry["sku_id"],
                        "quantity": l_entry["quantity"],
                        "created_at": format_dt(placed_dt),
                        "updated_at": format_dt(placed_dt)
                    })
                    shpl_idx += 1

                # Tracking Events
                # Build valid event progression up to shp_status
                event_chain = [
                    ("CREATED", placed_dt, "Shipment order created in system"),
                    ("INVENTORY_RESERVED", placed_dt + timedelta(minutes=15), "Stock reserved at fulfillment center"),
                    ("PICKING", placed_dt + timedelta(hours=1), "Items picked from warehouse aisles"),
                    ("PACKED", placed_dt + timedelta(hours=2), "Order packed and labeled for carrier handover"),
                    ("READY_FOR_DISPATCH", placed_dt + timedelta(hours=3), "Staged at carrier dispatch bay"),
                    ("DISPATCHED", dispatch_dt, f"Handed over to carrier {chosen_car['carrier_name']}"),
                    ("IN_TRANSIT", dispatch_dt + timedelta(hours=12), "Departed regional carrier sorting facility"),
                    ("OUT_FOR_DELIVERY", promised_delivery_dt - timedelta(hours=3), "Courier out for final delivery"),
                    ("DELIVERED", promised_delivery_dt, "Package handed to customer")
                ]

                # Anomaly 10: Invalid tracking sequence (jump CREATED to DELIVERED)
                if anomaly_type == "INVALID_TRACKING_SEQUENCE" and s_idx_sub == 1:
                    exc_id = f"EXC-2026-{exc_idx:06d}"
                    exc_idx += 1
                    fulfillment_exceptions.append({
                        "exception_id": exc_id,
                        "order_id": order_id,
                        "shipment_id": shp_id,
                        "issue_type": "INVALID_TRACKING_SEQUENCE",
                        "severity": "HIGH",
                        "description": f"Shipment {shp_id} skipped required transit states: transitioned directly from CREATED to DELIVERED.",
                        "detection_timestamp": format_dt(placed_dt),
                        "expected_behavior": "Shipments must pass through DISPATCHED and IN_TRANSIT before reaching DELIVERED.",
                        "resolution_status": "OPEN",
                        "resolution_notes": None,
                        "resolved_at": None,
                        "resolved_by": None,
                        "ground_truth_label": "INVALID_TRACKING_SEQUENCE",
                        "created_at": format_dt(placed_dt),
                        "updated_at": format_dt(placed_dt)
                    })
                    ground_truth_records.append({
                        "record_id": shp_id,
                        "issue_type": "INVALID_TRACKING_SEQUENCE",
                        "expected_result": "INVALID_LIFECYCLE_TRANSITION",
                        "expected_fulfillment_decision": "AUDIT_TRACKING_EVENTS",
                        "expected_delivery_status": "EXCEPTION",
                        "anomaly_label": "INVALID_TRACKING_SEQUENCE"
                    })
                    event_chain = [
                        ("CREATED", placed_dt, "Shipment created"),
                        ("DELIVERED", promised_delivery_dt, "Abruptly marked delivered")
                    ]

                # Stop event chain at current shp_status
                for ev_status, ev_time, ev_desc in event_chain:
                    t_ev_id = f"TRK-SHP-{shp_id[-6:]}-{trk_idx:03d}"
                    trk_idx += 1
                    tracking_events.append({
                        "event_id": t_ev_id,
                        "shipment_id": shp_id,
                        "event_status": ev_status,
                        "location": f"{s_node['city']}, {s_node['state']}",
                        "description": ev_desc,
                        "event_timestamp": format_dt(ev_time),
                        "is_delayed": False,
                        "delay_reason": None,
                        "created_at": format_dt(ev_time)
                    })
                    if ev_status == shp_status:
                        break

            # Calculate order-level status from shipments
            if anomaly_type == "INCORRECT_SPLIT_STATUS_ROLLUP":
                final_order_status = "DELIVERED" # injected false rollup
            else:
                statuses = [s["shipment_status"] for s in shipments_for_order]
                if all(s == "DELIVERED" for s in statuses):
                    final_order_status = "DELIVERED"
                elif any(s == "DELIVERED" for s in statuses):
                    final_order_status = "PARTIALLY_DELIVERED"
                elif any(s in ("DISPATCHED", "IN_TRANSIT", "OUT_FOR_DELIVERY") for s in statuses):
                    final_order_status = "SHIPPED"
                elif any(s in ("PICKING", "PACKED", "READY_FOR_DISPATCH") for s in statuses):
                    final_order_status = "PROCESSING"
                else:
                    final_order_status = "ALLOCATED"
        else:
            final_order_status = "EXCEPTION"

        # Additional Injected Anomalies (2, 3, 6, 7)
        if anomaly_type == "ALLOCATION_EXCEEDS_INVENTORY":
            exc_id = f"EXC-2026-{exc_idx:06d}"
            exc_idx += 1
            fulfillment_exceptions.append({
                "exception_id": exc_id,
                "order_id": order_id,
                "shipment_id": None,
                "issue_type": "ALLOCATION_EXCEEDS_INVENTORY",
                "severity": "HIGH",
                "description": f"Allocation for order {order_id} reserved more units than available inventory at node {selected_node['node_id']}.",
                "detection_timestamp": format_dt(placed_dt),
                "expected_behavior": "Allocations must not exceed available node inventory.",
                "resolution_status": "OPEN",
                "resolution_notes": None,
                "resolved_at": None,
                "resolved_by": None,
                "ground_truth_label": "ALLOCATION_EXCEEDS_INVENTORY",
                "created_at": format_dt(placed_dt),
                "updated_at": format_dt(placed_dt)
            })
            ground_truth_records.append({
                "record_id": order_id,
                "issue_type": "ALLOCATION_EXCEEDS_INVENTORY",
                "expected_result": "INSUFFICIENT_STOCK",
                "expected_fulfillment_decision": "REALLOCATE",
                "expected_delivery_status": "EXCEPTION",
                "anomaly_label": "ALLOCATION_EXCEEDS_INVENTORY"
            })

        if anomaly_type == "UNSUPPORTED_SHIPPING_ZONE":
            exc_id = f"EXC-2026-{exc_idx:06d}"
            exc_idx += 1
            fulfillment_exceptions.append({
                "exception_id": exc_id,
                "order_id": order_id,
                "shipment_id": None,
                "issue_type": "UNSUPPORTED_SHIPPING_ZONE",
                "severity": "MEDIUM",
                "description": f"Selected carrier service CAR-2026-010 does not support destination {dest_zone} for order {order_id}.",
                "detection_timestamp": format_dt(placed_dt),
                "expected_behavior": "Filter out unsupported carrier-zone combinations.",
                "resolution_status": "OPEN",
                "resolution_notes": None,
                "resolved_at": None,
                "resolved_by": None,
                "ground_truth_label": "UNSUPPORTED_SHIPPING_ZONE",
                "created_at": format_dt(placed_dt),
                "updated_at": format_dt(placed_dt)
            })
            ground_truth_records.append({
                "record_id": order_id,
                "issue_type": "UNSUPPORTED_SHIPPING_ZONE",
                "expected_result": "UNSUPPORTED_ZONE",
                "expected_fulfillment_decision": "SELECT_ALTERNATIVE_CARRIER",
                "expected_delivery_status": "EXCEPTION",
                "anomaly_label": "UNSUPPORTED_SHIPPING_ZONE"
            })

        if anomaly_type == "WAREHOUSE_CAPACITY_EXCEEDED":
            exc_id = f"EXC-2026-{exc_idx:06d}"
            exc_idx += 1
            fulfillment_exceptions.append({
                "exception_id": exc_id,
                "order_id": order_id,
                "shipment_id": None,
                "issue_type": "WAREHOUSE_CAPACITY_EXCEEDED",
                "severity": "HIGH",
                "description": f"Node {selected_node['node_id']} daily processing capacity exceeded for date {placed_dt.date()}.",
                "detection_timestamp": format_dt(placed_dt),
                "expected_behavior": "Shift dispatch to next available processing day or reroute to secondary warehouse.",
                "resolution_status": "OPEN",
                "resolution_notes": None,
                "resolved_at": None,
                "resolved_by": None,
                "ground_truth_label": "WAREHOUSE_CAPACITY_EXCEEDED",
                "created_at": format_dt(placed_dt),
                "updated_at": format_dt(placed_dt)
            })
            ground_truth_records.append({
                "record_id": order_id,
                "issue_type": "WAREHOUSE_CAPACITY_EXCEEDED",
                "expected_result": "CAPACITY_OVERLOAD",
                "expected_fulfillment_decision": "ROLL_TO_NEXT_BUSINESS_DAY",
                "expected_delivery_status": "EXCEPTION",
                "anomaly_label": "WAREHOUSE_CAPACITY_EXCEEDED"
            })

        if anomaly_type == "CARRIER_CUTOFF_MISSED":
            exc_id = f"EXC-2026-{exc_idx:06d}"
            exc_idx += 1
            fulfillment_exceptions.append({
                "exception_id": exc_id,
                "order_id": order_id,
                "shipment_id": None,
                "issue_type": "CARRIER_CUTOFF_MISSED",
                "severity": "MEDIUM",
                "description": f"Order {order_id} processed after carrier pickup cutoff 17:00; dispatched same day unexpectedly.",
                "detection_timestamp": format_dt(placed_dt),
                "expected_behavior": "Carrier pickup cutoff missed requires dispatch next operating business day.",
                "resolution_status": "OPEN",
                "resolution_notes": None,
                "resolved_at": None,
                "resolved_by": None,
                "ground_truth_label": "CARRIER_CUTOFF_MISSED",
                "created_at": format_dt(placed_dt),
                "updated_at": format_dt(placed_dt)
            })
            ground_truth_records.append({
                "record_id": order_id,
                "issue_type": "CARRIER_CUTOFF_MISSED",
                "expected_result": "CUTOFF_VIOLATION",
                "expected_fulfillment_decision": "SCHEDULE_NEXT_DAY_PICKUP",
                "expected_delivery_status": "EXCEPTION",
                "anomaly_label": "CARRIER_CUTOFF_MISSED"
            })

        orders.append({
            "order_id": order_id,
            "customer_id": cust_id,
            "customer_name": f"Customer {cust_id[-4:]}",
            "customer_email": f"cust{cust_id[-4:]}@example.com",
            "destination_address": dest_addr,
            "destination_city": dest_city,
            "destination_state": dest_state,
            "destination_zip": dest_zip,
            "destination_zone": dest_zone,
            "order_priority": priority,
            "order_status": final_order_status,
            "total_amount": round(total_order_amount, 2),
            "shipping_fee": round(shipping_cost, 2),
            "placed_at": format_dt(placed_dt),
            "promised_delivery_date": format_dt(promised_delivery_dt) if order_status != "EXCEPTION" else None,
            "actual_delivery_date": format_dt(promised_delivery_dt) if final_order_status == "DELIVERED" else None,
            "is_split": is_split,
            "created_at": format_dt(placed_dt),
            "updated_at": format_dt(placed_dt)
        })

        order_lines.extend(lines_data)

    # Write all data files
    dataset_manifest = {
        "skus": (skus, "skus.csv"),
        "fulfillment_nodes": (nodes, "fulfillment_nodes.csv"),
        "carriers": (carriers, "carriers.csv"),
        "service_levels": (service_levels, "service_levels.csv"),
        "carrier_service_zones": (carrier_service_zones, "carrier_service_zones.csv"),
        "warehouse_calendars": (warehouse_calendars, "warehouse_calendars.csv"),
        "carrier_calendars": (carrier_calendars, "carrier_calendars.csv"),
        "warehouse_capacities": (warehouse_capacities, "warehouse_capacities.csv"),
        "inventories": (inventories, "inventories.csv"),
        "orders": (orders, "orders.csv"),
        "order_lines": (order_lines, "order_lines.csv"),
        "allocations": (allocations, "allocations.csv"),
        "optimization_decisions": (optimization_decisions, "optimization_decisions.csv"),
        "shipments": (shipments, "shipments.csv"),
        "shipment_lines": (shipment_lines, "shipment_lines.csv"),
        "tracking_events": (tracking_events, "tracking_events.csv"),
        "delivery_promises": (delivery_promises, "delivery_promises.csv"),
        "fulfillment_exceptions": (fulfillment_exceptions, "fulfillment_exceptions.csv")
    }

    print("\nWriting generated CSV tables...")
    for entity_name, (records, fname) in dataset_manifest.items():
        fpath = os.path.join(output_dir, fname)
        if records:
            keys = list(records[0].keys())
            with open(fpath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(records)
            print(f"  -> {fname:30s}: {len(records):6d} records")

    # Write ground_truth.csv
    gt_path = os.path.join(ground_truth_dir, "ground_truth.csv")
    if ground_truth_records:
        keys = ["record_id", "issue_type", "expected_result", "expected_fulfillment_decision", "expected_delivery_status", "anomaly_label"]
        with open(gt_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(ground_truth_records)
        print(f"  -> {'ground_truth.csv':30s}: {len(ground_truth_records):6d} records")

    print("\nSynthetic data generation completed successfully!")
    return {k: len(v[0]) for k, v in dataset_manifest.items()}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synthetic Data Generator for Fulfillment System")
    parser.add_argument("--mode", choices=["starter", "full"], default="starter", help="starter (1,000 orders) or full (50,000 orders)")
    parser.add_argument("--outdir", default="data/generated", help="Output directory for generated CSVs")
    parser.add_argument("--gtdir", default="data/ground_truth", help="Output directory for ground truth")
    args = parser.parse_args()
    generate_all(mode=args.mode, output_dir=args.outdir, ground_truth_dir=args.gtdir)

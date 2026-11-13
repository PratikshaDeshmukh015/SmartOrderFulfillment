import csv
import os
import sys
import glob
from datetime import datetime, date

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from backend.app.database import SessionLocal, engine, Base
from backend.app.models.entities import (
    Order, OrderLine, SKU, FulfillmentNode, Inventory, WarehouseCapacity,
    Carrier, ServiceLevel, CarrierServiceZone, CarrierCalendar, WarehouseCalendar,
    Shipment, ShipmentLine, TrackingEvent, DeliveryPromise, Allocation,
    FulfillmentException, OptimizationDecision
)

def parse_dt(dt_str):
    if not dt_str:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            pass
    return None

def parse_date(d_str):
    if not d_str:
        return None
    try:
        return datetime.strptime(d_str, "%Y-%m-%d").date()
    except ValueError:
        return None

def parse_bool(b_val):
    if isinstance(b_val, bool):
        return b_val
    if isinstance(b_val, str):
        return b_val.lower() in ("true", "1", "t", "yes")
    return bool(b_val)

def seed_all(data_dir="data/generated"):
    print("Initializing database tables and seeding records...")
    # Recreate all tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    def read_csv(filename):
        fpath = os.path.join(data_dir, filename)
        if not os.path.exists(fpath):
            return []
        with open(fpath, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    try:
        # Clear existing records in reverse dependency order
        print("Clearing previous records...")
        db.query(TrackingEvent).delete()
        db.query(ShipmentLine).delete()
        db.query(Shipment).delete()
        db.query(Allocation).delete()
        db.query(DeliveryPromise).delete()
        db.query(OptimizationDecision).delete()
        db.query(FulfillmentException).delete()
        db.query(OrderLine).delete()
        db.query(Order).delete()
        db.query(Inventory).delete()
        db.query(WarehouseCapacity).delete()
        db.query(WarehouseCalendar).delete()
        db.query(CarrierServiceZone).delete()
        db.query(CarrierCalendar).delete()
        db.query(ServiceLevel).delete()
        db.query(Carrier).delete()
        db.query(FulfillmentNode).delete()
        db.query(SKU).delete()
        db.commit()

        # 1. SKUs
        print("Seeding SKUs...")
        skus_data = read_csv("skus.csv")
        for r in skus_data:
            db.add(SKU(
                sku_id=r["sku_id"],
                sku_name=r["sku_name"],
                category=r["category"],
                weight_kg=float(r["weight_kg"]),
                volume_m3=float(r["volume_m3"]),
                unit_price=float(r["unit_price"]),
                handling_type=r["handling_type"],
                is_active=parse_bool(r["is_active"]),
                created_at=parse_dt(r["created_at"]),
                updated_at=parse_dt(r["updated_at"])
            ))
        db.commit()

        # 2. Fulfillment Nodes
        print("Seeding Fulfillment Nodes...")
        nodes_data = read_csv("fulfillment_nodes.csv")
        for r in nodes_data:
            db.add(FulfillmentNode(
                node_id=r["node_id"],
                node_name=r["node_name"],
                node_type=r["node_type"],
                address=r["address"],
                city=r["city"],
                state=r["state"],
                zip_code=r["zip_code"],
                latitude=float(r["latitude"]),
                longitude=float(r["longitude"]),
                daily_order_capacity=int(r["daily_order_capacity"]),
                daily_unit_capacity=int(r["daily_unit_capacity"]),
                processing_cutoff_time=r["processing_cutoff_time"],
                operating_hours_start=r["operating_hours_start"],
                operating_hours_end=r["operating_hours_end"],
                weekend_operations=parse_bool(r["weekend_operations"]),
                is_active=parse_bool(r["is_active"]),
                created_at=parse_dt(r["created_at"]),
                updated_at=parse_dt(r["updated_at"])
            ))
        db.commit()

        # 3. Carriers
        print("Seeding Carriers...")
        carriers_data = read_csv("carriers.csv")
        for r in carriers_data:
            db.add(Carrier(
                carrier_id=r["carrier_id"],
                carrier_name=r["carrier_name"],
                contact_email=r["contact_email"],
                phone=r["phone"],
                reliability_score=float(r["reliability_score"]),
                is_active=parse_bool(r["is_active"]),
                created_at=parse_dt(r["created_at"]),
                updated_at=parse_dt(r["updated_at"])
            ))
        db.commit()

        # 4. Service Levels
        print("Seeding Service Levels...")
        service_data = read_csv("service_levels.csv")
        for r in service_data:
            db.add(ServiceLevel(
                service_id=r["service_id"],
                carrier_id=r["carrier_id"],
                service_name=r["service_name"],
                service_code=r["service_code"],
                base_rate=float(r["base_rate"]),
                rate_per_kg=float(r["rate_per_kg"]),
                rate_per_zone=float(r["rate_per_zone"]),
                guaranteed_delivery=parse_bool(r["guaranteed_delivery"]),
                created_at=parse_dt(r["created_at"]),
                updated_at=parse_dt(r["updated_at"])
            ))
        db.commit()

        # 5. Carrier Service Zones
        print("Seeding Carrier Service Zones...")
        zones_data = read_csv("carrier_service_zones.csv")
        batch = []
        for r in zones_data:
            batch.append(CarrierServiceZone(
                zone_id=r["zone_id"],
                service_id=r["service_id"],
                origin_node_id=r["origin_node_id"],
                destination_zone=r["destination_zone"],
                transit_days=int(r["transit_days"]),
                is_supported=parse_bool(r["is_supported"]),
                pickup_time=r["pickup_time"],
                created_at=parse_dt(r["created_at"]),
                updated_at=parse_dt(r["updated_at"])
            ))
            if len(batch) >= 1000:
                db.bulk_save_objects(batch)
                db.commit()
                batch = []
        if batch:
            db.bulk_save_objects(batch)
            db.commit()

        # 6. Calendars
        print("Seeding Calendars...")
        wcal_data = read_csv("warehouse_calendars.csv")
        db.bulk_save_objects([
            WarehouseCalendar(
                calendar_id=r["calendar_id"],
                node_id=r["node_id"],
                date=parse_date(r["date"]),
                is_operating=parse_bool(r["is_operating"]),
                holiday_name=r.get("holiday_name") or None,
                created_at=parse_dt(r["created_at"]),
                updated_at=parse_dt(r["updated_at"])
            ) for r in wcal_data
        ])
        db.commit()

        ccal_data = read_csv("carrier_calendars.csv")
        db.bulk_save_objects([
            CarrierCalendar(
                calendar_id=r["calendar_id"],
                carrier_id=r["carrier_id"],
                date=parse_date(r["date"]),
                is_operating=parse_bool(r["is_operating"]),
                holiday_name=r.get("holiday_name") or None,
                created_at=parse_dt(r["created_at"]),
                updated_at=parse_dt(r["updated_at"])
            ) for r in ccal_data
        ])
        db.commit()

        # 7. Warehouse Capacities
        print("Seeding Warehouse Capacities...")
        cap_data = read_csv("warehouse_capacities.csv")
        db.bulk_save_objects([
            WarehouseCapacity(
                capacity_id=r["capacity_id"],
                node_id=r["node_id"],
                date=parse_date(r["date"]),
                max_orders=int(r["max_orders"]),
                utilized_orders=int(r["utilized_orders"]),
                max_units=int(r["max_units"]),
                utilized_units=int(r["utilized_units"]),
                created_at=parse_dt(r["created_at"]),
                updated_at=parse_dt(r["updated_at"])
            ) for r in cap_data
        ])
        db.commit()

        # 8. Inventories
        print("Seeding Inventories...")
        inv_data = read_csv("inventories.csv")
        db.bulk_save_objects([
            Inventory(
                inventory_id=r["inventory_id"],
                node_id=r["node_id"],
                sku_id=r["sku_id"],
                available_quantity=int(r["available_quantity"]),
                reserved_quantity=int(r["reserved_quantity"]),
                reorder_threshold=int(r["reorder_threshold"]),
                safety_stock=int(r["safety_stock"]),
                last_restocked_at=parse_dt(r["last_restocked_at"]),
                created_at=parse_dt(r["created_at"]),
                updated_at=parse_dt(r["updated_at"])
            ) for r in inv_data
        ])
        db.commit()

        # 9. Orders
        print("Seeding Orders...")
        orders_data = read_csv("orders.csv")
        db.bulk_save_objects([
            Order(
                order_id=r["order_id"],
                customer_id=r["customer_id"],
                customer_name=r["customer_name"],
                customer_email=r["customer_email"],
                destination_address=r["destination_address"],
                destination_city=r["destination_city"],
                destination_state=r["destination_state"],
                destination_zip=r["destination_zip"],
                destination_zone=r["destination_zone"],
                order_priority=r["order_priority"],
                order_status=r["order_status"],
                total_amount=float(r["total_amount"]),
                shipping_fee=float(r["shipping_fee"]),
                placed_at=parse_dt(r["placed_at"]),
                promised_delivery_date=parse_dt(r.get("promised_delivery_date")),
                actual_delivery_date=parse_dt(r.get("actual_delivery_date")),
                is_split=parse_bool(r["is_split"]),
                created_at=parse_dt(r["created_at"]),
                updated_at=parse_dt(r["updated_at"])
            ) for r in orders_data
        ])
        db.commit()

        # 10. Order Lines
        print("Seeding Order Lines...")
        lines_data = read_csv("order_lines.csv")
        db.bulk_save_objects([
            OrderLine(
                order_line_id=r["order_line_id"],
                order_id=r["order_id"],
                sku_id=r["sku_id"],
                quantity=int(r["quantity"]),
                unit_price=float(r["unit_price"]),
                line_total=float(r["line_total"]),
                allocated_quantity=int(r["allocated_quantity"]),
                created_at=parse_dt(r["created_at"]),
                updated_at=parse_dt(r["updated_at"])
            ) for r in lines_data
        ])
        db.commit()

        # 11. Allocations
        print("Seeding Allocations...")
        alc_data = read_csv("allocations.csv")
        db.bulk_save_objects([
            Allocation(
                allocation_id=r["allocation_id"],
                order_id=r["order_id"],
                order_line_id=r["order_line_id"],
                node_id=r["node_id"],
                sku_id=r["sku_id"],
                allocated_quantity=int(r["allocated_quantity"]),
                allocation_status=r["allocation_status"],
                created_at=parse_dt(r["created_at"]),
                updated_at=parse_dt(r["updated_at"])
            ) for r in alc_data
        ])
        db.commit()

        # 12. Optimization Decisions
        print("Seeding Optimization Decisions...")
        dec_data = read_csv("optimization_decisions.csv")
        db.bulk_save_objects([
            OptimizationDecision(
                decision_id=r["decision_id"],
                order_id=r["order_id"],
                strategy=r["strategy"],
                selected_nodes=r["selected_nodes"],
                candidate_scores=r["candidate_scores"],
                weights_used=r["weights_used"],
                total_cost=float(r["total_cost"]),
                estimated_delivery_days=float(r["estimated_delivery_days"]),
                decision_reason=r["decision_reason"],
                execution_time_ms=float(r["execution_time_ms"]),
                is_split=parse_bool(r["is_split"]),
                created_at=parse_dt(r["created_at"])
            ) for r in dec_data
        ])
        db.commit()

        # 13. Shipments
        print("Seeding Shipments...")
        shipments_data = read_csv("shipments.csv")
        db.bulk_save_objects([
            Shipment(
                shipment_id=r["shipment_id"],
                order_id=r["order_id"],
                node_id=r["node_id"],
                carrier_id=r["carrier_id"],
                service_id=r["service_id"],
                shipment_status=r["shipment_status"],
                tracking_number=r["tracking_number"],
                shipping_cost=float(r["shipping_cost"]),
                total_weight_kg=float(r["total_weight_kg"]),
                scheduled_dispatch_date=parse_dt(r["scheduled_dispatch_date"]),
                actual_dispatch_date=parse_dt(r.get("actual_dispatch_date")),
                promised_delivery_date=parse_dt(r["promised_delivery_date"]),
                actual_delivery_date=parse_dt(r.get("actual_delivery_date")),
                is_split=parse_bool(r["is_split"]),
                created_at=parse_dt(r["created_at"]),
                updated_at=parse_dt(r["updated_at"])
            ) for r in shipments_data
        ])
        db.commit()

        # 14. Shipment Lines
        print("Seeding Shipment Lines...")
        shpl_data = read_csv("shipment_lines.csv")
        db.bulk_save_objects([
            ShipmentLine(
                shipment_line_id=r["shipment_line_id"],
                shipment_id=r["shipment_id"],
                order_line_id=r["order_line_id"],
                sku_id=r["sku_id"],
                quantity=int(r["quantity"]),
                created_at=parse_dt(r["created_at"]),
                updated_at=parse_dt(r["updated_at"])
            ) for r in shpl_data
        ])
        db.commit()

        # 15. Tracking Events
        print("Seeding Tracking Events...")
        trk_data = read_csv("tracking_events.csv")
        batch = []
        for r in trk_data:
            batch.append(TrackingEvent(
                event_id=r["event_id"],
                shipment_id=r["shipment_id"],
                event_status=r["event_status"],
                location=r["location"],
                description=r["description"],
                event_timestamp=parse_dt(r["event_timestamp"]),
                is_delayed=parse_bool(r["is_delayed"]),
                delay_reason=r.get("delay_reason") or None,
                created_at=parse_dt(r["created_at"])
            ))
            if len(batch) >= 1000:
                db.bulk_save_objects(batch)
                db.commit()
                batch = []
        if batch:
            db.bulk_save_objects(batch)
            db.commit()

        # 16. Delivery Promises
        print("Seeding Delivery Promises...")
        prom_data = read_csv("delivery_promises.csv")
        db.bulk_save_objects([
            DeliveryPromise(
                promise_id=r["promise_id"],
                order_id=r["order_id"],
                shipment_id=r.get("shipment_id") or None,
                original_promised_date=parse_dt(r["original_promised_date"]),
                revised_promised_date=parse_dt(r.get("revised_promised_date")),
                promise_version=int(r["promise_version"]),
                is_active=parse_bool(r["is_active"]),
                confidence_score=float(r["confidence_score"]),
                calculation_factors=r.get("calculation_factors"),
                reason=r["reason"],
                created_at=parse_dt(r["created_at"]),
                updated_at=parse_dt(r["updated_at"])
            ) for r in prom_data
        ])
        db.commit()

        # 17. Fulfillment Exceptions
        print("Seeding Fulfillment Exceptions...")
        exc_data = read_csv("fulfillment_exceptions.csv")
        db.bulk_save_objects([
            FulfillmentException(
                exception_id=r["exception_id"],
                order_id=r.get("order_id") or None,
                shipment_id=r.get("shipment_id") or None,
                issue_type=r["issue_type"],
                severity=r["severity"],
                description=r["description"],
                detection_timestamp=parse_dt(r["detection_timestamp"]),
                expected_behavior=r["expected_behavior"],
                resolution_status=r["resolution_status"],
                resolution_notes=r.get("resolution_notes") or None,
                resolved_at=parse_dt(r.get("resolved_at")),
                resolved_by=r.get("resolved_by") or None,
                ground_truth_label=r.get("ground_truth_label") or None,
                created_at=parse_dt(r["created_at"]),
                updated_at=parse_dt(r["updated_at"])
            ) for r in exc_data
        ])
        db.commit()

        print("\nAll database tables successfully seeded!")
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_all()

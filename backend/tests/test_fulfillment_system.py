import pytest
from datetime import datetime, date, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.app.models.entities import (
    Order, OrderLine, SKU, FulfillmentNode, Inventory, WarehouseCapacity,
    WarehouseCalendar, Carrier, ServiceLevel, CarrierServiceZone, CarrierCalendar,
    Shipment, TrackingEvent, FulfillmentException
)
from backend.app.models.enums import OrderStatus, ShipmentStatus, ExceptionSeverity, ExceptionResolutionStatus
from backend.app.services.inventory_service import InventoryService
from backend.app.services.warehouse_service import WarehouseService
from backend.app.services.carrier_service import CarrierService
from backend.app.services.shipment_service import ShipmentService
from backend.app.services.delivery_promise import DeliveryPromiseEngine
from backend.app.services.exception_service import ExceptionService
from backend.app.algorithms.scoring import FulfillmentScorer
from backend.app.algorithms.allocation import OrderSplitAllocator
from backend.app.algorithms.optimization import FulfillmentOptimizationEngine

# Setup in-memory SQLite fixture for rapid isolated testing
@pytest.fixture(scope="function")
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSession()

    # Seed minimal baseline testing entities
    sku1 = SKU(sku_id="SKU-TEST-001", sku_name="Test Electronics", category="Electronics", weight_kg=1.5, volume_m3=0.01, unit_price=100.0)
    sku2 = SKU(sku_id="SKU-TEST-002", sku_name="Test Apparel", category="Apparel", weight_kg=0.5, volume_m3=0.005, unit_price=40.0)
    db.add_all([sku1, sku2])

    node1 = FulfillmentNode(
        node_id="FUL-TEST-001", node_name="Chicago Hub", address="100 Test St",
        city="Chicago", state="IL", zip_code="60601", latitude=41.8781, longitude=-87.6298,
        daily_order_capacity=1000, daily_unit_capacity=5000, processing_cutoff_time="14:00"
    )
    node2 = FulfillmentNode(
        node_id="FUL-TEST-002", node_name="Dallas Center", address="200 South St",
        city="Dallas", state="TX", zip_code="75201", latitude=32.7767, longitude=-96.7970,
        daily_order_capacity=500, daily_unit_capacity=2500, processing_cutoff_time="15:00"
    )
    db.add_all([node1, node2])

    inv1 = Inventory(inventory_id="INV-001", node_id="FUL-TEST-001", sku_id="SKU-TEST-001", available_quantity=50, reserved_quantity=0)
    inv2 = Inventory(inventory_id="INV-002", node_id="FUL-TEST-001", sku_id="SKU-TEST-002", available_quantity=0, reserved_quantity=0) # out of stock
    inv3 = Inventory(inventory_id="INV-003", node_id="FUL-TEST-002", sku_id="SKU-TEST-002", available_quantity=30, reserved_quantity=0)
    db.add_all([inv1, inv2, inv3])

    car1 = Carrier(carrier_id="CAR-TEST-001", carrier_name="Swift Air", contact_email="test@swift.com", phone="123", reliability_score=0.96)
    db.add(car1)

    srv1 = ServiceLevel(service_id="SRV-TEST-001", carrier_id="CAR-TEST-001", service_name="Next Day Air", service_code="AIR_1D", base_rate=20.0, rate_per_kg=2.0, rate_per_zone=2.0)
    db.add(srv1)

    csz1 = CarrierServiceZone(zone_id="CSZ-001", service_id="SRV-TEST-001", origin_node_id="FUL-TEST-001", destination_zone="Zone 4", transit_days=1, is_supported=True)
    csz2 = CarrierServiceZone(zone_id="CSZ-002", service_id="SRV-TEST-001", origin_node_id="FUL-TEST-002", destination_zone="Zone 4", transit_days=2, is_supported=True)
    db.add_all([csz1, csz2])

    order1 = Order(
        order_id="ORD-TEST-001", customer_id="CUST-1", customer_name="Alice", customer_email="alice@test.com",
        destination_address="123 Lake St", destination_city="Chicago", destination_state="IL", destination_zip="60602",
        destination_zone="Zone 4", order_status=OrderStatus.CREATED, total_amount=100.0,
        placed_at=datetime(2026, 11, 15, 10, 0, 0, tzinfo=timezone.utc)
    )
    db.add(order1)

    ol1 = OrderLine(order_line_id="ORD-TEST-001-01", order_id="ORD-TEST-001", sku_id="SKU-TEST-001", quantity=2, unit_price=100.0, line_total=200.0)
    db.add(ol1)

    db.commit()
    yield db
    db.close()

# 1. Normal order fulfillment
def test_normal_order_fulfillment(test_db):
    engine = FulfillmentOptimizationEngine(test_db)
    result = engine.optimize_order("ORD-TEST-001", persist_decision=False)
    assert result["selected_node_id"] == "FUL-TEST-001"
    assert result["strategy"] == "OPTIMIZED_WEIGHTED"
    assert result["weighted_score"] > 80.0
    assert result["is_split"] is False

# 2. Insufficient inventory exception
def test_insufficient_inventory(test_db):
    # Order requiring more units than global stock
    ol_large = OrderLine(order_line_id="ORD-TEST-001-02", order_id="ORD-TEST-001", sku_id="SKU-TEST-001", quantity=500, unit_price=100.0, line_total=50000.0)
    test_db.add(ol_large)
    test_db.commit()

    engine = FulfillmentOptimizationEngine(test_db)
    result = engine.optimize_order("ORD-TEST-001", persist_decision=False)
    assert result["strategy"] == "EXCEPTION_NO_NODE"
    assert "INVENTORY_SHORTAGE" in result["decision_reason"]

# 3. Split fulfillment evaluation
def test_split_fulfillment(test_db):
    # Order requires SKU 1 (only in node 1) and SKU 2 (only in node 2)
    ol2 = OrderLine(order_line_id="ORD-TEST-001-02", order_id="ORD-TEST-001", sku_id="SKU-TEST-002", quantity=2, unit_price=40.0, line_total=80.0)
    test_db.add(ol2)
    test_db.commit()

    lines = [{"sku_id": "SKU-TEST-001", "quantity": 2}, {"sku_id": "SKU-TEST-002", "quantity": 2}]
    nodes = [
        {"node_id": "FUL-TEST-001", "node_name": "Chicago Hub", "city": "Chicago"},
        {"node_id": "FUL-TEST-002", "node_name": "Dallas Center", "city": "Dallas"}
    ]
    eval_res = OrderSplitAllocator.evaluate_split_allocation(test_db, lines, nodes)
    assert eval_res["can_fulfill"] is True
    assert eval_res["is_split"] is True
    assert len(eval_res["split_plan"]) == 2

# 4. Warehouse capacity headroom constraint
def test_warehouse_capacity_exceeded(test_db):
    test_date = date(2026, 11, 15)
    cap = WarehouseCapacity(capacity_id="CAP-1", node_id="FUL-TEST-001", date=test_date, max_orders=100, utilized_orders=100, max_units=500, utilized_units=500)
    test_db.add(cap)
    test_db.commit()

    has_room = WarehouseService.has_available_capacity(test_db, "FUL-TEST-001", test_date, required_units=5)
    assert has_room is False

# 5. Carrier cutoff passed rolls to next day
def test_carrier_cutoff_passed(test_db):
    placed_late = datetime(2026, 11, 15, 16, 30, 0, tzinfo=timezone.utc) # After 14:00 cutoff
    calc = DeliveryPromiseEngine.calculate_promised_date(
        test_db, "ORD-TEST-001", "FUL-TEST-001", "CAR-TEST-001", transit_days=1, placed_at=placed_late
    )
    assert calc["calculation_factors"]["cutoff_met"] is False
    # Dispatch must roll to Nov 16
    assert calc["dispatch_datetime"].date() == date(2026, 11, 16)

# 6. Holiday delivery calculation
def test_holiday_skipping(test_db):
    holiday_date = date(2026, 11, 16)
    w_cal = WarehouseCalendar(calendar_id="WCAL-TEST", node_id="FUL-TEST-001", date=holiday_date, is_operating=False, holiday_name="Civic Holiday")
    test_db.add(w_cal)
    test_db.commit()

    placed_late = datetime(2026, 11, 15, 18, 0, 0, tzinfo=timezone.utc)
    calc = DeliveryPromiseEngine.calculate_promised_date(
        test_db, "ORD-TEST-001", "FUL-TEST-001", "CAR-TEST-001", transit_days=1, placed_at=placed_late
    )
    # Must skip holiday Nov 16 and dispatch on Nov 17
    assert calc["dispatch_datetime"].date() == date(2026, 11, 17)

# 7. Unsupported shipping zone rejection
def test_unsupported_shipping_zone(test_db):
    srvs = CarrierService.get_eligible_services(test_db, "FUL-TEST-001", "Zone 8") # Zone 8 unsupported
    assert len(srvs) == 0

# 8. Invalid tracking event transition rejected
def test_invalid_tracking_sequence(test_db):
    shp = Shipment(
        shipment_id="SHP-TEST-001", order_id="ORD-TEST-001", node_id="FUL-TEST-001",
        carrier_id="CAR-TEST-001", service_id="SRV-TEST-001", shipment_status=ShipmentStatus.CREATED,
        tracking_number="TRK-TEST-001", shipping_cost=15.0, total_weight_kg=1.0,
        scheduled_dispatch_date=datetime.now(timezone.utc), promised_delivery_date=datetime.now(timezone.utc)
    )
    test_db.add(shp)
    test_db.commit()

    # Attempting to jump directly from CREATED to DELIVERED must raise ValueError
    with pytest.raises(ValueError) as excinfo:
        ShipmentService.add_tracking_event(
            test_db, "SHP-TEST-001", ShipmentStatus.DELIVERED, "Customer Address", "Delivered"
        )
    assert "Invalid lifecycle transition" in str(excinfo.value)

# 9. Split shipment status rollup
def test_split_shipment_status_rollup(test_db):
    shp1 = Shipment(
        shipment_id="SHP-SPLIT-01", order_id="ORD-TEST-001", node_id="FUL-TEST-001",
        carrier_id="CAR-TEST-001", service_id="SRV-TEST-001", shipment_status=ShipmentStatus.DELIVERED,
        tracking_number="TRK-S-01", shipping_cost=10.0, scheduled_dispatch_date=datetime.now(timezone.utc),
        promised_delivery_date=datetime.now(timezone.utc), actual_delivery_date=datetime.now(timezone.utc)
    )
    shp2 = Shipment(
        shipment_id="SHP-SPLIT-02", order_id="ORD-TEST-001", node_id="FUL-TEST-002",
        carrier_id="CAR-TEST-001", service_id="SRV-TEST-001", shipment_status=ShipmentStatus.IN_TRANSIT,
        tracking_number="TRK-S-02", shipping_cost=10.0, scheduled_dispatch_date=datetime.now(timezone.utc),
        promised_delivery_date=datetime.now(timezone.utc)
    )
    test_db.add_all([shp1, shp2])
    test_db.commit()

    # Order must be PARTIALLY_DELIVERED, not DELIVERED
    order_status = ShipmentService.rollup_order_status(test_db, "ORD-TEST-001")
    assert order_status == OrderStatus.PARTIALLY_DELIVERED

    # Once second shipment delivers, order becomes DELIVERED
    shp2.shipment_status = ShipmentStatus.DELIVERED
    shp2.actual_delivery_date = datetime.now(timezone.utc)
    test_db.commit()

    final_status = ShipmentService.rollup_order_status(test_db, "ORD-TEST-001")
    assert final_status == OrderStatus.DELIVERED

# 10. Exception Resolution Workflow
def test_exception_resolution(test_db):
    exc = FulfillmentException(
        exception_id="EXC-TEST-001", order_id="ORD-TEST-001", issue_type="WAREHOUSE_CAPACITY_EXCEEDED",
        severity=ExceptionSeverity.HIGH, description="Capacity exceeded", detection_timestamp=datetime.now(timezone.utc),
        expected_behavior="Reschedule dispatch", resolution_status=ExceptionResolutionStatus.OPEN
    )
    test_db.add(exc)
    test_db.commit()

    resolved = ExceptionService.resolve_exception(
        test_db, "EXC-TEST-001", resolution_notes="Dispatched on morning shift.", resolved_by="OpsManager"
    )
    assert resolved.resolution_status == ExceptionResolutionStatus.RESOLVED
    assert resolved.resolved_by == "OpsManager"
    assert resolved.resolved_at is not None

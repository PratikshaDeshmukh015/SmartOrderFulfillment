from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date, Text, ForeignKey,
    UniqueConstraint, Index, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from backend.app.database import Base
from backend.app.models.enums import (
    OrderStatus, OrderPriority, ShipmentStatus, HandlingType, NodeType,
    AllocationStatus, ExceptionSeverity, ExceptionResolutionStatus,
    OptimizationStrategy
)

def utcnow():
    return datetime.now(timezone.utc)

# 1. Order
class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String(50), primary_key=True, index=True) # e.g. ORD-2026-000001
    customer_id = Column(String(50), nullable=False, index=True)
    customer_name = Column(String(100), nullable=False)
    customer_email = Column(String(150), nullable=False)
    destination_address = Column(String(255), nullable=False)
    destination_city = Column(String(100), nullable=False)
    destination_state = Column(String(50), nullable=False)
    destination_zip = Column(String(20), nullable=False)
    destination_zone = Column(String(20), nullable=False, index=True) # e.g. Zone 1 - Zone 8
    order_priority = Column(SQLEnum(OrderPriority), default=OrderPriority.STANDARD, nullable=False)
    order_status = Column(SQLEnum(OrderStatus), default=OrderStatus.CREATED, nullable=False, index=True)
    total_amount = Column(Float, default=0.0, nullable=False)
    shipping_fee = Column(Float, default=0.0, nullable=False)
    placed_at = Column(DateTime, nullable=False, default=utcnow, index=True)
    promised_delivery_date = Column(DateTime, nullable=True)
    actual_delivery_date = Column(DateTime, nullable=True)
    is_split = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    lines = relationship("OrderLine", back_populates="order", cascade="all, delete-orphan")
    shipments = relationship("Shipment", back_populates="order")
    delivery_promises = relationship("DeliveryPromise", back_populates="order")
    allocations = relationship("Allocation", back_populates="order")
    exceptions = relationship("FulfillmentException", back_populates="order")
    decisions = relationship("OptimizationDecision", back_populates="order")

# 2. OrderLine
class OrderLine(Base):
    __tablename__ = "order_lines"

    order_line_id = Column(String(60), primary_key=True, index=True) # e.g. ORD-2026-000001-01
    order_id = Column(String(50), ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False, index=True)
    sku_id = Column(String(50), ForeignKey("skus.sku_id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    line_total = Column(Float, nullable=False)
    allocated_quantity = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="lines")
    sku = relationship("SKU", back_populates="order_lines")
    shipment_lines = relationship("ShipmentLine", back_populates="order_line")
    allocations = relationship("Allocation", back_populates="order_line")

# 3. SKU
class SKU(Base):
    __tablename__ = "skus"

    sku_id = Column(String(50), primary_key=True, index=True) # e.g. SKU-2026-00001
    sku_name = Column(String(150), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    weight_kg = Column(Float, default=1.0, nullable=False)
    volume_m3 = Column(Float, default=0.01, nullable=False)
    unit_price = Column(Float, default=10.0, nullable=False)
    handling_type = Column(SQLEnum(HandlingType), default=HandlingType.STANDARD, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    order_lines = relationship("OrderLine", back_populates="sku")
    inventories = relationship("Inventory", back_populates="sku")
    shipment_lines = relationship("ShipmentLine", back_populates="sku")
    allocations = relationship("Allocation", back_populates="sku")

# 4. FulfillmentNode
class FulfillmentNode(Base):
    __tablename__ = "fulfillment_nodes"

    node_id = Column(String(50), primary_key=True, index=True) # e.g. FUL-2026-000001
    node_name = Column(String(150), nullable=False)
    node_type = Column(SQLEnum(NodeType), default=NodeType.FULFILLMENT_CENTER, nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    zip_code = Column(String(20), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    daily_order_capacity = Column(Integer, default=1000, nullable=False)
    daily_unit_capacity = Column(Integer, default=5000, nullable=False)
    processing_cutoff_time = Column(String(10), default="14:00", nullable=False) # HH:MM
    operating_hours_start = Column(String(10), default="08:00", nullable=False)
    operating_hours_end = Column(String(10), default="20:00", nullable=False)
    weekend_operations = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    inventories = relationship("Inventory", back_populates="node")
    capacities = relationship("WarehouseCapacity", back_populates="node")
    service_zones = relationship("CarrierServiceZone", back_populates="node")
    warehouse_calendars = relationship("WarehouseCalendar", back_populates="node")
    shipments = relationship("Shipment", back_populates="node")
    allocations = relationship("Allocation", back_populates="node")

# 5. Inventory
class Inventory(Base):
    __tablename__ = "inventories"

    inventory_id = Column(String(50), primary_key=True, index=True) # e.g. INV-2026-000001
    node_id = Column(String(50), ForeignKey("fulfillment_nodes.node_id"), nullable=False, index=True)
    sku_id = Column(String(50), ForeignKey("skus.sku_id"), nullable=False, index=True)
    available_quantity = Column(Integer, default=0, nullable=False)
    reserved_quantity = Column(Integer, default=0, nullable=False)
    reorder_threshold = Column(Integer, default=20, nullable=False)
    safety_stock = Column(Integer, default=10, nullable=False)
    last_restocked_at = Column(DateTime, default=utcnow, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("node_id", "sku_id", name="uq_node_sku"),
    )

    # Relationships
    node = relationship("FulfillmentNode", back_populates="inventories")
    sku = relationship("SKU", back_populates="inventories")

# 6. WarehouseCapacity
class WarehouseCapacity(Base):
    __tablename__ = "warehouse_capacities"

    capacity_id = Column(String(50), primary_key=True, index=True) # e.g. CAP-2026-000001
    node_id = Column(String(50), ForeignKey("fulfillment_nodes.node_id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    max_orders = Column(Integer, default=1000, nullable=False)
    utilized_orders = Column(Integer, default=0, nullable=False)
    max_units = Column(Integer, default=5000, nullable=False)
    utilized_units = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("node_id", "date", name="uq_node_date_capacity"),
    )

    # Relationships
    node = relationship("FulfillmentNode", back_populates="capacities")

# 7. Carrier
class Carrier(Base):
    __tablename__ = "carriers"

    carrier_id = Column(String(50), primary_key=True, index=True) # e.g. CAR-2026-001
    carrier_name = Column(String(100), nullable=False)
    contact_email = Column(String(150), nullable=False)
    phone = Column(String(50), nullable=False)
    reliability_score = Column(Float, default=0.95, nullable=False) # 0.0 - 1.0
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    services = relationship("ServiceLevel", back_populates="carrier")
    carrier_calendars = relationship("CarrierCalendar", back_populates="carrier")
    shipments = relationship("Shipment", back_populates="carrier")

# 8. ServiceLevel
class ServiceLevel(Base):
    __tablename__ = "service_levels"

    service_id = Column(String(50), primary_key=True, index=True) # e.g. SRV-2026-001
    carrier_id = Column(String(50), ForeignKey("carriers.carrier_id"), nullable=False, index=True)
    service_name = Column(String(100), nullable=False) # Next Day Air, 2-Day Express, Ground Standard
    service_code = Column(String(50), nullable=False, index=True)
    base_rate = Column(Float, default=10.0, nullable=False)
    rate_per_kg = Column(Float, default=1.5, nullable=False)
    rate_per_zone = Column(Float, default=2.0, nullable=False)
    guaranteed_delivery = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    carrier = relationship("Carrier", back_populates="services")
    service_zones = relationship("CarrierServiceZone", back_populates="service")
    shipments = relationship("Shipment", back_populates="service")

# 9. CarrierServiceZone
class CarrierServiceZone(Base):
    __tablename__ = "carrier_service_zones"

    zone_id = Column(String(50), primary_key=True, index=True) # e.g. CSZ-2026-00001
    service_id = Column(String(50), ForeignKey("service_levels.service_id"), nullable=False, index=True)
    origin_node_id = Column(String(50), ForeignKey("fulfillment_nodes.node_id"), nullable=False, index=True)
    destination_zone = Column(String(20), nullable=False, index=True) # Zone 1 to Zone 8
    transit_days = Column(Integer, default=2, nullable=False)
    is_supported = Column(Boolean, default=True, nullable=False)
    pickup_time = Column(String(10), default="17:00", nullable=False) # Carrier daily pickup cutoff
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("service_id", "origin_node_id", "destination_zone", name="uq_service_origin_zone"),
    )

    # Relationships
    service = relationship("ServiceLevel", back_populates="service_zones")
    node = relationship("FulfillmentNode", back_populates="service_zones")

# 10. CarrierCalendar
class CarrierCalendar(Base):
    __tablename__ = "carrier_calendars"

    calendar_id = Column(String(50), primary_key=True, index=True) # e.g. CCAL-2026-00001
    carrier_id = Column(String(50), ForeignKey("carriers.carrier_id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    is_operating = Column(Boolean, default=True, nullable=False)
    holiday_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("carrier_id", "date", name="uq_carrier_date"),
    )

    # Relationships
    carrier = relationship("Carrier", back_populates="carrier_calendars")

# 11. WarehouseCalendar
class WarehouseCalendar(Base):
    __tablename__ = "warehouse_calendars"

    calendar_id = Column(String(50), primary_key=True, index=True) # e.g. WCAL-2026-00001
    node_id = Column(String(50), ForeignKey("fulfillment_nodes.node_id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    is_operating = Column(Boolean, default=True, nullable=False)
    holiday_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("node_id", "date", name="uq_node_date"),
    )

    # Relationships
    node = relationship("FulfillmentNode", back_populates="warehouse_calendars")

# 12. Shipment
class Shipment(Base):
    __tablename__ = "shipments"

    shipment_id = Column(String(50), primary_key=True, index=True) # e.g. SHP-2026-000001
    order_id = Column(String(50), ForeignKey("orders.order_id"), nullable=False, index=True)
    node_id = Column(String(50), ForeignKey("fulfillment_nodes.node_id"), nullable=False, index=True)
    carrier_id = Column(String(50), ForeignKey("carriers.carrier_id"), nullable=False, index=True)
    service_id = Column(String(50), ForeignKey("service_levels.service_id"), nullable=False, index=True)
    shipment_status = Column(SQLEnum(ShipmentStatus), default=ShipmentStatus.CREATED, nullable=False, index=True)
    tracking_number = Column(String(100), unique=True, nullable=False, index=True)
    shipping_cost = Column(Float, default=0.0, nullable=False)
    total_weight_kg = Column(Float, default=1.0, nullable=False)
    scheduled_dispatch_date = Column(DateTime, nullable=False)
    actual_dispatch_date = Column(DateTime, nullable=True)
    promised_delivery_date = Column(DateTime, nullable=False)
    actual_delivery_date = Column(DateTime, nullable=True)
    is_split = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="shipments")
    node = relationship("FulfillmentNode", back_populates="shipments")
    carrier = relationship("Carrier", back_populates="shipments")
    service = relationship("ServiceLevel", back_populates="shipments")
    lines = relationship("ShipmentLine", back_populates="shipment", cascade="all, delete-orphan")
    tracking_events = relationship("TrackingEvent", back_populates="shipment", order_by="TrackingEvent.event_timestamp")
    delivery_promises = relationship("DeliveryPromise", back_populates="shipment")
    exceptions = relationship("FulfillmentException", back_populates="shipment")

# 13. ShipmentLine
class ShipmentLine(Base):
    __tablename__ = "shipment_lines"

    shipment_line_id = Column(String(60), primary_key=True, index=True) # e.g. SHPL-2026-000001-01
    shipment_id = Column(String(50), ForeignKey("shipments.shipment_id", ondelete="CASCADE"), nullable=False, index=True)
    order_line_id = Column(String(60), ForeignKey("order_lines.order_line_id"), nullable=False, index=True)
    sku_id = Column(String(50), ForeignKey("skus.sku_id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    shipment = relationship("Shipment", back_populates="lines")
    order_line = relationship("OrderLine", back_populates="shipment_lines")
    sku = relationship("SKU", back_populates="shipment_lines")

# 14. TrackingEvent (Immutable event stream)
class TrackingEvent(Base):
    __tablename__ = "tracking_events"

    event_id = Column(String(60), primary_key=True, index=True) # e.g. TRK-SHP-2026-000001-001
    shipment_id = Column(String(50), ForeignKey("shipments.shipment_id"), nullable=False, index=True)
    event_status = Column(SQLEnum(ShipmentStatus), nullable=False, index=True)
    location = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    event_timestamp = Column(DateTime, nullable=False, index=True)
    is_delayed = Column(Boolean, default=False, nullable=False)
    delay_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    shipment = relationship("Shipment", back_populates="tracking_events")

# 15. DeliveryPromise (Historical promise revisions)
class DeliveryPromise(Base):
    __tablename__ = "delivery_promises"

    promise_id = Column(String(60), primary_key=True, index=True) # e.g. PROM-ORD-2026-000001-01
    order_id = Column(String(50), ForeignKey("orders.order_id"), nullable=False, index=True)
    shipment_id = Column(String(50), ForeignKey("shipments.shipment_id"), nullable=True, index=True)
    original_promised_date = Column(DateTime, nullable=False)
    revised_promised_date = Column(DateTime, nullable=True)
    promise_version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    confidence_score = Column(Float, default=0.95, nullable=False)
    calculation_factors = Column(Text, nullable=True) # JSON representation of transit, cutoffs, buffers
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="delivery_promises")
    shipment = relationship("Shipment", back_populates="delivery_promises")

# 16. Allocation
class Allocation(Base):
    __tablename__ = "allocations"

    allocation_id = Column(String(60), primary_key=True, index=True) # e.g. ALC-2026-000001-01
    order_id = Column(String(50), ForeignKey("orders.order_id"), nullable=False, index=True)
    order_line_id = Column(String(60), ForeignKey("order_lines.order_line_id"), nullable=False, index=True)
    node_id = Column(String(50), ForeignKey("fulfillment_nodes.node_id"), nullable=False, index=True)
    sku_id = Column(String(50), ForeignKey("skus.sku_id"), nullable=False, index=True)
    allocated_quantity = Column(Integer, nullable=False)
    allocation_status = Column(SQLEnum(AllocationStatus), default=AllocationStatus.RESERVED, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="allocations")
    order_line = relationship("OrderLine", back_populates="allocations")
    node = relationship("FulfillmentNode", back_populates="allocations")
    sku = relationship("SKU", back_populates="allocations")

# 17. FulfillmentException
class FulfillmentException(Base):
    __tablename__ = "fulfillment_exceptions"

    exception_id = Column(String(50), primary_key=True, index=True) # e.g. EXC-2026-000001
    order_id = Column(String(50), ForeignKey("orders.order_id"), nullable=True, index=True)
    shipment_id = Column(String(50), ForeignKey("shipments.shipment_id"), nullable=True, index=True)
    issue_type = Column(String(100), nullable=False, index=True)
    severity = Column(SQLEnum(ExceptionSeverity), default=ExceptionSeverity.MEDIUM, nullable=False, index=True)
    description = Column(Text, nullable=False)
    detection_timestamp = Column(DateTime, default=utcnow, nullable=False)
    expected_behavior = Column(Text, nullable=False)
    resolution_status = Column(SQLEnum(ExceptionResolutionStatus), default=ExceptionResolutionStatus.OPEN, nullable=False, index=True)
    resolution_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(100), nullable=True)
    ground_truth_label = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="exceptions")
    shipment = relationship("Shipment", back_populates="exceptions")

# 18. OptimizationDecision (Decision logging and explainability)
class OptimizationDecision(Base):
    __tablename__ = "optimization_decisions"

    decision_id = Column(String(50), primary_key=True, index=True) # e.g. DEC-2026-000001
    order_id = Column(String(50), ForeignKey("orders.order_id"), nullable=False, index=True)
    strategy = Column(SQLEnum(OptimizationStrategy), default=OptimizationStrategy.OPTIMIZED_WEIGHTED, nullable=False)
    selected_nodes = Column(Text, nullable=False) # JSON list of nodes chosen
    candidate_scores = Column(Text, nullable=False) # JSON breakdown of candidate warehouse scores
    weights_used = Column(Text, nullable=False) # JSON weights
    total_cost = Column(Float, default=0.0, nullable=False)
    estimated_delivery_days = Column(Float, default=0.0, nullable=False)
    decision_reason = Column(Text, nullable=False)
    execution_time_ms = Column(Float, default=0.0, nullable=False)
    is_split = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="decisions")

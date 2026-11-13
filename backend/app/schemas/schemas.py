from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from backend.app.models.enums import (
    OrderStatus, OrderPriority, ShipmentStatus, HandlingType, NodeType,
    AllocationStatus, ExceptionSeverity, ExceptionResolutionStatus,
    OptimizationStrategy
)

# --- SKU Schemas ---
class SKUBase(BaseModel):
    sku_id: str
    sku_name: str
    category: str
    weight_kg: float
    volume_m3: float
    unit_price: float
    handling_type: HandlingType
    is_active: bool = True

class SKUResponse(SKUBase):
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

# --- Inventory Schemas ---
class InventoryBase(BaseModel):
    inventory_id: str
    node_id: str
    sku_id: str
    available_quantity: int
    reserved_quantity: int
    reorder_threshold: int = 20
    safety_stock: int = 10

class InventoryResponse(InventoryBase):
    last_restocked_at: datetime
    created_at: datetime
    updated_at: datetime
    sku_name: Optional[str] = None
    node_name: Optional[str] = None
    class Config:
        from_attributes = True

# --- Fulfillment Node & Capacity Schemas ---
class FulfillmentNodeBase(BaseModel):
    node_id: str
    node_name: str
    node_type: NodeType
    address: str
    city: str
    state: str
    zip_code: str
    latitude: float
    longitude: float
    daily_order_capacity: int
    daily_unit_capacity: int
    processing_cutoff_time: str
    operating_hours_start: str
    operating_hours_end: str
    weekend_operations: bool
    is_active: bool

class FulfillmentNodeResponse(FulfillmentNodeBase):
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class WarehouseCapacityResponse(BaseModel):
    capacity_id: str
    node_id: str
    date: date
    max_orders: int
    utilized_orders: int
    max_units: int
    utilized_units: int
    order_utilization_pct: float = 0.0
    unit_utilization_pct: float = 0.0
    class Config:
        from_attributes = True

# --- Carrier Schemas ---
class ServiceLevelResponse(BaseModel):
    service_id: str
    carrier_id: str
    service_name: str
    service_code: str
    base_rate: float
    rate_per_kg: float
    rate_per_zone: float
    guaranteed_delivery: bool
    class Config:
        from_attributes = True

class CarrierResponse(BaseModel):
    carrier_id: str
    carrier_name: str
    contact_email: str
    phone: str
    reliability_score: float
    is_active: bool
    services: List[ServiceLevelResponse] = []
    class Config:
        from_attributes = True

# --- Order & Line Schemas ---
class OrderLineCreate(BaseModel):
    sku_id: str
    quantity: int = Field(..., gt=0)
    unit_price: Optional[float] = None

class OrderLineResponse(BaseModel):
    order_line_id: str
    order_id: str
    sku_id: str
    quantity: int
    unit_price: float
    line_total: float
    allocated_quantity: int
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    customer_id: str
    customer_name: str
    customer_email: str
    destination_address: str
    destination_city: str
    destination_state: str
    destination_zip: str
    destination_zone: str = "Zone 2" # Zone 1 to Zone 8
    order_priority: OrderPriority = OrderPriority.STANDARD
    lines: List[OrderLineCreate]

class OrderResponse(BaseModel):
    order_id: str
    customer_id: str
    customer_name: str
    customer_email: str
    destination_address: str
    destination_city: str
    destination_state: str
    destination_zip: str
    destination_zone: str
    order_priority: OrderPriority
    order_status: OrderStatus
    total_amount: float
    shipping_fee: float
    placed_at: datetime
    promised_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    is_split: bool
    created_at: datetime
    updated_at: datetime
    lines: List[OrderLineResponse] = []
    class Config:
        from_attributes = True

class OrderStatusResponse(BaseModel):
    order_id: str
    order_status: OrderStatus
    is_split: bool
    total_lines: int
    fulfilled_lines: int
    shipment_count: int
    shipments: List[Dict[str, Any]] = []

# --- Shipment & Tracking Schemas ---
class ShipmentLineResponse(BaseModel):
    shipment_line_id: str
    shipment_id: str
    order_line_id: str
    sku_id: str
    quantity: int
    class Config:
        from_attributes = True

class TrackingEventCreate(BaseModel):
    event_status: ShipmentStatus
    location: str
    description: str
    event_timestamp: Optional[datetime] = None
    is_delayed: bool = False
    delay_reason: Optional[str] = None

class TrackingEventResponse(BaseModel):
    event_id: str
    shipment_id: str
    event_status: ShipmentStatus
    location: str
    description: str
    event_timestamp: datetime
    is_delayed: bool
    delay_reason: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class ShipmentResponse(BaseModel):
    shipment_id: str
    order_id: str
    node_id: str
    carrier_id: str
    service_id: str
    shipment_status: ShipmentStatus
    tracking_number: str
    shipping_cost: float
    total_weight_kg: float
    scheduled_dispatch_date: datetime
    actual_dispatch_date: Optional[datetime] = None
    promised_delivery_date: datetime
    actual_delivery_date: Optional[datetime] = None
    is_split: bool
    node_name: Optional[str] = None
    carrier_name: Optional[str] = None
    service_name: Optional[str] = None
    lines: List[ShipmentLineResponse] = []
    tracking_events: List[TrackingEventResponse] = []
    class Config:
        from_attributes = True

# --- Delivery Promise Schemas ---
class DeliveryPromiseResponse(BaseModel):
    promise_id: str
    order_id: str
    shipment_id: Optional[str] = None
    original_promised_date: datetime
    revised_promised_date: Optional[datetime] = None
    promise_version: int
    is_active: bool
    confidence_score: float
    calculation_factors: Optional[Dict[str, Any]] = None
    reason: str
    created_at: datetime
    class Config:
        from_attributes = True

# --- Fulfillment Exception Schemas ---
class FulfillmentExceptionResponse(BaseModel):
    exception_id: str
    order_id: Optional[str] = None
    shipment_id: Optional[str] = None
    issue_type: str
    severity: ExceptionSeverity
    description: str
    detection_timestamp: datetime
    expected_behavior: str
    resolution_status: ExceptionResolutionStatus
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    ground_truth_label: Optional[str] = None
    class Config:
        from_attributes = True

class ExceptionResolveRequest(BaseModel):
    resolution_notes: str
    resolved_by: str = "SupplyChainManager"
    resolution_status: ExceptionResolutionStatus = ExceptionResolutionStatus.RESOLVED

# --- Optimization Engine Schemas ---
class FactorScores(BaseModel):
    inventory_availability: float # 0 to 100
    delivery_speed: float         # 0 to 100
    warehouse_capacity: float     # 0 to 100
    shipping_cost: float          # 0 to 100
    carrier_reliability: float    # 0 to 100
    operational_risk: float       # 0 to 100 (higher means lower risk/safer)

class CandidateOption(BaseModel):
    node_id: str
    node_name: str
    carrier_id: str
    carrier_name: str
    service_id: str
    service_name: str
    transit_days: int
    shipping_cost: float
    scheduled_dispatch: datetime
    promised_delivery: datetime
    weighted_score: float
    factor_scores: FactorScores
    is_eligible: bool
    eligibility_reasons: List[str] = []
    rejection_reasons: List[str] = []

class OptimizationWeights(BaseModel):
    inventory: float = 0.30
    speed: float = 0.25
    capacity: float = 0.15
    cost: float = 0.15
    reliability: float = 0.10
    risk: float = 0.05

class OptimizationResultResponse(BaseModel):
    decision_id: str
    order_id: str
    strategy: OptimizationStrategy
    is_split: bool
    selected_node_id: Optional[str] = None
    selected_node_name: Optional[str] = None
    selected_carrier: Optional[str] = None
    selected_service: Optional[str] = None
    estimated_dispatch: Optional[datetime] = None
    promised_delivery: Optional[datetime] = None
    shipping_cost: float
    weighted_score: float
    decision_reason: str
    candidate_options: List[CandidateOption] = []
    split_details: Optional[List[Dict[str, Any]]] = None
    weights_applied: OptimizationWeights
    execution_time_ms: float

class BaselineComparisonResponse(BaseModel):
    order_id: str
    baseline: Dict[str, Any] # Nearest Node strategy
    optimized: Dict[str, Any] # Weighted Optimization strategy
    cost_difference: float
    delivery_days_difference: float
    risk_reduction_pct: float
    improvement_summary: str

# --- Analytics Schemas ---
class AnalyticsOverviewResponse(BaseModel):
    total_orders: int
    fulfilled_orders: int
    pending_orders: int
    delayed_orders: int
    on_time_delivery_pct: float
    avg_delivery_days: float
    split_shipment_pct: float
    fulfillment_success_rate: float
    active_exceptions: int
    total_inventory_units: int
    avg_shipping_cost: float

class AnalyticsCarrierResponse(BaseModel):
    carrier_id: str
    carrier_name: str
    total_shipments: int
    on_time_shipments: int
    on_time_pct: float
    avg_transit_days: float
    avg_cost: float
    reliability_score: float

class AnalyticsFulfillmentResponse(BaseModel):
    node_id: str
    node_name: str
    total_allocated_orders: int
    daily_order_capacity: int
    avg_capacity_utilization_pct: float
    total_units_shipped: int
    split_order_contributions: int

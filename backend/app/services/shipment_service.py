from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.models.entities import Shipment, ShipmentLine, TrackingEvent, Order, FulfillmentNode, Carrier, ServiceLevel
from backend.app.models.enums import ShipmentStatus, OrderStatus

# Valid status transitions
ALLOWED_TRANSITIONS = {
    ShipmentStatus.CREATED: {ShipmentStatus.INVENTORY_RESERVED, ShipmentStatus.CANCELLED},
    ShipmentStatus.INVENTORY_RESERVED: {ShipmentStatus.ALLOCATION_CONFIRMED, ShipmentStatus.PICKING, ShipmentStatus.CANCELLED},
    ShipmentStatus.ALLOCATION_CONFIRMED: {ShipmentStatus.PICKING, ShipmentStatus.CANCELLED},
    ShipmentStatus.PICKING: {ShipmentStatus.PACKED, ShipmentStatus.CANCELLED},
    ShipmentStatus.PACKED: {ShipmentStatus.READY_FOR_DISPATCH, ShipmentStatus.CANCELLED},
    ShipmentStatus.READY_FOR_DISPATCH: {ShipmentStatus.DISPATCHED, ShipmentStatus.CANCELLED},
    ShipmentStatus.DISPATCHED: {ShipmentStatus.IN_TRANSIT, ShipmentStatus.DELIVERY_DELAYED, ShipmentStatus.CANCELLED},
    ShipmentStatus.IN_TRANSIT: {ShipmentStatus.OUT_FOR_DELIVERY, ShipmentStatus.DELIVERY_DELAYED, ShipmentStatus.DELIVERY_FAILED},
    ShipmentStatus.OUT_FOR_DELIVERY: {ShipmentStatus.DELIVERED, ShipmentStatus.DELIVERY_DELAYED, ShipmentStatus.DELIVERY_FAILED},
    ShipmentStatus.DELIVERY_DELAYED: {ShipmentStatus.IN_TRANSIT, ShipmentStatus.OUT_FOR_DELIVERY, ShipmentStatus.DELIVERED, ShipmentStatus.DELIVERY_FAILED},
    ShipmentStatus.DELIVERY_FAILED: {ShipmentStatus.OUT_FOR_DELIVERY, ShipmentStatus.CANCELLED},
    ShipmentStatus.DELIVERED: set(), # Terminal
    ShipmentStatus.CANCELLED: set()  # Terminal
}

class ShipmentService:
    @staticmethod
    def get_shipments(
        db: Session,
        order_id: Optional[str] = None,
        node_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        query = (
            db.query(Shipment, FulfillmentNode.node_name, Carrier.carrier_name, ServiceLevel.service_name)
            .join(FulfillmentNode, Shipment.node_id == FulfillmentNode.node_id)
            .join(Carrier, Shipment.carrier_id == Carrier.carrier_id)
            .join(ServiceLevel, Shipment.service_id == ServiceLevel.service_id)
        )
        if order_id:
            query = query.filter(Shipment.order_id == order_id)
        if node_id:
            query = query.filter(Shipment.node_id == node_id)
        if status:
            query = query.filter(Shipment.shipment_status == status)

        records = query.order_by(Shipment.created_at.desc()).offset(offset).limit(limit).all()
        result = []
        for shp, node_name, carrier_name, service_name in records:
            result.append({
                "shipment_id": shp.shipment_id,
                "order_id": shp.order_id,
                "node_id": shp.node_id,
                "node_name": node_name,
                "carrier_id": shp.carrier_id,
                "carrier_name": carrier_name,
                "service_id": shp.service_id,
                "service_name": service_name,
                "shipment_status": shp.shipment_status.value if hasattr(shp.shipment_status, "value") else str(shp.shipment_status),
                "tracking_number": shp.tracking_number,
                "shipping_cost": shp.shipping_cost,
                "total_weight_kg": shp.total_weight_kg,
                "scheduled_dispatch_date": shp.scheduled_dispatch_date.isoformat() if shp.scheduled_dispatch_date else None,
                "actual_dispatch_date": shp.actual_dispatch_date.isoformat() if shp.actual_dispatch_date else None,
                "promised_delivery_date": shp.promised_delivery_date.isoformat() if shp.promised_delivery_date else None,
                "actual_delivery_date": shp.actual_delivery_date.isoformat() if shp.actual_delivery_date else None,
                "is_split": shp.is_split,
                "created_at": shp.created_at.isoformat() if shp.created_at else None
            })
        return result

    @staticmethod
    def get_shipment_by_id(db: Session, shipment_id: str) -> Optional[Dict[str, Any]]:
        shp = db.query(Shipment).filter(Shipment.shipment_id == shipment_id).first()
        if not shp:
            return None

        node = db.query(FulfillmentNode).filter(FulfillmentNode.node_id == shp.node_id).first()
        carrier = db.query(Carrier).filter(Carrier.carrier_id == shp.carrier_id).first()
        service = db.query(ServiceLevel).filter(ServiceLevel.service_id == shp.service_id).first()
        lines = db.query(ShipmentLine).filter(ShipmentLine.shipment_id == shipment_id).all()
        events = db.query(TrackingEvent).filter(TrackingEvent.shipment_id == shipment_id).order_by(TrackingEvent.event_timestamp.asc()).all()

        return {
            "shipment_id": shp.shipment_id,
            "order_id": shp.order_id,
            "node_id": shp.node_id,
            "node_name": node.node_name if node else None,
            "carrier_id": shp.carrier_id,
            "carrier_name": carrier.carrier_name if carrier else None,
            "service_id": shp.service_id,
            "service_name": service.service_name if service else None,
            "shipment_status": shp.shipment_status.value if hasattr(shp.shipment_status, "value") else str(shp.shipment_status),
            "tracking_number": shp.tracking_number,
            "shipping_cost": shp.shipping_cost,
            "total_weight_kg": shp.total_weight_kg,
            "scheduled_dispatch_date": shp.scheduled_dispatch_date.isoformat() if shp.scheduled_dispatch_date else None,
            "actual_dispatch_date": shp.actual_dispatch_date.isoformat() if shp.actual_dispatch_date else None,
            "promised_delivery_date": shp.promised_delivery_date.isoformat() if shp.promised_delivery_date else None,
            "actual_delivery_date": shp.actual_delivery_date.isoformat() if shp.actual_delivery_date else None,
            "is_split": shp.is_split,
            "lines": [{
                "shipment_line_id": l.shipment_line_id,
                "order_line_id": l.order_line_id,
                "sku_id": l.sku_id,
                "quantity": l.quantity
            } for l in lines],
            "tracking_events": [{
                "event_id": e.event_id,
                "event_status": e.event_status.value if hasattr(e.event_status, "value") else str(e.event_status),
                "location": e.location,
                "description": e.description,
                "event_timestamp": e.event_timestamp.isoformat() if e.event_timestamp else None,
                "is_delayed": e.is_delayed,
                "delay_reason": e.delay_reason
            } for e in events]
        }

    @classmethod
    def add_tracking_event(
        cls,
        db: Session,
        shipment_id: str,
        target_status: ShipmentStatus,
        location: str,
        description: str,
        event_time: Optional[datetime] = None,
        is_delayed: bool = False,
        delay_reason: Optional[str] = None
    ) -> TrackingEvent:
        shipment = db.query(Shipment).filter(Shipment.shipment_id == shipment_id).first()
        if not shipment:
            raise ValueError(f"Shipment {shipment_id} not found.")

        current_status = shipment.shipment_status
        allowed = ALLOWED_TRANSITIONS.get(current_status, set())
        
        # Check transition validity
        if target_status not in allowed and target_status != current_status:
            raise ValueError(
                f"Invalid lifecycle transition from {current_status} to {target_status}. "
                f"Allowed transitions: {[s.value for s in allowed]}"
            )

        now_dt = event_time or datetime.now(timezone.utc)
        event_id = f"TRK-{shipment_id[-6:]}-{int(now_dt.timestamp()*1000)%1000000:06d}"

        event = TrackingEvent(
            event_id=event_id,
            shipment_id=shipment_id,
            event_status=target_status,
            location=location,
            description=description,
            event_timestamp=now_dt,
            is_delayed=is_delayed,
            delay_reason=delay_reason,
            created_at=datetime.now(timezone.utc)
        )
        db.add(event)

        # Update shipment status
        shipment.shipment_status = target_status
        shipment.updated_at = datetime.now(timezone.utc)

        if target_status == ShipmentStatus.DISPATCHED and not shipment.actual_dispatch_date:
            shipment.actual_dispatch_date = now_dt
        elif target_status == ShipmentStatus.DELIVERED and not shipment.actual_delivery_date:
            shipment.actual_delivery_date = now_dt

        # Rollup to order
        cls.rollup_order_status(db, shipment.order_id)

        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def rollup_order_status(db: Session, order_id: str) -> OrderStatus:
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            return OrderStatus.CREATED

        shipments = db.query(Shipment).filter(Shipment.order_id == order_id).all()
        if not shipments:
            return order.order_status

        statuses = [s.shipment_status for s in shipments]
        
        # Split shipment rule: marked DELIVERED only if ALL shipments are DELIVERED
        if all(s == ShipmentStatus.DELIVERED for s in statuses):
            new_status = OrderStatus.DELIVERED
            if not order.actual_delivery_date:
                latest_deliv = max((s.actual_delivery_date for s in shipments if s.actual_delivery_date), default=datetime.now(timezone.utc))
                order.actual_delivery_date = latest_deliv
        elif any(s == ShipmentStatus.DELIVERED for s in statuses):
            new_status = OrderStatus.PARTIALLY_DELIVERED
        elif any(s in (ShipmentStatus.DISPATCHED, ShipmentStatus.IN_TRANSIT, ShipmentStatus.OUT_FOR_DELIVERY) for s in statuses):
            new_status = OrderStatus.SHIPPED
        elif any(s in (ShipmentStatus.PICKING, ShipmentStatus.PACKED, ShipmentStatus.READY_FOR_DISPATCH) for s in statuses):
            new_status = OrderStatus.PROCESSING
        elif any(s == ShipmentStatus.INVENTORY_RESERVED for s in statuses):
            new_status = OrderStatus.ALLOCATED
        else:
            new_status = order.order_status

        order.order_status = new_status
        order.updated_at = datetime.now(timezone.utc)
        db.commit()
        return new_status

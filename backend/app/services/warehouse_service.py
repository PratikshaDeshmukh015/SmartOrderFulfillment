from typing import List, Optional, Dict, Any
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from backend.app.models.entities import FulfillmentNode, WarehouseCapacity, WarehouseCalendar

class WarehouseService:
    @staticmethod
    def get_all_nodes(db: Session, active_only: bool = True) -> List[Dict[str, Any]]:
        query = db.query(FulfillmentNode)
        if active_only:
            query = query.filter(FulfillmentNode.is_active == True)
        nodes = query.all()
        return [{
            "node_id": n.node_id,
            "node_name": n.node_name,
            "node_type": n.node_type.value if hasattr(n.node_type, "value") else str(n.node_type),
            "address": n.address,
            "city": n.city,
            "state": n.state,
            "zip_code": n.zip_code,
            "latitude": n.latitude,
            "longitude": n.longitude,
            "daily_order_capacity": n.daily_order_capacity,
            "daily_unit_capacity": n.daily_unit_capacity,
            "processing_cutoff_time": n.processing_cutoff_time,
            "operating_hours_start": n.operating_hours_start,
            "operating_hours_end": n.operating_hours_end,
            "weekend_operations": n.weekend_operations,
            "is_active": n.is_active
        } for n in nodes]

    @staticmethod
    def get_node_capacity(db: Session, node_id: str, target_date: Optional[date] = None) -> List[Dict[str, Any]]:
        query = db.query(WarehouseCapacity).filter(WarehouseCapacity.node_id == node_id)
        if target_date:
            query = query.filter(WarehouseCapacity.date == target_date)
        records = query.order_by(WarehouseCapacity.date.desc()).limit(30).all()
        return [{
            "capacity_id": c.capacity_id,
            "node_id": c.node_id,
            "date": c.date.isoformat(),
            "max_orders": c.max_orders,
            "utilized_orders": c.utilized_orders,
            "max_units": c.max_units,
            "utilized_units": c.utilized_units,
            "order_utilization_pct": round((c.utilized_orders / max(1, c.max_orders)) * 100, 2),
            "unit_utilization_pct": round((c.utilized_units / max(1, c.max_units)) * 100, 2)
        } for c in records]

    @staticmethod
    def is_node_operating(db: Session, node_id: str, check_date: date) -> bool:
        # Check calendar
        cal = db.query(WarehouseCalendar).filter(
            WarehouseCalendar.node_id == node_id,
            WarehouseCalendar.date == check_date
        ).first()
        if cal:
            return cal.is_operating

        # Default fallback: check weekend rule
        node = db.query(FulfillmentNode).filter(FulfillmentNode.node_id == node_id).first()
        if not node:
            return False
        if check_date.weekday() >= 5 and not node.weekend_operations:
            return False
        return True

    @staticmethod
    def has_available_capacity(db: Session, node_id: str, check_date: date, required_units: int = 1) -> bool:
        cap = db.query(WarehouseCapacity).filter(
            WarehouseCapacity.node_id == node_id,
            WarehouseCapacity.date == check_date
        ).first()
        if not cap:
            # If no explicit capacity record, assume default headroom
            return True
        return (cap.utilized_orders < cap.max_orders) and ((cap.utilized_units + required_units) <= cap.max_units)

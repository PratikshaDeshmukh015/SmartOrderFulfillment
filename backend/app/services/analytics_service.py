from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from backend.app.models.entities import (
    Order, Shipment, OrderLine, Inventory, WarehouseCapacity, Carrier, FulfillmentException, OptimizationDecision
)
from backend.app.models.enums import OrderStatus, ShipmentStatus, ExceptionResolutionStatus

class AnalyticsService:
    @staticmethod
    def get_overview_metrics(db: Session) -> Dict[str, Any]:
        total_orders = db.query(func.count(Order.order_id)).scalar() or 0
        fulfilled_orders = db.query(func.count(Order.order_id)).filter(Order.order_status == OrderStatus.DELIVERED).scalar() or 0
        pending_orders = db.query(func.count(Order.order_id)).filter(
            Order.order_status.in_([OrderStatus.CREATED, OrderStatus.ALLOCATED, OrderStatus.PROCESSING, OrderStatus.SHIPPED, OrderStatus.PARTIALLY_DELIVERED])
        ).scalar() or 0
        split_orders = db.query(func.count(Order.order_id)).filter(Order.is_split == True).scalar() or 0

        # Shipments
        total_shipments = db.query(func.count(Shipment.shipment_id)).scalar() or 0
        delivered_shipments = db.query(Shipment).filter(Shipment.shipment_status == ShipmentStatus.DELIVERED).all()
        
        on_time_count = 0
        total_delivery_hours = 0.0
        for s in delivered_shipments:
            if s.actual_delivery_date and s.promised_delivery_date:
                if s.actual_delivery_date <= s.promised_delivery_date:
                    on_time_count += 1
            if s.actual_delivery_date and s.scheduled_dispatch_date:
                diff_hours = (s.actual_delivery_date - s.scheduled_dispatch_date).total_seconds() / 3600.0
                total_delivery_hours += max(0.0, diff_hours)

        on_time_pct = round((on_time_count / max(1, len(delivered_shipments))) * 100, 2)
        avg_delivery_days = round((total_delivery_hours / max(1, len(delivered_shipments))) / 24.0, 2)
        fulfillment_success_rate = round((fulfilled_orders / max(1, total_orders)) * 100, 2)
        split_shipment_pct = round((split_orders / max(1, total_orders)) * 100, 2)

        # Average Shipping Cost
        avg_cost = db.query(func.avg(Shipment.shipping_cost)).scalar() or 0.0
        
        # Exceptions
        active_exceptions = db.query(func.count(FulfillmentException.exception_id)).filter(
            FulfillmentException.resolution_status != ExceptionResolutionStatus.RESOLVED
        ).scalar() or 0
        total_exceptions = db.query(func.count(FulfillmentException.exception_id)).scalar() or 0

        # Total Inventory
        total_inv_units = db.query(func.sum(Inventory.available_quantity + Inventory.reserved_quantity)).scalar() or 0

        return {
            "total_orders": total_orders,
            "fulfilled_orders": fulfilled_orders,
            "pending_orders": pending_orders,
            "delayed_orders": max(0, len(delivered_shipments) - on_time_count),
            "on_time_delivery_pct": on_time_pct,
            "avg_delivery_days": avg_delivery_days,
            "split_shipment_pct": split_shipment_pct,
            "fulfillment_success_rate": fulfillment_success_rate,
            "active_exceptions": active_exceptions,
            "total_exceptions": total_exceptions,
            "exception_rate": round((total_exceptions / max(1, total_orders)) * 100, 2),
            "total_inventory_units": int(total_inv_units),
            "avg_shipping_cost": round(float(avg_cost), 2)
        }

    @staticmethod
    def get_carrier_scorecard(db: Session) -> List[Dict[str, Any]]:
        carriers = db.query(Carrier).all()
        result = []
        for c in carriers:
            shipments = db.query(Shipment).filter(Shipment.carrier_id == c.carrier_id).all()
            total_s = len(shipments)
            deliv_s = [s for s in shipments if s.shipment_status == ShipmentStatus.DELIVERED]
            
            on_time = 0
            transit_sum = 0.0
            cost_sum = 0.0

            for s in deliv_s:
                if s.actual_delivery_date and s.promised_delivery_date and s.actual_delivery_date <= s.promised_delivery_date:
                    on_time += 1
                if s.actual_delivery_date and s.actual_dispatch_date:
                    days = (s.actual_delivery_date - s.actual_dispatch_date).total_seconds() / 86400.0
                    transit_sum += max(0.5, days)
                cost_sum += s.shipping_cost

            result.append({
                "carrier_id": c.carrier_id,
                "carrier_name": c.carrier_name,
                "total_shipments": total_s,
                "delivered_shipments": len(deliv_s),
                "on_time_shipments": on_time,
                "on_time_pct": round((on_time / max(1, len(deliv_s))) * 100, 2),
                "avg_transit_days": round(transit_sum / max(1, len(deliv_s)), 2),
                "avg_cost": round(cost_sum / max(1, len(deliv_s)), 2),
                "reliability_score": round(c.reliability_score * 100, 1)
            })
        return result

    @staticmethod
    def get_warehouse_utilization_summary(db: Session) -> List[Dict[str, Any]]:
        capacities = (
            db.query(
                WarehouseCapacity.node_id,
                func.avg(WarehouseCapacity.max_orders).label("avg_max_orders"),
                func.avg(WarehouseCapacity.utilized_orders).label("avg_utilized_orders"),
                func.avg(WarehouseCapacity.max_units).label("avg_max_units"),
                func.avg(WarehouseCapacity.utilized_units).label("avg_utilized_units")
            )
            .group_by(WarehouseCapacity.node_id)
            .all()
        )
        result = []
        for row in capacities:
            util_order_pct = round((row.avg_utilized_orders / max(1.0, row.avg_max_orders)) * 100, 2)
            util_unit_pct = round((row.avg_utilized_units / max(1.0, row.avg_max_units)) * 100, 2)
            shipped_units = db.query(func.sum(Shipment.total_weight_kg)).filter(Shipment.node_id == row.node_id).scalar() or 0.0
            order_count = db.query(func.count(Shipment.shipment_id)).filter(Shipment.node_id == row.node_id).scalar() or 0

            result.append({
                "node_id": row.node_id,
                "avg_max_orders": int(row.avg_max_orders),
                "avg_utilized_orders": int(row.avg_utilized_orders),
                "order_utilization_pct": util_order_pct,
                "unit_utilization_pct": util_unit_pct,
                "total_shipments_assigned": order_count
            })
        return result

import json
from typing import Dict, Any, Optional
from datetime import datetime, date, timedelta, timezone
from sqlalchemy.orm import Session
from backend.app.models.entities import DeliveryPromise, Order, FulfillmentNode, Carrier, WarehouseCalendar, CarrierCalendar
from backend.app.services.warehouse_service import WarehouseService
from backend.app.services.carrier_service import CarrierService

class DeliveryPromiseEngine:
    @staticmethod
    def calculate_promised_date(
        db: Session,
        order_id: str,
        node_id: str,
        carrier_id: str,
        transit_days: int,
        placed_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            raise ValueError(f"Order {order_id} not found.")

        order_dt = placed_at or order.placed_at or datetime.now(timezone.utc)
        node = db.query(FulfillmentNode).filter(FulfillmentNode.node_id == node_id).first()
        if not node:
            raise ValueError(f"FulfillmentNode {node_id} not found.")

        # 1. Processing Cutoff Check
        cutoff_parts = node.processing_cutoff_time.split(":")
        cutoff_hour = int(cutoff_parts[0])
        cutoff_minute = int(cutoff_parts[1]) if len(cutoff_parts) > 1 else 0
        cutoff_met = (order_dt.hour < cutoff_hour) or (order_dt.hour == cutoff_hour and order_dt.minute <= cutoff_minute)

        # 2. Determine Processing / Dispatch Date
        curr_date = order_dt.date()
        if not cutoff_met:
            curr_date += timedelta(days=1)

        # Advance curr_date if warehouse is closed on that date
        max_lookahead = 14
        while max_lookahead > 0:
            if WarehouseService.is_node_operating(db, node_id, curr_date):
                # Also check carrier pickup operating on dispatch day
                if CarrierService.is_carrier_operating(db, carrier_id, curr_date):
                    break
            curr_date += timedelta(days=1)
            max_lookahead -= 1

        dispatch_dt = datetime.combine(curr_date, datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=17)

        # 3. Transit Days with Carrier Calendar Skipping
        transit_remaining = transit_days
        delivery_date = curr_date

        while transit_remaining > 0:
            delivery_date += timedelta(days=1)
            # Check if carrier delivers on delivery_date
            if CarrierService.is_carrier_operating(db, carrier_id, delivery_date):
                transit_remaining -= 1

        promised_delivery_dt = datetime.combine(delivery_date, datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=15)

        confidence_score = 0.98 if cutoff_met else 0.92

        factors = {
            "order_placed_at": order_dt.isoformat(),
            "cutoff_time": node.processing_cutoff_time,
            "cutoff_met": cutoff_met,
            "dispatch_date": dispatch_dt.isoformat(),
            "transit_days": transit_days,
            "promised_delivery_date": promised_delivery_dt.isoformat(),
            "confidence_score": confidence_score
        }

        reason = (
            f"Promised delivery on {promised_delivery_dt.strftime('%d %B %Y')} calculated from "
            f"dispatch on {dispatch_dt.strftime('%d %B %Y')}. "
            f"{'Order received prior to cutoff' if cutoff_met else 'Cutoff passed; dispatched next operating day'} "
            f"with {transit_days} transit days via carrier {carrier_id}."
        )

        return {
            "dispatch_datetime": dispatch_dt,
            "promised_delivery_datetime": promised_delivery_dt,
            "confidence_score": confidence_score,
            "calculation_factors": factors,
            "reason": reason
        }

    @classmethod
    def record_or_revise_promise(
        cls,
        db: Session,
        order_id: str,
        shipment_id: Optional[str],
        node_id: str,
        carrier_id: str,
        transit_days: int
    ) -> DeliveryPromise:
        calc = cls.calculate_promised_date(db, order_id, node_id, carrier_id, transit_days)
        
        # Check existing active promises
        existing = db.query(DeliveryPromise).filter(
            DeliveryPromise.order_id == order_id,
            DeliveryPromise.is_active == True
        ).all()

        version = 1
        original_date = calc["promised_delivery_datetime"]

        if existing:
            # Mark previous inactive
            for p in existing:
                p.is_active = False
            version = len(existing) + 1
            original_date = existing[0].original_promised_date

        prom_id = f"PROM-ORD-{order_id[-6:]}-{version:02d}"
        new_promise = DeliveryPromise(
            promise_id=prom_id,
            order_id=order_id,
            shipment_id=shipment_id,
            original_promised_date=original_date,
            revised_promised_date=calc["promised_delivery_datetime"] if version > 1 else None,
            promise_version=version,
            is_active=True,
            confidence_score=calc["confidence_score"],
            calculation_factors=json.dumps(calc["calculation_factors"]),
            reason=calc["reason"],
            created_at=datetime.now(timezone.utc)
        )
        db.add(new_promise)

        # Update order promise
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if order:
            order.promised_delivery_date = calc["promised_delivery_datetime"]

        db.commit()
        db.refresh(new_promise)
        return new_promise

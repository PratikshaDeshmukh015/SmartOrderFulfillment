from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from backend.app.database import get_db
from backend.app.models.entities import DeliveryPromise, Order
from backend.app.schemas.schemas import DeliveryPromiseResponse
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="", tags=["Delivery Promises"])

@router.get("/promises/{order_id}", response_model=List[DeliveryPromiseResponse])
def get_order_promises(order_id: str, db: Session = Depends(get_db)):
    promises = (
        db.query(DeliveryPromise)
        .filter(DeliveryPromise.order_id == order_id)
        .order_by(DeliveryPromise.promise_version.desc())
        .all()
    )
    if not promises:
        raise HTTPException(status_code=404, detail=f"No delivery promises found for order {order_id}.")
    
    result = []
    for p in promises:
        factors = None
        if p.calculation_factors:
            try:
                factors = json.loads(p.calculation_factors)
            except Exception:
                pass
        result.append({
            "promise_id": p.promise_id,
            "order_id": p.order_id,
            "shipment_id": p.shipment_id,
            "original_promised_date": p.original_promised_date,
            "revised_promised_date": p.revised_promised_date,
            "promise_version": p.promise_version,
            "is_active": p.is_active,
            "confidence_score": p.confidence_score,
            "calculation_factors": factors,
            "reason": p.reason,
            "created_at": p.created_at
        })
    return result

@router.get("/delivery/performance")
def get_delivery_performance(db: Session = Depends(get_db)):
    overview = AnalyticsService.get_overview_metrics(db)
    return {
        "on_time_delivery_pct": overview["on_time_delivery_pct"],
        "avg_delivery_days": overview["avg_delivery_days"],
        "delayed_orders": overview["delayed_orders"],
        "fulfillment_success_rate": overview["fulfillment_success_rate"]
    }

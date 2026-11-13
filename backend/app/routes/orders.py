from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from backend.app.database import get_db
from backend.app.models.entities import Order, OrderLine, SKU
from backend.app.models.enums import OrderStatus, OrderPriority
from backend.app.schemas.schemas import OrderCreate, OrderResponse, OrderStatusResponse
from backend.app.services.shipment_service import ShipmentService

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("", response_model=OrderResponse, status_code=201)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    # Deterministic or timestamped order ID
    count = db.query(Order).count() + 1
    order_id = f"ORD-2026-{count:06d}"

    placed_dt = datetime.now(timezone.utc)
    total_amount = 0.0
    lines_to_add = []

    for idx, l in enumerate(payload.lines, 1):
        sku = db.query(SKU).filter(SKU.sku_id == l.sku_id).first()
        if not sku:
            raise HTTPException(status_code=404, detail=f"SKU {l.sku_id} not found.")
        unit_price = l.unit_price or sku.unit_price
        line_total = round(l.quantity * unit_price, 2)
        total_amount += line_total

        line_id = f"{order_id}-{idx:02d}"
        lines_to_add.append(OrderLine(
            order_line_id=line_id,
            order_id=order_id,
            sku_id=l.sku_id,
            quantity=l.quantity,
            unit_price=unit_price,
            line_total=line_total,
            allocated_quantity=0,
            created_at=placed_dt,
            updated_at=placed_dt
        ))

    order = Order(
        order_id=order_id,
        customer_id=payload.customer_id,
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        destination_address=payload.destination_address,
        destination_city=payload.destination_city,
        destination_state=payload.destination_state,
        destination_zip=payload.destination_zip,
        destination_zone=payload.destination_zone,
        order_priority=payload.order_priority,
        order_status=OrderStatus.CREATED,
        total_amount=round(total_amount, 2),
        shipping_fee=14.50,
        placed_at=placed_dt,
        is_split=False,
        created_at=placed_dt,
        updated_at=placed_dt
    )

    db.add(order)
    db.flush()
    for l_obj in lines_to_add:
        db.add(l_obj)
    db.commit()
    db.refresh(order)
    return order

@router.get("", response_model=List[OrderResponse])
def list_orders(
    status: Optional[OrderStatus] = None,
    priority: Optional[OrderPriority] = None,
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    safe_limit = limit if isinstance(limit, int) else (getattr(limit, "default", 50) or 50)
    safe_offset = offset if isinstance(offset, int) else (getattr(offset, "default", 0) or 0)
    query = db.query(Order)
    if status:
        query = query.filter(Order.order_status == status)
    if priority:
        query = query.filter(Order.order_priority == priority)
    if search:
        query = query.filter(
            (Order.order_id.ilike(f"%{search}%")) |
            (Order.customer_name.ilike(f"%{search}%")) |
            (Order.destination_city.ilike(f"%{search}%"))
        )
    return query.order_by(Order.placed_at.desc()).offset(int(safe_offset)).limit(int(safe_limit)).all()

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found.")
    return order

@router.get("/{order_id}/status", response_model=OrderStatusResponse)
def get_order_status(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found.")

    shipments = ShipmentService.get_shipments(db, order_id=order_id)
    total_lines = len(order.lines)
    fulfilled_lines = sum(1 for l in order.lines if l.allocated_quantity >= l.quantity)

    return {
        "order_id": order.order_id,
        "order_status": order.order_status,
        "is_split": order.is_split,
        "total_lines": total_lines,
        "fulfilled_lines": fulfilled_lines,
        "shipment_count": len(shipments),
        "shipments": shipments
    }

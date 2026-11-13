from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.database import get_db
from backend.app.models.enums import ShipmentStatus
from backend.app.schemas.schemas import ShipmentResponse, TrackingEventResponse, TrackingEventCreate
from backend.app.services.shipment_service import ShipmentService

router = APIRouter(prefix="/shipments", tags=["Shipments"])

@router.get("", response_model=List[ShipmentResponse])
def list_shipments(
    order_id: Optional[str] = None,
    node_id: Optional[str] = None,
    status: Optional[ShipmentStatus] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    return ShipmentService.get_shipments(
        db, order_id=order_id, node_id=node_id, status=status.value if status else None,
        limit=limit, offset=offset
    )

@router.get("/{shipment_id}", response_model=ShipmentResponse)
def get_shipment(shipment_id: str, db: Session = Depends(get_db)):
    shp = ShipmentService.get_shipment_by_id(db, shipment_id)
    if not shp:
        raise HTTPException(status_code=404, detail=f"Shipment {shipment_id} not found.")
    return shp

@router.get("/{shipment_id}/tracking", response_model=List[TrackingEventResponse])
def get_shipment_tracking(shipment_id: str, db: Session = Depends(get_db)):
    shp = ShipmentService.get_shipment_by_id(db, shipment_id)
    if not shp:
        raise HTTPException(status_code=404, detail=f"Shipment {shipment_id} not found.")
    return shp.get("tracking_events", [])

@router.post("/{shipment_id}/events", response_model=TrackingEventResponse, status_code=201)
def add_tracking_event(
    shipment_id: str,
    event_payload: TrackingEventCreate,
    db: Session = Depends(get_db)
):
    try:
        ev = ShipmentService.add_tracking_event(
            db,
            shipment_id=shipment_id,
            target_status=event_payload.event_status,
            location=event_payload.location,
            description=event_payload.description,
            event_time=event_payload.event_timestamp,
            is_delayed=event_payload.is_delayed,
            delay_reason=event_payload.delay_reason
        )
        return ev
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

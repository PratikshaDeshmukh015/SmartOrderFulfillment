from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from backend.app.database import get_db
from backend.app.schemas.schemas import FulfillmentNodeResponse, WarehouseCapacityResponse
from backend.app.services.warehouse_service import WarehouseService

router = APIRouter(prefix="/nodes", tags=["Fulfillment Nodes"])

@router.get("", response_model=List[FulfillmentNodeResponse])
def list_nodes(active_only: bool = True, db: Session = Depends(get_db)):
    return WarehouseService.get_all_nodes(db, active_only=active_only)

@router.get("/{node_id}/capacity", response_model=List[WarehouseCapacityResponse])
def get_node_capacity(
    node_id: str,
    target_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    caps = WarehouseService.get_node_capacity(db, node_id=node_id, target_date=target_date)
    if not caps:
        raise HTTPException(status_code=404, detail=f"No capacity records found for node {node_id}.")
    return caps

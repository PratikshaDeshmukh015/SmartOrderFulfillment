from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.database import get_db
from backend.app.schemas.schemas import InventoryResponse
from backend.app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("", response_model=List[InventoryResponse])
def list_inventory(
    sku_id: Optional[str] = None,
    node_id: Optional[str] = None,
    low_stock_only: bool = False,
    db: Session = Depends(get_db)
):
    return InventoryService.get_inventory_summary(
        db, sku_id=sku_id, node_id=node_id, low_stock_only=low_stock_only
    )

@router.get("/{sku_id}")
def get_inventory_by_sku(sku_id: str, db: Session = Depends(get_db)):
    availability = InventoryService.get_sku_availability_by_node(db, sku_id)
    if not availability:
        raise HTTPException(status_code=404, detail=f"SKU {sku_id} has no inventory records.")
    return {
        "sku_id": sku_id,
        "total_available": sum(a["available_quantity"] for a in availability),
        "total_reserved": sum(a["reserved_quantity"] for a in availability),
        "warehouse_availability": availability
    }

@router.get("/node/{node_id}", response_model=List[InventoryResponse])
def get_inventory_by_node(node_id: str, db: Session = Depends(get_db)):
    items = InventoryService.get_inventory_summary(db, node_id=node_id)
    if not items:
        raise HTTPException(status_code=404, detail=f"Node {node_id} has no inventory records.")
    return items

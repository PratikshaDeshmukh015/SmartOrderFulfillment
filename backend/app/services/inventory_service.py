from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from backend.app.models.entities import Inventory, SKU, FulfillmentNode, Allocation
from backend.app.models.enums import AllocationStatus

class InventoryService:
    @staticmethod
    def get_inventory_summary(
        db: Session,
        sku_id: Optional[str] = None,
        node_id: Optional[str] = None,
        low_stock_only: bool = False
    ) -> List[Dict[str, Any]]:
        query = (
            db.query(
                Inventory,
                SKU.sku_name,
                SKU.category,
                FulfillmentNode.node_name,
                FulfillmentNode.city
            )
            .join(SKU, Inventory.sku_id == SKU.sku_id)
            .join(FulfillmentNode, Inventory.node_id == FulfillmentNode.node_id)
        )
        if sku_id:
            query = query.filter(Inventory.sku_id == sku_id)
        if node_id:
            query = query.filter(Inventory.node_id == node_id)
        if low_stock_only:
            query = query.filter(Inventory.available_quantity <= Inventory.reorder_threshold)

        results = query.all()
        output = []
        for inv, sku_name, category, node_name, city in results:
            output.append({
                "inventory_id": inv.inventory_id,
                "node_id": inv.node_id,
                "node_name": node_name,
                "city": city,
                "sku_id": inv.sku_id,
                "sku_name": sku_name,
                "category": category,
                "available_quantity": inv.available_quantity,
                "reserved_quantity": inv.reserved_quantity,
                "total_quantity": inv.available_quantity + inv.reserved_quantity,
                "reorder_threshold": inv.reorder_threshold,
                "safety_stock": inv.safety_stock,
                "is_low_stock": inv.available_quantity <= inv.reorder_threshold,
                "last_restocked_at": inv.last_restocked_at.isoformat() if inv.last_restocked_at else None
            })
        return output

    @staticmethod
    def get_sku_availability_by_node(db: Session, sku_id: str) -> List[Dict[str, Any]]:
        rows = (
            db.query(Inventory, FulfillmentNode)
            .join(FulfillmentNode, Inventory.node_id == FulfillmentNode.node_id)
            .filter(Inventory.sku_id == sku_id)
            .all()
        )
        return [{
            "node_id": node.node_id,
            "node_name": node.node_name,
            "city": node.city,
            "state": node.state,
            "available_quantity": inv.available_quantity,
            "reserved_quantity": inv.reserved_quantity
        } for inv, node in rows]

    @staticmethod
    def reserve_stock(
        db: Session,
        order_id: str,
        order_line_id: str,
        sku_id: str,
        node_id: str,
        quantity: int
    ) -> Allocation:
        inv = (
            db.query(Inventory)
            .filter(Inventory.node_id == node_id, Inventory.sku_id == sku_id)
            .with_for_update()
            .first()
        )
        if not inv or inv.available_quantity < quantity:
            raise ValueError(
                f"Insufficient inventory at node {node_id} for SKU {sku_id}: "
                f"requested={quantity}, available={inv.available_quantity if inv else 0}"
            )

        inv.available_quantity -= quantity
        inv.reserved_quantity += quantity
        inv.updated_at = datetime.now(timezone.utc)

        alc_id = f"ALC-{order_id[-6:]}-{int(datetime.now().timestamp()*1000)%1000000:06d}"
        allocation = Allocation(
            allocation_id=alc_id,
            order_id=order_id,
            order_line_id=order_line_id,
            node_id=node_id,
            sku_id=sku_id,
            allocated_quantity=quantity,
            allocation_status=AllocationStatus.RESERVED
        )
        db.add(allocation)
        db.commit()
        db.refresh(allocation)
        return allocation

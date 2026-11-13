from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from backend.app.models.entities import Inventory, FulfillmentNode, SKU

class OrderSplitAllocator:
    @staticmethod
    def evaluate_split_allocation(
        db: Session,
        order_lines: List[Dict[str, Any]], # list of {"sku_id": str, "quantity": int}
        candidate_nodes: List[Dict[str, Any]] # list of node dicts
    ) -> Dict[str, Any]:
        """
        Evaluate single warehouse fulfillment first.
        If no single warehouse satisfies all line items, find minimal split configuration.
        """
        node_inventory = {}
        for node in candidate_nodes:
            n_id = node["node_id"]
            node_inventory[n_id] = {}
            for line in order_lines:
                s_id = line["sku_id"]
                inv = db.query(Inventory).filter(
                    Inventory.node_id == n_id,
                    Inventory.sku_id == s_id
                ).first()
                node_inventory[n_id][s_id] = inv.available_quantity if inv else 0

        # 1. Single node satisfaction check
        single_capable = []
        for node in candidate_nodes:
            n_id = node["node_id"]
            can_fulfill_all = True
            for line in order_lines:
                if node_inventory[n_id].get(line["sku_id"], 0) < line["quantity"]:
                    can_fulfill_all = False
                    break
            if can_fulfill_all:
                single_capable.append(node)

        if single_capable:
            return {
                "can_fulfill": True,
                "is_split": False,
                "single_capable_nodes": single_capable,
                "split_plan": None
            }

        # 2. Split fulfillment search (minimize number of warehouses)
        # Check global network feasibility
        for line in order_lines:
            s_id = line["sku_id"]
            total_network_stock = sum(node_inventory[n["node_id"]].get(s_id, 0) for n in candidate_nodes)
            if total_network_stock < line["quantity"]:
                return {
                    "can_fulfill": False,
                    "is_split": False,
                    "single_capable_nodes": [],
                    "split_plan": None,
                    "failure_reason": f"INVENTORY_SHORTAGE: SKU {s_id} requires {line['quantity']} but total network stock is {total_network_stock}."
                }

        # Greedy set cover for split allocation
        remaining_lines = {l["sku_id"]: l["quantity"] for l in order_lines}
        split_plan = []

        # Sort candidate nodes by total available quantity of required SKUs
        sorted_nodes = sorted(
            candidate_nodes,
            key=lambda n: sum(node_inventory[n["node_id"]].get(s, 0) for s in remaining_lines),
            reverse=True
        )

        for node in sorted_nodes:
            n_id = node["node_id"]
            items_from_this_node = []
            for s_id, needed in list(remaining_lines.items()):
                avail = node_inventory[n_id].get(s_id, 0)
                if avail > 0:
                    allocated_qty = min(avail, needed)
                    items_from_this_node.append({
                        "sku_id": s_id,
                        "allocated_quantity": allocated_qty
                    })
                    remaining_lines[s_id] -= allocated_qty
                    if remaining_lines[s_id] <= 0:
                        del remaining_lines[s_id]

            if items_from_this_node:
                split_plan.append({
                    "node_id": n_id,
                    "node_name": node["node_name"],
                    "city": node["city"],
                    "items": items_from_this_node
                })

            if not remaining_lines:
                break

        if not remaining_lines:
            return {
                "can_fulfill": True,
                "is_split": True,
                "single_capable_nodes": [],
                "split_plan": split_plan
            }

        return {
            "can_fulfill": False,
            "is_split": True,
            "single_capable_nodes": [],
            "split_plan": None,
            "failure_reason": "NO_ELIGIBLE_COMBINATION: Cannot allocate all lines across available nodes."
        }

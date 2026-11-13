from typing import Dict, Any

class FulfillmentScorer:
    DEFAULT_WEIGHTS = {
        "inventory": 0.30,
        "speed": 0.25,
        "capacity": 0.15,
        "cost": 0.15,
        "reliability": 0.10,
        "risk": 0.05
    }

    @staticmethod
    def calculate_factor_scores(
        inventory_ratio: float,          # 0.0 to 1.0 (available / required)
        transit_days: int,               # 1 to 5+
        capacity_utilization_pct: float, # 0.0 to 100.0
        shipping_cost: float,            # in dollars (e.g. 10.0 to 50.0)
        carrier_reliability: float,      # 0.0 to 1.0 (e.g. 0.95)
        has_holiday_buffer: bool = True
    ) -> Dict[str, float]:
        # 1. Inventory availability (0 - 100)
        inv_score = min(100.0, max(0.0, inventory_ratio * 100.0))

        # 2. Delivery speed (1 day = 100, 2 days = 85, 3 days = 70, 4 days = 50, 5+ = 30)
        speed_map = {1: 100.0, 2: 85.0, 3: 70.0, 4: 50.0}
        speed_score = speed_map.get(transit_days, max(20.0, 100.0 - (transit_days * 18.0)))

        # 3. Warehouse capacity (Headroom: 100% minus utilization)
        cap_score = max(10.0, min(100.0, 100.0 - capacity_utilization_pct))

        # 4. Shipping cost: lower cost = higher score ($8 = 95, $40 = 20)
        cost_score = max(10.0, min(100.0, 100.0 - (shipping_cost / 45.0 * 80.0)))

        # 5. Carrier reliability (0.95 -> 95.0)
        rel_score = max(10.0, min(100.0, carrier_reliability * 100.0))

        # 6. Operational risk (buffer presence, weekend risk)
        risk_score = 90.0 if has_holiday_buffer else 55.0

        return {
            "inventory_availability": round(inv_score, 2),
            "delivery_speed": round(speed_score, 2),
            "warehouse_capacity": round(cap_score, 2),
            "shipping_cost": round(cost_score, 2),
            "carrier_reliability": round(rel_score, 2),
            "operational_risk": round(risk_score, 2)
        }

    @classmethod
    def compute_weighted_score(
        cls,
        factor_scores: Dict[str, float],
        custom_weights: Dict[str, float] = None
    ) -> float:
        w = custom_weights or cls.DEFAULT_WEIGHTS
        composite = (
            w.get("inventory", 0.30) * factor_scores["inventory_availability"] +
            w.get("speed", 0.25) * factor_scores["delivery_speed"] +
            w.get("capacity", 0.15) * factor_scores["warehouse_capacity"] +
            w.get("cost", 0.15) * factor_scores["shipping_cost"] +
            w.get("reliability", 0.10) * factor_scores["carrier_reliability"] +
            w.get("risk", 0.05) * factor_scores["operational_risk"]
        )
        return round(composite, 2)

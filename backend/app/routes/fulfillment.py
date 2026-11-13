from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from backend.app.database import get_db
from backend.app.models.entities import Order, OptimizationDecision
from backend.app.schemas.schemas import (
    OptimizationResultResponse, BaselineComparisonResponse, OptimizationWeights
)
from backend.app.algorithms.optimization import FulfillmentOptimizationEngine

router = APIRouter(prefix="/fulfillment", tags=["Fulfillment Optimization"])

@router.post("/optimize/{order_id}", response_model=OptimizationResultResponse)
def optimize_order(
    order_id: str,
    weights: Optional[OptimizationWeights] = None,
    db: Session = Depends(get_db)
):
    w_dict = weights.model_dump() if weights else None
    engine = FulfillmentOptimizationEngine(db, weights=w_dict)
    try:
        result = engine.optimize_order(order_id, persist_decision=True)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")

@router.get("/decision/{order_id}")
def get_decision(order_id: str, db: Session = Depends(get_db)):
    decision = (
        db.query(OptimizationDecision)
        .filter(OptimizationDecision.order_id == order_id)
        .order_by(OptimizationDecision.created_at.desc())
        .first()
    )
    if not decision:
        raise HTTPException(status_code=404, detail=f"No decision found for order {order_id}.")
    
    return {
        "decision_id": decision.decision_id,
        "order_id": decision.order_id,
        "strategy": decision.strategy,
        "selected_nodes": decision.selected_nodes,
        "candidate_scores": decision.candidate_scores,
        "weights_used": decision.weights_used,
        "total_cost": decision.total_cost,
        "estimated_delivery_days": decision.estimated_delivery_days,
        "decision_reason": decision.decision_reason,
        "execution_time_ms": decision.execution_time_ms,
        "is_split": decision.is_split,
        "created_at": decision.created_at.isoformat()
    }

@router.get("/options/{order_id}")
def get_options(order_id: str, db: Session = Depends(get_db)):
    engine = FulfillmentOptimizationEngine(db)
    try:
        result = engine.optimize_order(order_id, persist_decision=False)
        return {
            "order_id": order_id,
            "candidate_options": result.get("candidate_options", []),
            "weights_applied": result.get("weights_applied", {})
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/compare-baseline/{order_id}", response_model=BaselineComparisonResponse)
def compare_with_baseline(order_id: str, db: Session = Depends(get_db)):
    engine = FulfillmentOptimizationEngine(db)
    try:
        comparison = engine.compare_with_baseline(order_id)
        return comparison
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

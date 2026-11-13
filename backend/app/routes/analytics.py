from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from backend.app.database import get_db
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/overview")
def get_analytics_overview(db: Session = Depends(get_db)):
    return AnalyticsService.get_overview_metrics(db)

@router.get("/carriers")
def get_carrier_analytics(db: Session = Depends(get_db)):
    return AnalyticsService.get_carrier_scorecard(db)

@router.get("/fulfillment")
def get_fulfillment_analytics(db: Session = Depends(get_db)):
    return AnalyticsService.get_warehouse_utilization_summary(db)

@router.get("/delivery-performance")
def get_delivery_performance(db: Session = Depends(get_db)):
    overview = AnalyticsService.get_overview_metrics(db)
    carrier_data = AnalyticsService.get_carrier_scorecard(db)
    return {
        "overview": overview,
        "carriers": carrier_data
    }

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.models.entities import FulfillmentException, Order, Shipment
from backend.app.models.enums import ExceptionSeverity, ExceptionResolutionStatus

class ExceptionService:
    @staticmethod
    def list_exceptions(
        db: Session,
        severity: Optional[str] = None,
        issue_type: Optional[str] = None,
        resolution_status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        query = db.query(FulfillmentException)
        if severity:
            query = query.filter(FulfillmentException.severity == severity)
        if issue_type:
            query = query.filter(FulfillmentException.issue_type == issue_type)
        if resolution_status:
            query = query.filter(FulfillmentException.resolution_status == resolution_status)

        records = query.order_by(FulfillmentException.detection_timestamp.desc()).offset(offset).limit(limit).all()
        return [{
            "exception_id": e.exception_id,
            "order_id": e.order_id,
            "shipment_id": e.shipment_id,
            "issue_type": e.issue_type,
            "severity": e.severity.value if hasattr(e.severity, "value") else str(e.severity),
            "description": e.description,
            "detection_timestamp": e.detection_timestamp.isoformat() if e.detection_timestamp else None,
            "expected_behavior": e.expected_behavior,
            "resolution_status": e.resolution_status.value if hasattr(e.resolution_status, "value") else str(e.resolution_status),
            "resolution_notes": e.resolution_notes,
            "resolved_at": e.resolved_at.isoformat() if e.resolved_at else None,
            "resolved_by": e.resolved_by,
            "ground_truth_label": e.ground_truth_label
        } for e in records]

    @staticmethod
    def get_exception_by_id(db: Session, exception_id: str) -> Optional[Dict[str, Any]]:
        e = db.query(FulfillmentException).filter(FulfillmentException.exception_id == exception_id).first()
        if not e:
            return None
        return {
            "exception_id": e.exception_id,
            "order_id": e.order_id,
            "shipment_id": e.shipment_id,
            "issue_type": e.issue_type,
            "severity": e.severity.value if hasattr(e.severity, "value") else str(e.severity),
            "description": e.description,
            "detection_timestamp": e.detection_timestamp.isoformat() if e.detection_timestamp else None,
            "expected_behavior": e.expected_behavior,
            "resolution_status": e.resolution_status.value if hasattr(e.resolution_status, "value") else str(e.resolution_status),
            "resolution_notes": e.resolution_notes,
            "resolved_at": e.resolved_at.isoformat() if e.resolved_at else None,
            "resolved_by": e.resolved_by,
            "ground_truth_label": e.ground_truth_label
        }

    @staticmethod
    def resolve_exception(
        db: Session,
        exception_id: str,
        resolution_notes: str,
        resolved_by: str = "SupplyChainManager",
        status: ExceptionResolutionStatus = ExceptionResolutionStatus.RESOLVED
    ) -> FulfillmentException:
        e = db.query(FulfillmentException).filter(FulfillmentException.exception_id == exception_id).first()
        if not e:
            raise ValueError(f"Exception {exception_id} not found.")

        now_dt = datetime.now(timezone.utc)
        e.resolution_status = status
        e.resolution_notes = resolution_notes
        e.resolved_at = now_dt
        e.resolved_by = resolved_by
        e.updated_at = now_dt

        # If order was in EXCEPTION status and now resolved, move order to ALLOCATED / PROCESSING
        if e.order_id and status == ExceptionResolutionStatus.RESOLVED:
            order = db.query(Order).filter(Order.order_id == e.order_id).first()
            if order and order.order_status.value == "EXCEPTION":
                order.order_status = "ALLOCATED"
                order.updated_at = now_dt

        db.commit()
        db.refresh(e)
        return e

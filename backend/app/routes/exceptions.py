from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.database import get_db
from backend.app.models.enums import ExceptionSeverity, ExceptionResolutionStatus
from backend.app.schemas.schemas import FulfillmentExceptionResponse, ExceptionResolveRequest
from backend.app.services.exception_service import ExceptionService

router = APIRouter(prefix="/exceptions", tags=["Exceptions"])

@router.get("", response_model=List[FulfillmentExceptionResponse])
def list_exceptions(
    severity: Optional[ExceptionSeverity] = None,
    issue_type: Optional[str] = None,
    resolution_status: Optional[ExceptionResolutionStatus] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    safe_limit = limit if isinstance(limit, int) else (getattr(limit, "default", 50) or 50)
    safe_offset = offset if isinstance(offset, int) else (getattr(offset, "default", 0) or 0)
    return ExceptionService.list_exceptions(
        db,
        severity=severity.value if severity else None,
        issue_type=issue_type,
        resolution_status=resolution_status.value if resolution_status else None,
        limit=int(safe_limit),
        offset=int(safe_offset)
    )

@router.get("/{exception_id}", response_model=FulfillmentExceptionResponse)
def get_exception(exception_id: str, db: Session = Depends(get_db)):
    exc = ExceptionService.get_exception_by_id(db, exception_id)
    if not exc:
        raise HTTPException(status_code=404, detail=f"Exception {exception_id} not found.")
    return exc

@router.patch("/{exception_id}/resolve", response_model=FulfillmentExceptionResponse)
def resolve_exception(
    exception_id: str,
    payload: ExceptionResolveRequest,
    db: Session = Depends(get_db)
):
    try:
        resolved = ExceptionService.resolve_exception(
            db,
            exception_id=exception_id,
            resolution_notes=payload.resolution_notes,
            resolved_by=payload.resolved_by,
            status=payload.resolution_status
        )
        return resolved
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

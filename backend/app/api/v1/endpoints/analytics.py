from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models
from app.api import deps
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/audit", response_model=Dict[str, Any])
async def generate_audit_report(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate a comprehensive account audit report.
    """
    service = AnalyticsService(db, current_user)
    report = await service.generate_audit_report()
    return report

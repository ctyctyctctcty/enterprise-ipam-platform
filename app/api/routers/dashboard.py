from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.dashboard import CapacityAlertRead, DashboardRecentActivityRead, DashboardSummaryRead
from app.services.dashboard import DashboardService

router = APIRouter()


@router.get("/summary", response_model=DashboardSummaryRead)
def get_dashboard_summary(
    site_id: str | None = None,
    db: Session = Depends(get_db),
) -> DashboardSummaryRead:
    return DashboardService(db).summary(site_id)


@router.get("/fixed-ip-alerts", response_model=list[CapacityAlertRead])
def get_fixed_ip_alerts(
    site_id: str | None = None,
    db: Session = Depends(get_db),
) -> list[CapacityAlertRead]:
    return DashboardService(db).fixed_ip_alerts(site_id)


@router.get("/dhcp-alerts", response_model=list[CapacityAlertRead])
def get_dhcp_alerts(
    site_id: str | None = None,
    db: Session = Depends(get_db),
) -> list[CapacityAlertRead]:
    return DashboardService(db).dhcp_alerts(site_id)


@router.get("/recent-activity", response_model=DashboardRecentActivityRead)
def get_recent_activity(
    site_id: str | None = None,
    db: Session = Depends(get_db),
) -> DashboardRecentActivityRead:
    return DashboardService(db).recent_activity(site_id)

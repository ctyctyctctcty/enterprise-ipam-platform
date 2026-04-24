from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.audit import AuditLogRead
from app.services.audit import AuditQueryService

router = APIRouter()


@router.get("/logs", response_model=list[AuditLogRead])
def list_audit_logs(db: Session = Depends(get_db)) -> list[AuditLogRead]:
    return AuditQueryService(db).list_logs()

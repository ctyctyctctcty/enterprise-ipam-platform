import json

from sqlalchemy.orm import Session

from app.core.enums import AuditAction, SourceType
from app.models.audit import AuditLog


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def log_event(
        self,
        *,
        action: AuditAction,
        entity_type: str,
        entity_id: str | None = None,
        actor_user_id: str | None = None,
        source_type: SourceType | None = None,
        source_reference: str | None = None,
        correlation_id: str | None = None,
        before: dict | None = None,
        after: dict | None = None,
        change_summary: str | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            correlation_id=correlation_id,
            source_type=source_type,
            source_reference=source_reference,
            before_json=json.dumps(before, default=str) if before else None,
            after_json=json.dumps(after, default=str) if after else None,
            change_summary=change_summary,
        )
        self.db.add(entry)
        self.db.flush()
        return entry


class AuditQueryService:
    def __init__(self, db: Session):
        self.db = db

    def list_logs(self) -> list[AuditLog]:
        return self.db.query(AuditLog).order_by(AuditLog.created_at.desc()).all()

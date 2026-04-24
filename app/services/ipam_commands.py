from sqlalchemy.orm import Session

from app.core.enums import AuditAction, SourceType
from app.models.ipam import IPAddress
from app.schemas.ipam import IPAddressCreate
from app.services.audit import AuditService


class IPAMCommandService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditService(db)

    def create_ip(self, payload: IPAddressCreate, actor_user_id: str | None = None) -> IPAddress:
        ip = IPAddress(**payload.model_dump())
        self.db.add(ip)
        self.db.flush()
        self.audit.log_event(
            action=AuditAction.CREATE,
            entity_type="IPAddress",
            entity_id=ip.id,
            actor_user_id=actor_user_id,
            source_type=SourceType.API,
            after={
                "address": ip.address,
                "status": ip.status,
                "primary_source_record_id": ip.primary_source_record_id,
            },
        )
        self.db.commit()
        self.db.refresh(ip)
        return ip


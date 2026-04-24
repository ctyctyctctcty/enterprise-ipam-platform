from app.core.enums import AuditAction, SourceType
from app.schemas.common import TimestampedSchema


class AuditLogRead(TimestampedSchema):
    actor_user_id: str | None = None
    action: AuditAction
    entity_type: str
    entity_id: str | None = None
    correlation_id: str | None = None
    source_type: SourceType | None = None
    source_reference: str | None = None
    before_json: str | None = None
    after_json: str | None = None
    change_summary: str | None = None

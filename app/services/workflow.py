from sqlalchemy.orm import Session

from app.core.enums import AuditAction
from app.models.intake import IntakeRequest
from app.services.audit import AuditService


class WorkflowService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditService(db)

    def get_pending_steps(self, request_id: str) -> list[dict]:
        request = self.db.query(IntakeRequest).filter(IntakeRequest.id == request_id).first()
        if not request:
            return []
        return [
            {
                "step_order": step.step_order,
                "name": step.name,
                "status": step.status,
                "approver_role": step.approver_role,
            }
            for step in request.approval_steps
        ]

    def trigger_external_workflow(self, request_id: str) -> dict:
        request = self.db.query(IntakeRequest).filter(IntakeRequest.id == request_id).first()
        if request:
            self.audit.log_event(
                action=AuditAction.TRANSITION,
                entity_type="IntakeRequest",
                entity_id=request.id,
                source_type=request.source_type,
                source_reference=request.external_request_reference,
                correlation_id=request.request_number,
                change_summary="Workflow trigger placeholder invoked.",
            )
            self.db.commit()
        return {
            "request_id": request_id,
            "status": "stubbed",
            "message": "Future Power Automate orchestration hook.",
        }

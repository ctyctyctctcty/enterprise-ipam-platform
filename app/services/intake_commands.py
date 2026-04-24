import json
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.enums import AuditAction, ApprovalStatus, IPAddressStatus, RequestStatus
from app.models.intake import ApprovalStep, IntakeRequest
from app.models.ipam import AllocationHistory, IPAddress
from app.models.ipam import InformationOutlet
from app.rules.ip_assignment import IPAssignmentRuleEngine
from app.schemas.intake import IntakeEvaluationRead
from app.schemas.intake import IntakeRequestSubmit
from app.services.audit import AuditService


class IntakeSubmissionService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditService(db)
        self.rule_engine = IPAssignmentRuleEngine(db)

    def submit_request(self, payload: IntakeRequestSubmit) -> IntakeRequest:
        outlet = None
        if payload.information_outlet_code:
            outlet = (
                self.db.query(InformationOutlet)
                .filter(InformationOutlet.code == payload.information_outlet_code)
                .first()
            )

        request = IntakeRequest(
            request_number=self._next_request_number(),
            status=RequestStatus.SUBMITTED,
            applicant_name=payload.applicant_name,
            applicant_email=payload.applicant_email,
            department=payload.department,
            requested_site_name=payload.site,
            requested_building_name=payload.building,
            requested_floor_name=payload.floor,
            requested_room_name=payload.room,
            room_id=outlet.room_id if outlet else None,
            information_outlet_id=outlet.id if outlet else None,
            information_outlet_code=payload.information_outlet_code,
            vlan_or_subnet=payload.vlan_or_subnet,
            hostname=payload.hostname,
            mac_address=payload.mac_address,
            device_model_name=payload.device_model_name,
            purpose=payload.purpose,
            required_by_date=payload.required_by_date,
            fixed_ip_required=payload.fixed_ip_required,
            note=payload.note,
            source_type=payload.source_type,
            source_channel=payload.source_type.value,
            external_request_reference=payload.source_reference,
            request_payload_json=json.dumps(payload.model_dump(mode="json"), default=str),
            submitted_at=datetime.now(timezone.utc),
            current_approval_order=1,
        )
        self.db.add(request)
        self.db.flush()
        self.db.add(
            ApprovalStep(
                intake_request_id=request.id,
                step_order=1,
                name="Initial Review",
                approver_role="reviewer",
            )
        )
        self.audit.log_event(
            action=AuditAction.SUBMIT,
            entity_type="IntakeRequest",
            entity_id=request.id,
            source_type=request.source_type,
            source_reference=request.external_request_reference,
            correlation_id=request.request_number,
            after={"request_number": request.request_number, "status": request.status},
            change_summary="Request submitted into backend system of record.",
        )
        evaluation = self.evaluate_request(request.id)
        request = self.db.query(IntakeRequest).filter(IntakeRequest.id == request.id).first()
        self.db.commit()
        self.db.refresh(request)
        return request

    @staticmethod
    def _next_request_number() -> str:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"REQ-{stamp}-{uuid4().hex[:6].upper()}"

    def evaluate_request(self, request_id: str) -> IntakeEvaluationRead | None:
        request = self.db.query(IntakeRequest).filter(IntakeRequest.id == request_id).first()
        if not request:
            return None

        result = self.rule_engine.evaluate_request(request)
        request.eligibility_outcome = result.outcome
        request.eligibility_summary = result.summary
        request.recommended_ip_address_id = result.recommended_ip.id if result.recommended_ip else None
        if result.outcome == "candidate":
            request.status = RequestStatus.UNDER_REVIEW
        elif result.outcome == "review_needed":
            request.status = RequestStatus.UNDER_REVIEW
        else:
            request.status = RequestStatus.REJECTED

        self.audit.log_event(
            action=AuditAction.TRANSITION,
            entity_type="IntakeRequest",
            entity_id=request.id,
            source_type=request.source_type,
            source_reference=request.external_request_reference,
            correlation_id=request.request_number,
            after={
                "eligibility_outcome": request.eligibility_outcome,
                "recommended_ip_address_id": request.recommended_ip_address_id,
                "status": request.status,
            },
            change_summary="Deterministic request eligibility evaluation executed.",
        )
        self.db.flush()
        return IntakeEvaluationRead(
            request_id=request.id,
            request_number=request.request_number,
            outcome=result.outcome,
            summary=result.summary,
            recommended_ip_address_id=request.recommended_ip_address_id,
        )

    def transition_request(
        self,
        request_id: str,
        target_status: RequestStatus,
        comment: str | None = None,
    ) -> IntakeRequest | None:
        request = self.db.query(IntakeRequest).filter(IntakeRequest.id == request_id).first()
        if not request:
            return None

        request.status = target_status
        if target_status == RequestStatus.ASSIGNED and request.recommended_ip_address_id:
            request.assigned_ip_address_id = request.recommended_ip_address_id
            ip = self.db.query(IPAddress).filter(IPAddress.id == request.recommended_ip_address_id).first()
            if ip:
                previous_status = ip.status.value
                ip.status = IPAddressStatus.ALLOCATED_CONFIRMED
                ip.hostname = request.hostname or ip.hostname
                ip.mac_address = request.mac_address or ip.mac_address
                self.db.add(
                    AllocationHistory(
                        ip_address_id=ip.id,
                        intake_request_id=request.id,
                        action="assigned_via_demo_review",
                        previous_status=previous_status,
                        new_status=ip.status.value,
                        new_owner=request.department,
                        source_type=request.source_type,
                        source_reference=request.external_request_reference,
                        notes="Assigned through demo transition endpoint.",
                    )
                )
        step = (
            self.db.query(ApprovalStep)
            .filter(ApprovalStep.intake_request_id == request.id, ApprovalStep.step_order == 1)
            .first()
        )
        if step:
            step.comment = comment
            if target_status == RequestStatus.APPROVED or target_status == RequestStatus.ASSIGNED:
                step.status = ApprovalStatus.APPROVED
            elif target_status == RequestStatus.REJECTED:
                step.status = ApprovalStatus.REJECTED

        self.audit.log_event(
            action=AuditAction.TRANSITION,
            entity_type="IntakeRequest",
            entity_id=request.id,
            source_type=request.source_type,
            source_reference=request.external_request_reference,
            correlation_id=request.request_number,
            after={"status": request.status, "assigned_ip_address_id": request.assigned_ip_address_id},
            change_summary=f"Request transitioned to {target_status}.",
        )
        self.db.commit()
        self.db.refresh(request)
        return request

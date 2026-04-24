from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field

from app.core.enums import ApprovalStatus, RequestStatus, SourceType
from app.schemas.common import TimestampedSchema


class IntakeRequestSubmit(BaseModel):
    applicant_name: str
    applicant_email: EmailStr
    department: str | None = None
    site: str | None = None
    building: str | None = None
    floor: str | None = None
    room: str | None = None
    information_outlet_code: str | None = None
    vlan_or_subnet: str | None = None
    hostname: str | None = None
    mac_address: str | None = None
    device_model_name: str | None = None
    purpose: str | None = None
    required_by_date: date | None = None
    fixed_ip_required: bool = True
    note: str | None = None
    source_type: SourceType = SourceType.API
    source_reference: str | None = None


class IntakeRequestCreate(IntakeRequestSubmit):
    pass


class ApprovalStepRead(TimestampedSchema):
    step_order: int
    name: str
    approver_role: str | None = None
    status: ApprovalStatus
    decision_at: datetime | None = None
    comment: str | None = None


class IntakeRequestRead(TimestampedSchema):
    request_number: str
    status: RequestStatus
    applicant_name: str
    applicant_email: EmailStr
    department: str | None = None
    requested_site_name: str | None = None
    requested_building_name: str | None = None
    requested_floor_name: str | None = None
    requested_room_name: str | None = None
    information_outlet_code: str | None = None
    vlan_or_subnet: str | None = None
    hostname: str | None = None
    mac_address: str | None = None
    device_model_name: str | None = None
    purpose: str | None = None
    required_by_date: date | None = None
    fixed_ip_required: bool
    note: str | None = None
    source_type: SourceType
    source_channel: str | None = None
    external_request_reference: str | None = None
    submitted_at: datetime | None = None
    assigned_ip_address_id: str | None = None
    recommended_ip_address_id: str | None = None
    eligibility_outcome: str | None = None
    eligibility_summary: str | None = None
    approval_steps: list[ApprovalStepRead] = Field(default_factory=list)


class IntakeRequestStatusRead(BaseModel):
    request_number: str
    status: RequestStatus
    current_approval_order: int | None = None
    assigned_ip_address_id: str | None = None
    recommended_ip_address_id: str | None = None
    eligibility_outcome: str | None = None
    eligibility_summary: str | None = None


class IntakeEvaluationRead(BaseModel):
    request_id: str
    request_number: str
    outcome: str
    summary: str
    recommended_ip_address_id: str | None = None


class IntakeTransitionRequest(BaseModel):
    target_status: RequestStatus
    comment: str | None = None

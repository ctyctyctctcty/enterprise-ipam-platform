from datetime import datetime

from pydantic import BaseModel, Field


class DashboardKPIRead(BaseModel):
    total_ips: int = 0
    allocated_fixed_ips: int = 0
    available_candidate_ips: int = 0
    conflict_suspected_ips: int = 0
    review_needed_requests: int = 0
    failed_import_jobs: int = 0


class CapacityAlertRead(BaseModel):
    id: str
    name: str
    scope_type: str
    site_name: str | None = None
    utilization_pct: float
    used_count: int
    capacity_total: int
    level: str
    metadata: dict = Field(default_factory=dict)


class DashboardConflictAlertRead(BaseModel):
    ip_id: str
    address: str
    hostname: str | None = None
    subnet_cidr: str | None = None
    confidence_score: float | None = None
    source_summary: str | None = None


class DashboardReviewRequestAlertRead(BaseModel):
    request_id: str
    request_number: str
    applicant_name: str
    department: str | None = None
    subnet: str | None = None
    eligibility_summary: str | None = None
    created_at: datetime


class DashboardImportAlertRead(BaseModel):
    job_id: str
    job_name: str
    status: str
    source_type: str
    source_reference: str | None = None
    summary: str | None = None
    error_message: str | None = None
    created_at: datetime


class DashboardTraceabilityAlertRead(BaseModel):
    ip_id: str
    address: str
    hostname: str | None = None
    subnet_cidr: str | None = None
    observation_count: int
    owner_department: str | None = None
    ownership_type: str | None = None
    trace_reference: str | None = None


class DashboardOperationalAlertsRead(BaseModel):
    conflict_ips: list[DashboardConflictAlertRead] = Field(default_factory=list)
    review_needed_requests: list[DashboardReviewRequestAlertRead] = Field(default_factory=list)
    import_jobs: list[DashboardImportAlertRead] = Field(default_factory=list)
    weak_traceability_ips: list[DashboardTraceabilityAlertRead] = Field(default_factory=list)


class DashboardSiteSummaryRead(BaseModel):
    site_id: str
    site_code: str
    site_name: str
    subnet_count: int = 0
    ip_count: int = 0
    request_count: int = 0
    conflict_count: int = 0


class DashboardSummaryRead(BaseModel):
    generated_at: datetime
    site_filter_id: str | None = None
    kpis: DashboardKPIRead
    operational_alerts: DashboardOperationalAlertsRead
    site_summary: list[DashboardSiteSummaryRead] = Field(default_factory=list)


class DashboardRecentRequestRead(BaseModel):
    request_id: str
    request_number: str
    applicant_name: str
    status: str
    eligibility_outcome: str | None = None
    created_at: datetime


class DashboardRecentAuditRead(BaseModel):
    audit_id: str
    action: str
    entity_type: str
    entity_id: str | None = None
    change_summary: str | None = None
    source_type: str | None = None
    created_at: datetime


class DashboardRecentImportJobRead(BaseModel):
    job_id: str
    job_name: str
    status: str
    source_type: str
    created_at: datetime
    failed_count: int | None = None


class DashboardRecentActivityRead(BaseModel):
    recent_requests: list[DashboardRecentRequestRead] = Field(default_factory=list)
    recent_audit_logs: list[DashboardRecentAuditRead] = Field(default_factory=list)
    recent_import_jobs: list[DashboardRecentImportJobRead] = Field(default_factory=list)

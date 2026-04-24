from __future__ import annotations

from datetime import datetime
from ipaddress import ip_address, ip_network

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.enums import IPAddressStatus, ImportJobStatus
from app.models.audit import AuditLog
from app.models.intake import IntakeRequest
from app.models.ipam import DhcpScope, IPAddress, Site, Subnet
from app.models.jobs import ImportJob
from app.schemas.dashboard import (
    CapacityAlertRead,
    DashboardConflictAlertRead,
    DashboardImportAlertRead,
    DashboardKPIRead,
    DashboardOperationalAlertsRead,
    DashboardRecentActivityRead,
    DashboardRecentAuditRead,
    DashboardRecentImportJobRead,
    DashboardRecentRequestRead,
    DashboardReviewRequestAlertRead,
    DashboardSiteSummaryRead,
    DashboardSummaryRead,
    DashboardTraceabilityAlertRead,
)


class DashboardService:
    WARNING_THRESHOLD = 70
    HIGH_THRESHOLD = 85
    CRITICAL_THRESHOLD = 95

    def __init__(self, db: Session):
        self.db = db

    def summary(self, site_id: str | None = None) -> DashboardSummaryRead:
        return DashboardSummaryRead(
            generated_at=datetime.now(),
            site_filter_id=site_id,
            kpis=self.kpis(site_id),
            operational_alerts=self.operational_alerts(site_id),
            site_summary=self.site_summary(),
        )

    def kpis(self, site_id: str | None = None) -> DashboardKPIRead:
        ip_query = self._ip_query(site_id)
        request_query = self._request_query(site_id)
        return DashboardKPIRead(
            total_ips=ip_query.count(),
            allocated_fixed_ips=ip_query.filter(
                IPAddress.status.in_(
                    [
                        IPAddressStatus.ALLOCATED_CONFIRMED,
                        IPAddressStatus.ALLOCATED_UNVERIFIED,
                    ]
                )
            ).count(),
            available_candidate_ips=ip_query.filter(
                IPAddress.status == IPAddressStatus.AVAILABLE_CANDIDATE
            ).count(),
            conflict_suspected_ips=ip_query.filter(
                IPAddress.status == IPAddressStatus.CONFLICT_SUSPECTED
            ).count(),
            review_needed_requests=request_query.filter(
                IntakeRequest.eligibility_outcome == "review_needed"
            ).count(),
            failed_import_jobs=self.db.query(ImportJob).filter(
                ImportJob.status == ImportJobStatus.FAILED
            ).count(),
        )

    def fixed_ip_alerts(self, site_id: str | None = None) -> list[CapacityAlertRead]:
        alerts: list[CapacityAlertRead] = []
        subnets = self._subnet_query(site_id).options(joinedload(Subnet.site)).all()
        for subnet in subnets:
            capacity_total = self._usable_capacity(subnet.cidr)
            if capacity_total <= 0:
                continue

            used_count = (
                self.db.query(func.count(IPAddress.id))
                .filter(
                    IPAddress.subnet_id == subnet.id,
                    IPAddress.status.in_(
                        [
                            IPAddressStatus.ALLOCATED_CONFIRMED,
                            IPAddressStatus.ALLOCATED_UNVERIFIED,
                            IPAddressStatus.RESERVED,
                        ]
                    ),
                )
                .scalar()
                or 0
            )
            utilization_pct = round((used_count / capacity_total) * 100, 1)
            level = self._alert_level(utilization_pct)
            if not level:
                continue

            alerts.append(
                CapacityAlertRead(
                    id=subnet.id,
                    name=subnet.cidr,
                    scope_type="fixed_ip_subnet",
                    site_name=subnet.site.name if subnet.site else None,
                    utilization_pct=utilization_pct,
                    used_count=used_count,
                    capacity_total=capacity_total,
                    level=level,
                    metadata={
                        "subnet_name": subnet.name,
                        "gateway": subnet.gateway,
                        "usage_type": subnet.usage_type,
                    },
                )
            )
        return sorted(alerts, key=lambda item: item.utilization_pct, reverse=True)

    def dhcp_alerts(self, site_id: str | None = None) -> list[CapacityAlertRead]:
        alerts: list[CapacityAlertRead] = []
        query = (
            self.db.query(DhcpScope)
            .options(joinedload(DhcpScope.subnet).joinedload(Subnet.site))
            .join(Subnet, DhcpScope.subnet_id == Subnet.id, isouter=True)
        )
        if site_id:
            query = query.filter(Subnet.site_id == site_id)

        for scope in query.order_by(DhcpScope.name.asc()).all():
            capacity_total = self._ip_range_size(scope.start_ip, scope.end_ip)
            if capacity_total <= 0:
                continue

            observed_used = self._dhcp_scope_observed_used(scope)
            utilization_pct = round((observed_used / capacity_total) * 100, 1)
            level = self._alert_level(utilization_pct)
            if not level:
                continue

            alerts.append(
                CapacityAlertRead(
                    id=scope.id,
                    name=scope.name,
                    scope_type="dhcp_scope",
                    site_name=scope.subnet.site.name if scope.subnet and scope.subnet.site else None,
                    utilization_pct=utilization_pct,
                    used_count=observed_used,
                    capacity_total=capacity_total,
                    level=level,
                    metadata={
                        "server_name": scope.server_name,
                        "start_ip": scope.start_ip,
                        "end_ip": scope.end_ip,
                        "subnet_cidr": scope.subnet.cidr if scope.subnet else None,
                    },
                )
            )
        return sorted(alerts, key=lambda item: item.utilization_pct, reverse=True)

    def operational_alerts(self, site_id: str | None = None) -> DashboardOperationalAlertsRead:
        conflict_ips = (
            self._ip_query(site_id)
            .options(joinedload(IPAddress.subnet))
            .filter(IPAddress.status == IPAddressStatus.CONFLICT_SUSPECTED)
            .order_by(IPAddress.updated_at.desc())
            .limit(10)
            .all()
        )
        review_requests = (
            self._request_query(site_id)
            .filter(IntakeRequest.eligibility_outcome == "review_needed")
            .order_by(IntakeRequest.created_at.desc())
            .limit(10)
            .all()
        )
        import_jobs = (
            self.db.query(ImportJob)
            .filter(ImportJob.status.in_([ImportJobStatus.FAILED, ImportJobStatus.PARTIAL, ImportJobStatus.PENDING]))
            .order_by(ImportJob.created_at.desc())
            .limit(10)
            .all()
        )
        weak_traceability = (
            self._ip_query(site_id)
            .options(joinedload(IPAddress.subnet), joinedload(IPAddress.source_observations))
            .join(IPAddress.source_observations)
            .filter(
                (IPAddress.owner_department.is_(None))
                | (IPAddress.ownership_type.is_(None))
                | (IPAddress.trace_reference.is_(None))
            )
            .order_by(IPAddress.updated_at.desc())
            .distinct()
            .limit(10)
            .all()
        )

        return DashboardOperationalAlertsRead(
            conflict_ips=[
                DashboardConflictAlertRead(
                    ip_id=item.id,
                    address=item.address,
                    hostname=item.hostname,
                    subnet_cidr=item.subnet.cidr if item.subnet else None,
                    confidence_score=item.confidence_score,
                    source_summary=item.source_summary,
                )
                for item in conflict_ips
            ],
            review_needed_requests=[
                DashboardReviewRequestAlertRead(
                    request_id=item.id,
                    request_number=item.request_number,
                    applicant_name=item.applicant_name,
                    department=item.department,
                    subnet=item.vlan_or_subnet or (item.subnet.cidr if item.subnet else None),
                    eligibility_summary=item.eligibility_summary,
                    created_at=item.created_at,
                )
                for item in review_requests
            ],
            import_jobs=[
                DashboardImportAlertRead(
                    job_id=item.id,
                    job_name=item.job_name,
                    status=item.status.value,
                    source_type=item.source_type.value,
                    source_reference=item.source_reference,
                    summary=item.summary,
                    error_message=item.error_message,
                    created_at=item.created_at,
                )
                for item in import_jobs
            ],
            weak_traceability_ips=[
                DashboardTraceabilityAlertRead(
                    ip_id=item.id,
                    address=item.address,
                    hostname=item.hostname,
                    subnet_cidr=item.subnet.cidr if item.subnet else None,
                    observation_count=len(item.source_observations),
                    owner_department=item.owner_department,
                    ownership_type=item.ownership_type,
                    trace_reference=item.trace_reference,
                )
                for item in weak_traceability
            ],
        )

    def recent_activity(self, site_id: str | None = None) -> DashboardRecentActivityRead:
        recent_requests = (
            self._request_query(site_id)
            .order_by(IntakeRequest.created_at.desc())
            .limit(8)
            .all()
        )
        recent_audits = self.db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(8).all()
        recent_jobs = self.db.query(ImportJob).order_by(ImportJob.created_at.desc()).limit(8).all()

        return DashboardRecentActivityRead(
            recent_requests=[
                DashboardRecentRequestRead(
                    request_id=item.id,
                    request_number=item.request_number,
                    applicant_name=item.applicant_name,
                    status=item.status.value,
                    eligibility_outcome=item.eligibility_outcome,
                    created_at=item.created_at,
                )
                for item in recent_requests
            ],
            recent_audit_logs=[
                DashboardRecentAuditRead(
                    audit_id=item.id,
                    action=item.action.value,
                    entity_type=item.entity_type,
                    entity_id=item.entity_id,
                    change_summary=item.change_summary,
                    source_type=item.source_type.value if item.source_type else None,
                    created_at=item.created_at,
                )
                for item in recent_audits
            ],
            recent_import_jobs=[
                DashboardRecentImportJobRead(
                    job_id=item.id,
                    job_name=item.job_name,
                    status=item.status.value,
                    source_type=item.source_type.value,
                    created_at=item.created_at,
                    failed_count=item.failed_count,
                )
                for item in recent_jobs
            ],
        )

    def site_summary(self) -> list[DashboardSiteSummaryRead]:
        sites = self.db.query(Site).options(joinedload(Site.subnets)).order_by(Site.name.asc()).all()
        rows: list[DashboardSiteSummaryRead] = []
        for site in sites:
            subnet_ids = [subnet.id for subnet in site.subnets]
            ip_count = (
                self.db.query(func.count(IPAddress.id)).filter(IPAddress.subnet_id.in_(subnet_ids)).scalar()
                if subnet_ids
                else 0
            )
            conflict_count = (
                self.db.query(func.count(IPAddress.id))
                .filter(
                    IPAddress.subnet_id.in_(subnet_ids),
                    IPAddress.status == IPAddressStatus.CONFLICT_SUSPECTED,
                )
                .scalar()
                if subnet_ids
                else 0
            )
            request_count = (
                self.db.query(func.count(IntakeRequest.id)).filter(IntakeRequest.site_id == site.id).scalar()
                or 0
            )
            rows.append(
                DashboardSiteSummaryRead(
                    site_id=site.id,
                    site_code=site.code,
                    site_name=site.name,
                    subnet_count=len(site.subnets),
                    ip_count=ip_count or 0,
                    request_count=request_count,
                    conflict_count=conflict_count or 0,
                )
            )
        return rows

    def _subnet_query(self, site_id: str | None = None):
        query = self.db.query(Subnet)
        if site_id:
            query = query.filter(Subnet.site_id == site_id)
        return query

    def _ip_query(self, site_id: str | None = None):
        query = self.db.query(IPAddress)
        if site_id:
            query = query.join(Subnet, IPAddress.subnet_id == Subnet.id).filter(Subnet.site_id == site_id)
        return query

    def _request_query(self, site_id: str | None = None):
        query = self.db.query(IntakeRequest).options(joinedload(IntakeRequest.subnet))
        if site_id:
            query = query.filter(IntakeRequest.site_id == site_id)
        return query

    def _usable_capacity(self, cidr: str | None) -> int:
        if not cidr:
            return 0
        network = ip_network(cidr, strict=False)
        if network.version == 4 and network.prefixlen <= 30:
            return max(network.num_addresses - 2, 0)
        return network.num_addresses

    def _ip_range_size(self, start_ip: str | None, end_ip: str | None) -> int:
        if not start_ip or not end_ip:
            return 0
        start = int(ip_address(start_ip))
        end = int(ip_address(end_ip))
        if end < start:
            return 0
        return (end - start) + 1

    def _dhcp_scope_observed_used(self, scope: DhcpScope) -> int:
        if not scope.start_ip or not scope.end_ip:
            return 0
        start = int(ip_address(scope.start_ip))
        end = int(ip_address(scope.end_ip))
        count = 0
        for address_value, status in (
            self.db.query(IPAddress.address, IPAddress.status)
            .filter(IPAddress.subnet_id == scope.subnet_id)
            .all()
        ):
            try:
                current = int(ip_address(address_value))
            except ValueError:
                continue
            if start <= current <= end and status == IPAddressStatus.DHCP_POOL:
                count += 1
        return count

    def _alert_level(self, utilization_pct: float) -> str | None:
        if utilization_pct > self.CRITICAL_THRESHOLD:
            return "critical"
        if utilization_pct > self.HIGH_THRESHOLD:
            return "high"
        if utilization_pct > self.WARNING_THRESHOLD:
            return "warning"
        return None

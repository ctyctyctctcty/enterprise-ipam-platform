from datetime import datetime, timedelta, timezone

from app.core.enums import (
    ApprovalStatus,
    AuditAction,
    IPAddressStatus,
    ImportJobStatus,
    RequestStatus,
    SourceType,
)
from app.models.audit import AuditLog
from app.models.intake import ApprovalStep, IntakeRequest
from app.models.ipam import (
    AllocationHistory,
    ArpObservation,
    DhcpScope,
    DnsRecord,
    IPAddress,
    IPAddressSourceObservation,
    SourceRecord,
)
from app.models.jobs import ImportJob
from scripts.seeds import SeedContext


def _get_or_create(db, model, defaults: dict | None = None, **filters):
    instance = db.query(model).filter_by(**filters).first()
    if instance:
        return instance
    payload = {**filters, **(defaults or {})}
    instance = model(**payload)
    db.add(instance)
    db.flush()
    return instance


def seed_operations(context: SeedContext, topology_index: dict[str, object], users_by_username: dict[str, object]) -> None:
    db = context.db
    now = datetime.now(timezone.utc)

    tokyo_fixed = topology_index["subnets"]["10.10.110.0/24"]
    tokyo_ops = topology_index["subnets"]["10.10.120.0/24"]
    osaka_fixed = topology_index["subnets"]["10.20.210.0/24"]

    dhcp_scope_specs = [
        ("Tokyo HQ DHCP Office", tokyo_fixed.id, "10.10.110.200", "10.10.110.239", "dhcp-tokyo-01"),
        ("Tokyo Ops DHCP", tokyo_ops.id, "10.10.120.180", "10.10.120.239", "dhcp-tokyo-02"),
        ("Osaka Branch DHCP", osaka_fixed.id, "10.20.210.180", "10.20.210.239", "dhcp-osaka-01"),
    ]
    for name, subnet_id, start_ip, end_ip, server_name in dhcp_scope_specs:
        _get_or_create(
            db,
            DhcpScope,
            name=name,
            defaults={
                "subnet_id": subnet_id,
                "start_ip": start_ip,
                "end_ip": end_ip,
                "server_name": server_name,
                "lease_duration_hours": 24,
            },
        )

    import_jobs = {
        "excel_complete": _get_or_create(
            db,
            ImportJob,
            job_name="Demo Excel Import - Tokyo",
            defaults={
                "source_type": SourceType.EXCEL,
                "status": ImportJobStatus.COMPLETED,
                "source_reference": "demo/demo_ips.xlsx",
                "importer_name": "excel_demo_importer",
                "summary": "Completed Tokyo import.",
                "processed_count": 12,
                "created_count": 12,
                "updated_count": 0,
                "failed_count": 0,
            },
        ),
        "dhcp_partial": _get_or_create(
            db,
            ImportJob,
            job_name="DHCP Snapshot Import",
            defaults={
                "source_type": SourceType.DHCP,
                "status": ImportJobStatus.PARTIAL,
                "source_reference": "demo/dhcp_snapshot.csv",
                "importer_name": "dhcp_stub_importer",
                "summary": "Partial DHCP snapshot load.",
                "processed_count": 20,
                "created_count": 8,
                "updated_count": 8,
                "failed_count": 4,
                "error_message": "Some DHCP leases could not be matched to known subnets.",
            },
        ),
        "dns_failed": _get_or_create(
            db,
            ImportJob,
            job_name="DNS Recon Import",
            defaults={
                "source_type": SourceType.DNS,
                "status": ImportJobStatus.FAILED,
                "source_reference": "demo/dns_export.csv",
                "importer_name": "dns_stub_importer",
                "summary": "Failed DNS load.",
                "processed_count": 0,
                "created_count": 0,
                "updated_count": 0,
                "failed_count": 6,
                "error_message": "Upstream DNS export format mismatch.",
            },
        ),
    }

    source_records = {}
    source_specs = [
        ("excel_tokyo_available", SourceType.EXCEL, "Tokyo Excel Seed", "tokyo-row-available", import_jobs["excel_complete"].id, 0.95),
        ("excel_tokyo_dhcp", SourceType.EXCEL, "Tokyo Excel Seed", "tokyo-row-dhcp", import_jobs["excel_complete"].id, 0.92),
        ("excel_tokyo_allocated", SourceType.EXCEL, "Tokyo Excel Seed", "tokyo-row-allocated", import_jobs["excel_complete"].id, 0.98),
        ("excel_tokyo_conflict", SourceType.EXCEL, "Tokyo Excel Seed", "tokyo-row-conflict", import_jobs["excel_complete"].id, 0.78),
        ("dhcp_tokyo", SourceType.DHCP, "Tokyo DHCP Snapshot", "tokyo-dhcp-lease", import_jobs["dhcp_partial"].id, 0.80),
        ("dns_osaka", SourceType.DNS, "Osaka DNS Export", "osaka-dns-a", import_jobs["dns_failed"].id, 0.66),
    ]
    for key, source_type, source_name, source_reference, import_job_id, confidence_score in source_specs:
        source_records[key] = _get_or_create(
            db,
            SourceRecord,
            source_type=source_type,
            source_name=source_name,
            source_reference=source_reference,
            defaults={
                "import_job_id": import_job_id,
                "source_system": source_type.value,
                "row_identifier": source_reference,
                "confidence_score": confidence_score,
            },
        )

    ip_specs = [
        ("10.10.110.20", tokyo_fixed.id, IPAddressStatus.AVAILABLE_CANDIDATE, "demo-available-01", "00:11:22:33:44:20", "Infrastructure", "fixed_device", "tokyo-available", source_records["excel_tokyo_available"], "Excel candidate"),
        ("10.10.110.21", tokyo_fixed.id, IPAddressStatus.DHCP_POOL, "demo-dhcp-01", "00:11:22:33:44:21", None, None, None, source_records["excel_tokyo_dhcp"], "DHCP pool entry"),
        ("10.10.110.22", tokyo_fixed.id, IPAddressStatus.ALLOCATED_CONFIRMED, "demo-allocated-01", "00:11:22:33:44:22", "Finance", "fixed_device", "asset-fin-22", source_records["excel_tokyo_allocated"], "Allocated office endpoint"),
        ("10.10.110.23", tokyo_fixed.id, IPAddressStatus.CONFLICT_SUSPECTED, "demo-conflict-01", "00:11:22:33:44:23", None, None, None, source_records["excel_tokyo_conflict"], "Conflict across DNS and DHCP"),
        ("10.10.120.30", tokyo_ops.id, IPAddressStatus.RESERVED, "ops-printer-01", "00:11:22:33:55:30", "Operations", "printer", "ops-printer-01", source_records["excel_tokyo_available"], "Reserved printer address"),
        ("10.10.120.31", tokyo_ops.id, IPAddressStatus.ALLOCATED_UNVERIFIED, "ops-terminal-01", "00:11:22:33:55:31", "Operations", "terminal", "ops-terminal-01", source_records["dhcp_tokyo"], "Observed but not fully validated"),
        ("10.20.210.40", osaka_fixed.id, IPAddressStatus.AVAILABLE_CANDIDATE, "osaka-available-01", "00:11:22:44:66:40", "Branch IT", "fixed_device", "osaka-available-01", source_records["dns_osaka"], "Branch candidate"),
        ("10.20.210.41", osaka_fixed.id, IPAddressStatus.CONFLICT_SUSPECTED, "osaka-conflict-01", "00:11:22:44:66:41", None, None, None, source_records["dns_osaka"], "Branch conflict"),
    ]

    ip_by_address: dict[str, IPAddress] = {}
    for address, subnet_id, status, hostname, mac, owner_department, ownership_type, trace_reference, primary_source, source_summary in ip_specs:
        ip = _get_or_create(
            db,
            IPAddress,
            address=address,
            defaults={
                "subnet_id": subnet_id,
                "status": status,
                "hostname": hostname,
                "mac_address": mac,
                "owner_department": owner_department,
                "ownership_type": ownership_type,
                "trace_reference": trace_reference,
                "primary_source_record_id": primary_source.id,
                "source_summary": source_summary,
                "confidence_score": primary_source.confidence_score,
            },
        )
        ip.status = status
        ip.hostname = hostname
        ip.mac_address = mac
        ip.owner_department = owner_department
        ip.ownership_type = ownership_type
        ip.trace_reference = trace_reference
        ip.primary_source_record_id = primary_source.id
        ip.source_summary = source_summary
        ip.confidence_score = primary_source.confidence_score
        ip_by_address[address] = ip

    observation_specs = [
        ("10.10.110.20", source_records["excel_tokyo_available"], "demo-available-01", "00:11:22:33:44:20", "available_candidate", True),
        ("10.10.110.21", source_records["excel_tokyo_dhcp"], "demo-dhcp-01", "00:11:22:33:44:21", "dhcp_pool", True),
        ("10.10.110.22", source_records["excel_tokyo_allocated"], "demo-allocated-01", "00:11:22:33:44:22", "allocated_confirmed", True),
        ("10.10.110.23", source_records["excel_tokyo_conflict"], "demo-conflict-01", "00:11:22:33:44:23", "conflict_suspected", True),
        ("10.10.110.23", source_records["dhcp_tokyo"], "tokyo-conflict-dhcp", "00:11:22:33:44:99", "dhcp_pool", False),
        ("10.20.210.41", source_records["dns_osaka"], "osaka-conflict-01", "00:11:22:44:66:41", "allocated_unverified", True),
    ]
    for address, source_record, observed_hostname, observed_mac, observed_status, is_primary in observation_specs:
        _get_or_create(
            db,
            IPAddressSourceObservation,
            ip_address_id=ip_by_address[address].id,
            source_record_id=source_record.id,
            defaults={
                "observed_hostname": observed_hostname,
                "observed_mac_address": observed_mac,
                "observed_status": observed_status,
                "observed_at": now - timedelta(hours=4),
                "confidence_score": source_record.confidence_score,
                "is_primary": is_primary,
            },
        )

    dns_record_specs = [
        ("demo-allocated-01.corp.local", ip_by_address["10.10.110.22"].id, source_records["excel_tokyo_allocated"].id),
        ("osaka-conflict-01.corp.local", ip_by_address["10.20.210.41"].id, source_records["dns_osaka"].id),
    ]
    for hostname, ip_address_id, source_record_id in dns_record_specs:
        _get_or_create(
            db,
            DnsRecord,
            hostname=hostname,
            record_type="A",
            defaults={"ip_address_id": ip_address_id, "zone_name": "corp.local", "source_record_id": source_record_id},
        )

    arp_specs = [
        ("10.10.110.22", "00:11:22:33:44:22", "Gi1/0/24"),
        ("10.10.110.23", "00:11:22:33:44:99", "Gi1/0/24"),
    ]
    for address, mac_address, switch_port_hint in arp_specs:
        existing = (
            db.query(ArpObservation)
            .filter(ArpObservation.ip_address_id == ip_by_address[address].id, ArpObservation.mac_address == mac_address)
            .first()
        )
        if not existing:
            db.add(
                ArpObservation(
                    ip_address_id=ip_by_address[address].id,
                    mac_address=mac_address,
                    observed_at=now - timedelta(hours=2),
                    observation_source="demo_seed",
                    source_record_id=source_records["dhcp_tokyo"].id,
                    switch_port_hint=switch_port_hint,
                )
            )

    request_specs = [
        {
            "request_number": "REQ-DEMO-REVIEW-001",
            "status": RequestStatus.UNDER_REVIEW,
            "applicant_name": "Aiko Tanaka",
            "applicant_email": "aiko.tanaka@example.com",
            "department": "Finance",
            "site_id": topology_index["sites"]["TOKYO-HQ"].id,
            "information_outlet_code": "IO-10F-1001-A",
            "subnet_id": tokyo_fixed.id,
            "vlan_or_subnet": tokyo_fixed.cidr,
            "hostname": "finance-pc-01",
            "mac_address": "00:AA:BB:CC:DD:01",
            "device_model_name": "Dell Latitude 7450",
            "fixed_ip_required": True,
            "source_type": SourceType.POWER_APPS,
            "source_channel": "power_apps",
            "eligibility_outcome": "review_needed",
            "eligibility_summary": "Conflict suspected IP exists in target subnet, manual review required.",
            "recommended_ip_address_id": None,
            "assigned_ip_address_id": None,
        },
        {
            "request_number": "REQ-DEMO-CANDIDATE-001",
            "status": RequestStatus.ASSIGNED,
            "applicant_name": "Ken Sato",
            "applicant_email": "ken.sato@example.com",
            "department": "Operations",
            "site_id": topology_index["sites"]["TOKYO-HQ"].id,
            "information_outlet_code": "IO-11F-1102-A",
            "subnet_id": tokyo_ops.id,
            "vlan_or_subnet": tokyo_ops.cidr,
            "hostname": "ops-terminal-02",
            "mac_address": "00:AA:BB:CC:DD:02",
            "device_model_name": "Panasonic CF-SR",
            "fixed_ip_required": True,
            "source_type": SourceType.POWER_AUTOMATE,
            "source_channel": "power_automate",
            "eligibility_outcome": "candidate",
            "eligibility_summary": "Candidate IP found in target subnet.",
            "recommended_ip_address_id": ip_by_address["10.10.120.30"].id,
            "assigned_ip_address_id": ip_by_address["10.10.120.30"].id,
        },
        {
            "request_number": "REQ-DEMO-BLOCKED-001",
            "status": RequestStatus.REJECTED,
            "applicant_name": "Mika Yamada",
            "applicant_email": "mika.yamada@example.com",
            "department": "Branch Ops",
            "site_id": topology_index["sites"]["OSAKA-BR"].id,
            "information_outlet_code": "IO-03F-0301-A",
            "subnet_id": osaka_fixed.id,
            "vlan_or_subnet": osaka_fixed.cidr,
            "hostname": "branch-kiosk-01",
            "mac_address": "00:AA:BB:CC:DD:03",
            "device_model_name": "Fujitsu ESPRIMO",
            "fixed_ip_required": True,
            "source_type": SourceType.API,
            "source_channel": "api",
            "eligibility_outcome": "blocked",
            "eligibility_summary": "No safe candidate IP available in target subnet.",
            "recommended_ip_address_id": None,
            "assigned_ip_address_id": None,
        },
    ]

    for spec in request_specs:
        request = _get_or_create(
            db,
            IntakeRequest,
            request_number=spec["request_number"],
            defaults=spec,
        )
        for key, value in spec.items():
            setattr(request, key, value)

        step = (
            db.query(ApprovalStep)
            .filter(ApprovalStep.intake_request_id == request.id, ApprovalStep.step_order == 1)
            .first()
        )
        if not step:
            step = ApprovalStep(
                intake_request_id=request.id,
                step_order=1,
                name="Initial Review",
                approver_role="reviewer",
                status=ApprovalStatus.PENDING,
            )
            db.add(step)
        if request.status == RequestStatus.ASSIGNED:
            step.status = ApprovalStatus.APPROVED
            step.approver_user_id = users_by_username["reviewer1"].id
            step.comment = "Approved from demo seed."
        elif request.status == RequestStatus.REJECTED:
            step.status = ApprovalStatus.REJECTED
            step.approver_user_id = users_by_username["reviewer1"].id
            step.comment = "Rejected from demo seed."

    assigned_ip = ip_by_address["10.10.120.30"]
    assigned_ip.status = IPAddressStatus.ALLOCATED_CONFIRMED
    assigned_ip.hostname = "ops-terminal-02"
    assigned_ip.mac_address = "00:AA:BB:CC:DD:02"
    assigned_ip.owner_department = "Operations"
    assigned_ip.ownership_type = "terminal"
    assigned_ip.trace_reference = "REQ-DEMO-CANDIDATE-001"

    allocation = (
        db.query(AllocationHistory)
        .filter(AllocationHistory.ip_address_id == ip_by_address["10.10.120.30"].id)
        .first()
    )
    if not allocation:
        assigned_request = db.query(IntakeRequest).filter(IntakeRequest.request_number == "REQ-DEMO-CANDIDATE-001").first()
        db.add(
            AllocationHistory(
                ip_address_id=ip_by_address["10.10.120.30"].id,
                intake_request_id=assigned_request.id,
                action="seed_assigned",
                previous_status="reserved",
                new_status="allocated_confirmed",
                new_owner="Operations",
                source_type=SourceType.POWER_AUTOMATE,
                source_reference=assigned_request.request_number,
                notes="Seeded assigned allocation for demo activity.",
            )
        )

    audit_specs = [
        (AuditAction.IMPORT, "ImportJob", import_jobs["excel_complete"].id, SourceType.EXCEL, "Initial Excel import completed."),
        (AuditAction.IMPORT, "ImportJob", import_jobs["dns_failed"].id, SourceType.DNS, "DNS import failed and needs review."),
        (AuditAction.SUBMIT, "IntakeRequest", "REQ-DEMO-REVIEW-001", SourceType.POWER_APPS, "Review-needed request submitted."),
        (AuditAction.TRANSITION, "IntakeRequest", "REQ-DEMO-CANDIDATE-001", SourceType.POWER_AUTOMATE, "Request assigned through workflow."),
    ]
    for action, entity_type, entity_id, source_type, summary in audit_specs:
        exists = (
            db.query(AuditLog)
            .filter(AuditLog.action == action, AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
            .first()
        )
        if not exists:
            db.add(
                AuditLog(
                    actor_user_id=users_by_username["admin"].id,
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    source_type=source_type,
                    change_summary=summary,
                    correlation_id=entity_id,
                )
            )

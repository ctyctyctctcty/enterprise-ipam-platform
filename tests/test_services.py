from pathlib import Path

from app.core.enums import AuditAction, IPAddressStatus, RequestStatus, SourceType
from app.models.audit import AuditLog
from app.models.intake import IntakeRequest
from app.models.ipam import IPAddress, Site, Subnet
from app.schemas.jobs import ImportJobCreate
from app.schemas.intake import IntakeRequestSubmit
from app.schemas.ipam import IPAddressCreate
from app.services.import_jobs import ImportJobService
from app.services.intake import IntakeService
from app.services.ipam import IPAMService
from scripts.generate_demo_excel import generate_demo_excel


def test_create_ip(db):
    service = IPAMService(db)
    ip = service.create_ip(
        IPAddressCreate(address="10.0.0.10", status=IPAddressStatus.AVAILABLE_CANDIDATE)
    )
    assert ip.address == "10.0.0.10"
    assert db.query(IPAddress).count() == 1


def test_create_request_generates_approval_step(db):
    service = IntakeService(db)
    request = service.create_request(
        IntakeRequestSubmit(
            applicant_name="Alice",
            applicant_email="alice@example.com",
            department="IT",
            site="Tokyo HQ",
            building="Main Building",
            floor="10F",
            room="Network Room",
            information_outlet_code="IO-001",
            fixed_ip_required=True,
            source_type=SourceType.POWER_APPS,
            source_reference="PA-123",
        )
    )
    assert request.request_number.startswith("REQ-")
    assert len(request.approval_steps) == 1
    assert request.requested_site_name == "Tokyo HQ"
    assert request.source_type == SourceType.POWER_APPS


def test_create_request_writes_audit_log(db):
    service = IntakeService(db)
    request = service.create_request(
        IntakeRequestSubmit(
            applicant_name="Bob",
            applicant_email="bob@example.com",
            fixed_ip_required=True,
            source_type=SourceType.API,
        )
    )
    audit_entry = (
        db.query(AuditLog)
        .filter(AuditLog.entity_id == request.id, AuditLog.action == AuditAction.SUBMIT)
        .first()
    )
    assert audit_entry is not None
    assert audit_entry.correlation_id == request.request_number


def test_subnet_usage_counts_ip_statuses(db):
    service = IPAMService(db)
    site = Site(code="TEST", name="Test Site")
    db.add(site)
    db.flush()
    subnet = Subnet(cidr="10.0.0.0/24", site_id=site.id)
    db.add(subnet)
    db.commit()
    db.refresh(subnet)
    service.create_ip(IPAddressCreate(address="10.0.0.10", subnet_id=subnet.id, status=IPAddressStatus.RESERVED))
    service.create_ip(
        IPAddressCreate(
            address="10.0.0.11",
            subnet_id=subnet.id,
            status=IPAddressStatus.CONFLICT_SUSPECTED,
        )
    )
    usage = service.subnet_usage(subnet.id)
    assert usage is not None
    assert usage.total_ips_known == 2
    assert usage.reserved == 1
    assert usage.conflict_suspected == 1


def test_demo_excel_import_and_request_transition(db):
    site = Site(code="TOKYO-HQ", name="Tokyo HQ")
    db.add(site)
    db.flush()
    subnet = Subnet(cidr="10.10.110.0/24", site_id=site.id)
    db.add(subnet)
    db.commit()

    workbook = generate_demo_excel(Path("C:/codex-workspace/enterprise-ipam/demo/test_demo_ips.xlsx"))
    import_service = ImportJobService(db)
    job = import_service.create_job(
        ImportJobCreate(
            source_type=SourceType.EXCEL,
            job_name="test import",
            importer_name="excel",
            source_reference=str(workbook),
        )
    )
    job = import_service.execute_job(job.id)
    assert job is not None
    assert job.processed_count == 4

    intake_service = IntakeService(db)
    request = intake_service.create_request(
        IntakeRequestSubmit(
            applicant_name="Demo User",
            applicant_email="demo@example.com",
            department="IT",
            vlan_or_subnet="10.10.110.0/24",
            hostname="demo-laptop-01",
            mac_address="00:aa:bb:cc:dd:ee",
            information_outlet_code="IO-10F-1001-A",
            fixed_ip_required=True,
        )
    )
    assert request.eligibility_outcome == "candidate"
    assert request.recommended_ip_address_id is not None

    transitioned = intake_service.transition_request(request.id, target_status=RequestStatus.ASSIGNED)
    assert transitioned is not None
    assert transitioned.assigned_ip_address_id == transitioned.recommended_ip_address_id
    refreshed = db.query(IntakeRequest).filter(IntakeRequest.id == request.id).first()
    assert refreshed is not None
    assert refreshed.status == RequestStatus.ASSIGNED

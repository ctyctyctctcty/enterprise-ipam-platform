from app.core.enums import AuditAction, IPAddressStatus, ImportJobStatus, RequestStatus, SourceType
from app.models.audit import AuditLog
from app.models.intake import IntakeRequest
from app.models.ipam import IPAddress, Site, Subnet
from app.models.jobs import ImportJob


def test_dashboard_summary_endpoint(client):
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    body = response.json()
    assert "kpis" in body
    assert body["kpis"]["total_ips"] == 0
    assert "operational_alerts" in body
    assert "site_summary" in body


def test_dashboard_alerts_and_recent_activity(client, db):
    site = Site(code="TOKYO-HQ", name="Tokyo HQ")
    db.add(site)
    db.flush()

    subnet = Subnet(cidr="10.20.30.0/29", name="Demo Subnet", site_id=site.id)
    db.add(subnet)
    db.flush()

    conflict_ip = IPAddress(
        address="10.20.30.2",
        subnet_id=subnet.id,
        status=IPAddressStatus.CONFLICT_SUSPECTED,
        hostname="conflict-demo",
    )
    candidate_ip = IPAddress(
        address="10.20.30.3",
        subnet_id=subnet.id,
        status=IPAddressStatus.AVAILABLE_CANDIDATE,
        hostname="candidate-demo",
    )
    db.add_all([conflict_ip, candidate_ip])

    request = IntakeRequest(
        request_number="REQ-DEMO-001",
        status=RequestStatus.UNDER_REVIEW,
        applicant_name="Demo User",
        applicant_email="demo@example.com",
        site_id=site.id,
        vlan_or_subnet=subnet.cidr,
        fixed_ip_required=True,
        source_type=SourceType.API,
        eligibility_outcome="review_needed",
        eligibility_summary="Conflict suspected IP requires manual review.",
    )
    job = ImportJob(
        source_type=SourceType.EXCEL,
        job_name="Demo Excel Import",
        status=ImportJobStatus.FAILED,
        source_reference="demo/demo_ips.xlsx",
        failed_count=1,
    )
    audit = AuditLog(
        action=AuditAction.IMPORT,
        entity_type="import_job",
        entity_id="job-1",
        source_type=SourceType.EXCEL,
        change_summary="Demo import failed for one row",
    )
    db.add_all([request, job, audit])
    db.commit()

    summary_response = client.get(f"/api/v1/dashboard/summary?site_id={site.id}")
    assert summary_response.status_code == 200
    summary_body = summary_response.json()
    assert summary_body["kpis"]["total_ips"] == 2
    assert summary_body["kpis"]["conflict_suspected_ips"] == 1
    assert summary_body["kpis"]["review_needed_requests"] == 1
    assert summary_body["kpis"]["failed_import_jobs"] == 1

    recent_response = client.get(f"/api/v1/dashboard/recent-activity?site_id={site.id}")
    assert recent_response.status_code == 200
    recent_body = recent_response.json()
    assert len(recent_body["recent_requests"]) == 1
    assert len(recent_body["recent_audit_logs"]) == 1
    assert len(recent_body["recent_import_jobs"]) == 1

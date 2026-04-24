from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.enums import ImportJobStatus, SourceType
from app.schemas.jobs import ExcelImportRequest, ImportJobCreate, ImportJobExecutionResult, ImportJobRead
from app.services.import_jobs import ImportJobService

router = APIRouter()


@router.get("/", response_model=list[ImportJobRead])
def list_import_jobs(db: Session = Depends(get_db)) -> list[ImportJobRead]:
    return ImportJobService(db).list_jobs()


@router.post("/jobs", response_model=ImportJobRead)
def create_import_job(payload: ImportJobCreate, db: Session = Depends(get_db)) -> ImportJobRead:
    return ImportJobService(db).create_job(payload)


@router.get("/jobs/{job_id}", response_model=ImportJobRead)
def get_import_job(job_id: str, db: Session = Depends(get_db)) -> ImportJobRead:
    job = ImportJobService(db).get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")
    return job


@router.post("/jobs/{job_id}/execute", response_model=ImportJobExecutionResult)
def execute_import_job(job_id: str, db: Session = Depends(get_db)) -> ImportJobExecutionResult:
    job = ImportJobService(db).execute_job(job_id)
    if not job:
        return ImportJobExecutionResult(
            job_id=job_id,
            status=ImportJobStatus.FAILED,
            message="Import job not found",
        )
    return ImportJobExecutionResult(
        job_id=job.id,
        status=job.status,
        message=job.summary or "Execution stub invoked",
    )


@router.post("/excel", response_model=ImportJobRead)
def create_excel_import(payload: ExcelImportRequest | None = None, db: Session = Depends(get_db)) -> ImportJobRead:
    return ImportJobService(db).create_job(
        ImportJobCreate(
            source_type=SourceType.EXCEL,
            job_name="Excel Demo Import",
            importer_name="excel",
            source_reference=(payload.workbook_path if payload and payload.workbook_path else "demo/demo_ips.xlsx"),
        )
    )


@router.post("/dhcp", response_model=ImportJobRead)
def create_dhcp_import(db: Session = Depends(get_db)) -> ImportJobRead:
    return ImportJobService(db).create_job(
        ImportJobCreate(
            source_type=SourceType.DHCP,
            job_name="DHCP Placeholder Import",
            importer_name="dhcp",
        )
    )


@router.post("/dns", response_model=ImportJobRead)
def create_dns_import(db: Session = Depends(get_db)) -> ImportJobRead:
    return ImportJobService(db).create_job(
        ImportJobCreate(
            source_type=SourceType.DNS,
            job_name="DNS Placeholder Import",
            importer_name="dns",
        )
    )


@router.post("/arp", response_model=ImportJobRead)
def create_arp_import(db: Session = Depends(get_db)) -> ImportJobRead:
    return ImportJobService(db).create_job(
        ImportJobCreate(
            source_type=SourceType.ARP,
            job_name="ARP Placeholder Import",
            importer_name="arp",
        )
    )

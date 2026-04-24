from sqlalchemy.orm import Session

from app.core.enums import AuditAction, ImportJobStatus, SourceType
from app.importers.excel import ExcelImporter
from app.models.jobs import ImportJob
from app.schemas.jobs import ImportJobCreate
from app.services.audit import AuditService


class ImportJobService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditService(db)

    def create_job(self, payload: ImportJobCreate) -> ImportJob:
        job = ImportJob(
            source_type=payload.source_type,
            job_name=payload.job_name,
            source_reference=payload.source_reference,
            importer_name=payload.importer_name,
            status=ImportJobStatus.PENDING,
        )
        self.db.add(job)
        self.db.flush()
        self.audit.log_event(
            action=AuditAction.IMPORT,
            entity_type="ImportJob",
            entity_id=job.id,
            source_type=payload.source_type,
            source_reference=payload.source_reference,
            change_summary="Import job registered.",
        )
        self.db.commit()
        self.db.refresh(job)
        return job

    def list_jobs(self) -> list[ImportJob]:
        return self.db.query(ImportJob).order_by(ImportJob.created_at.desc()).all()

    def get_job(self, job_id: str) -> ImportJob | None:
        return self.db.query(ImportJob).filter(ImportJob.id == job_id).first()

    def execute_job(self, job_id: str) -> ImportJob | None:
        job = self.get_job(job_id)
        if not job:
            return None
        job.status = ImportJobStatus.RUNNING
        self.db.flush()
        self.audit.log_event(
            action=AuditAction.IMPORT,
            entity_type="ImportJob",
            entity_id=job.id,
            source_type=job.source_type,
            source_reference=job.source_reference,
            correlation_id=job.id,
            change_summary="Import job execution started.",
        )
        if job.importer_name == "excel":
            workbook_path = job.source_reference or "demo/demo_ips.xlsx"
            ExcelImporter().run({"db": self.db, "job": job, "workbook_path": workbook_path})
            return self.get_job(job_id)

        job.summary = "Execution stub registered. Connect importer implementation here."
        self.audit.log_event(
            action=AuditAction.IMPORT,
            entity_type="ImportJob",
            entity_id=job.id,
            source_type=job.source_type,
            source_reference=job.source_reference,
            change_summary="Import job execution stub invoked.",
        )
        self.db.commit()
        self.db.refresh(job)
        return job

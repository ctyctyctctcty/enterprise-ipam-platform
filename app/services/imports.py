from sqlalchemy.orm import Session

from app.schemas.jobs import ImportJobCreate
from app.services.import_jobs import ImportJobService

class ImportService(ImportJobService):
    def __init__(self, db: Session):
        super().__init__(db)

    def create_job_legacy(self, source_type, name: str, source_reference: str | None = None):
        return self.create_job(
            ImportJobCreate(
                source_type=source_type,
                job_name=name,
                source_reference=source_reference,
            )
        )

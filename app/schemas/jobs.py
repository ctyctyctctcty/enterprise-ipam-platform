from pydantic import BaseModel

from app.core.enums import ImportJobStatus, SourceType
from app.schemas.common import TimestampedSchema


class ImportJobRead(TimestampedSchema):
    source_type: SourceType
    job_name: str
    status: ImportJobStatus
    file_name: str | None = None
    source_reference: str | None = None
    started_by: str | None = None
    importer_name: str | None = None
    summary: str | None = None
    error_message: str | None = None
    processed_count: int | None = None
    created_count: int | None = None
    updated_count: int | None = None
    failed_count: int | None = None


class ImportJobCreate(BaseModel):
    source_type: SourceType
    job_name: str
    source_reference: str | None = None
    importer_name: str | None = None


class ImportJobExecutionResult(BaseModel):
    job_id: str
    status: ImportJobStatus
    message: str


class ExcelImportRequest(BaseModel):
    workbook_path: str | None = None

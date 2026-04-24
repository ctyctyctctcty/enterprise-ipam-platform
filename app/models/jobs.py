from sqlalchemy import Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.core.enums import ImportJobStatus, SourceType
from app.models.base import TimestampMixin


class ImportJob(TimestampMixin, Base):
    __tablename__ = "import_jobs"

    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType))
    job_name: Mapped[str] = mapped_column(String(255))
    status: Mapped[ImportJobStatus] = mapped_column(Enum(ImportJobStatus), default=ImportJobStatus.PENDING)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    started_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    importer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    processed_count: Mapped[int | None] = mapped_column(nullable=True)
    created_count: Mapped[int | None] = mapped_column(nullable=True)
    updated_count: Mapped[int | None] = mapped_column(nullable=True)
    failed_count: Mapped[int | None] = mapped_column(nullable=True)
    source_records: Mapped[list["SourceRecord"]] = relationship("SourceRecord", back_populates="import_job")

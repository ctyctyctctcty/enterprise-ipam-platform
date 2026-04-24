from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampedSchema(ORMModel):
    id: str
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    environment: str
    database_url: str


class DateRangeFilter(BaseModel):
    start_date: date | None = None
    end_date: date | None = None


class ListResponse(BaseModel):
    total: int

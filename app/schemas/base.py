from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime


class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def create(cls, items: list, total: int, page: int, size: int):
        pages = (total + size - 1) // size
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    uptime_seconds: Optional[float] = None

class ReadinessCheckResponse(BaseModel):
    status: str

class RootResponse(BaseModel):
    name: str
    version: str
    status: str
    docs_url: str
    api_prefix: str
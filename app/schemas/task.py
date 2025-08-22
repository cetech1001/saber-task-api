from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.schemas.base import BaseResponse, TimestampMixin


class TaskBase(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    priority: Optional[int] = Field(None, ge=1, le=3, description="1=High, 2=Medium, 3=Low")
    due_date: Optional[datetime] = None

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v not in [1, 2, 3]:
            raise ValueError('Priority must be 1 (High), 2 (Medium), or 3 (Low)')
        return v

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                raise ValueError('Title cannot be empty or just whitespace')
        return v


class TaskCreate(TaskBase):
    title: str = Field(..., min_length=1, max_length=255)
    priority: int = Field(..., ge=1, le=3, description="1=High, 2=Medium, 3=Low")


class TaskUpdate(TaskBase):
    completed: Optional[bool] = None


class TaskOut(BaseResponse, TimestampMixin):
    id: int
    title: str
    description: Optional[str] = None
    priority: int
    due_date: Optional[datetime] = None
    completed: bool


class TaskSummary(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    high_priority_tasks: int
    overdue_tasks: int
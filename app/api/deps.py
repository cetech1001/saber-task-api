from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.task import Task
from app.crud.task import task as crud_task
from app.config import settings


def get_task_or_404(
    task_id: int,
    db: Session = Depends(get_db)
) -> Task:
    task_obj = crud_task.get(db, id=task_id)
    if not task_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return task_obj


def validate_pagination_params(
    page: int = 1,
    size: int = settings.default_page_size,
) -> tuple[int, int]:
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be >= 1"
        )
    if size < 1 or size > settings.max_page_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Size must be between 1 and {settings.max_page_size}"
        )
    return page, size
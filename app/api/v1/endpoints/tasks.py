from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud.task import task as crud_task
from app.database import get_db
from app.models.task import Task
from app.api.deps import get_task_or_404, validate_pagination_params
from app.schemas.base import PaginatedResponse
from app.schemas.task import TaskOut, TaskCreate, TaskUpdate, TaskSummary
from app.config import settings
from app.logging_config import get_logger

logger = get_logger("api.tasks")
router = APIRouter()


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
        task_data: TaskCreate,
        db: Session = Depends(get_db)
):
    """
    Create a new task.

    Returns the created task with its assigned ID and completed status defaulting to False.
    """
    logger.info(f"Creating new task: {task_data.title}")
    task = crud_task.create(db, obj_in=task_data)
    logger.info(f"Task created successfully with ID: {task.id}")
    return task


@router.get("/", response_model=PaginatedResponse)
def list_tasks(
        completed: Optional[bool] = Query(None, description="Filter by completion status"),
        priority: Optional[int] = Query(None, ge=1, le=3, description="1=High, 2=Medium, 3=Low"),
        q: Optional[str] = Query(None, description="Search by title/description (case-insensitive)"),
        page: int = Query(1, ge=1, description="Page number (1-based)"),
        size: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size, description="Items per page"),
        db: Session = Depends(get_db),
):
    """
    Retrieve tasks with optional filters, search, and pagination.

    - **completed**: Filter by completion status
    - **priority**: Filter by priority (1=High, 2=Medium, 3=Low)
    - **q**: Search in title and description
    - **page**: Page number (starts from 1)
    - **size**: Number of items per page (max 1000)
    """
    page, size = validate_pagination_params(page, size)
    skip = (page - 1) * size

    logger.info(
        f"Fetching tasks - page: {page}, size: {size}, filters: completed={completed}, priority={priority}, q={q}")

    tasks = crud_task.get_by_filters(
        db,
        completed=completed,
        priority=priority,
        q=q,
        skip=skip,
        limit=size
    )

    total = crud_task.count_by_filters(
        db,
        completed=completed,
        priority=priority,
        q=q
    )

    return PaginatedResponse.create(
        items=[TaskOut.model_validate(task) for task in tasks],
        total=total,
        page=page,
        size=size
    )


@router.get("/summary", response_model=TaskSummary)
def get_task_summary(db: Session = Depends(get_db)):
    """Get task statistics summary."""
    logger.info("Generating task summary")
    return crud_task.get_summary(db)


@router.get("/{task_id}/", response_model=TaskOut)
def get_task(task: Task = Depends(get_task_or_404)):
    """Retrieve a specific task by its ID."""
    logger.info(f"Fetching task with ID: {task.id}")
    return task


@router.put("/{task_id}/", response_model=TaskOut)
def update_task(
        task_data: TaskUpdate,
        task: Task = Depends(get_task_or_404),
        db: Session = Depends(get_db)
):
    """
    Update an existing task. All fields are optional.

    Only provided fields will be updated, others remain unchanged.
    """
    logger.info(f"Updating task with ID: {task.id}")
    updated_task = crud_task.update(db, db_obj=task, obj_in=task_data)
    logger.info(f"Task {task.id} updated successfully")
    return updated_task


@router.delete("/{task_id}/", status_code=status.HTTP_200_OK)
def delete_task(
        task: Task = Depends(get_task_or_404),
        db: Session = Depends(get_db)
):
    """Delete a task by ID."""
    logger.info(f"Deleting task with ID: {task.id}")
    crud_task.remove(db, id=task.id)
    logger.info(f"Task {task.id} deleted successfully")
    return {"message": "Task deleted successfully."}
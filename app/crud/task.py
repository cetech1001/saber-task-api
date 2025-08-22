from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, func, and_
from datetime import datetime

from app.crud.base import CRUDBase
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskSummary
from app.exceptions import DatabaseError
from app.logging_config import get_logger

logger = get_logger("crud.task")


class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    def get_by_filters(
            self,
            db: Session,
            *,
            completed: Optional[bool] = None,
            priority: Optional[int] = None,
            q: Optional[str] = None,
            skip: int = 0,
            limit: int = 100,
    ) -> List[Task]:
        try:
            stmt = select(Task)

            conditions = []
            if completed is not None:
                conditions.append(Task.completed == completed)
            if priority is not None:
                conditions.append(Task.priority == priority)
            if q:
                search_term = f"%{q}%"
                conditions.append(
                    or_(
                        Task.title.ilike(search_term),
                        Task.description.ilike(search_term)
                    )
                )

            if conditions:
                stmt = stmt.where(and_(*conditions))

            stmt = stmt.offset(skip).limit(limit)

            stmt = stmt.order_by(Task.priority.asc(), Task.created_at.desc())

            result = db.execute(stmt)
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"Error fetching tasks with filters: {e}")
            raise DatabaseError("Failed to fetch tasks")

    def count_by_filters(
            self,
            db: Session,
            *,
            completed: Optional[bool] = None,
            priority: Optional[int] = None,
            q: Optional[str] = None,
    ) -> int:
        try:
            stmt = select(func.count(Task.id))

            conditions = []
            if completed is not None:
                conditions.append(Task.completed == completed)
            if priority is not None:
                conditions.append(Task.priority == priority)
            if q:
                search_term = f"%{q}%"
                conditions.append(
                    or_(
                        Task.title.ilike(search_term),
                        Task.description.ilike(search_term)
                    )
                )

            if conditions:
                stmt = stmt.where(and_(*conditions))

            return db.execute(stmt).scalar()

        except Exception as e:
            logger.error(f"Error counting tasks with filters: {e}")
            raise DatabaseError("Failed to count tasks")

    def get_summary(self, db: Session) -> TaskSummary:
        try:
            total_tasks = db.execute(select(func.count(Task.id))).scalar()
            completed_tasks = db.execute(
                select(func.count(Task.id)).where(Task.completed == True)
            ).scalar()
            pending_tasks = total_tasks - completed_tasks
            high_priority_tasks = db.execute(
                select(func.count(Task.id)).where(Task.priority == 1)
            ).scalar()

            now = datetime.now()
            overdue_tasks = db.execute(
                select(func.count(Task.id)).where(
                    and_(
                        Task.due_date < now,
                        Task.completed == False
                    )
                )
            ).scalar()

            return TaskSummary(
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
                pending_tasks=pending_tasks,
                high_priority_tasks=high_priority_tasks,
                overdue_tasks=overdue_tasks
            )

        except Exception as e:
            logger.error(f"Error generating task summary: {e}")
            raise DatabaseError("Failed to generate task summary")


task = CRUDTask(Task)
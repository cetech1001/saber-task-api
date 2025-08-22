from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class BaseAppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class TaskNotFoundError(BaseAppException):
    def __init__(self, task_id: int):
        super().__init__(
            message=f"Task with id {task_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"task_id": task_id}
        )


class TaskValidationError(BaseAppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class DatabaseError(BaseAppException):
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def create_http_exception_from_app_exception(exc: BaseAppException) -> HTTPException:
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "message": exc.message,
            "details": exc.details
        }
    )
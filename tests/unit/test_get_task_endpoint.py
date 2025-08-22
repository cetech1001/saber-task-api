import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from datetime import datetime

from app.crud.task import task as crud_task
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.exceptions import DatabaseError


class TestTaskCRUD:
    def test_create_task_success(self):
        # Mock database session
        mock_db = Mock(spec=Session)

        # Mock task data
        task_data = TaskCreate(
            title="Unit Test Task",
            description="Testing CRUD create",
            priority=1,
            due_date=datetime(2024, 12, 25, 10, 0, 0)
        )

        # Instead of comparing objects, just verify the function calls and basic properties
        result = crud_task.create(mock_db, obj_in=task_data)

        # Verify the result is a Task instance with correct properties
        assert isinstance(result, Task)
        assert result.title == "Unit Test Task"
        assert result.description == "Testing CRUD create"
        assert result.priority == 1

        # Verify database operations were called
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

        # Verify the Task object passed to db.add has correct data
        added_task = mock_db.add.call_args[0][0]
        assert isinstance(added_task, Task)
        assert added_task.title == "Unit Test Task"

    def test_get_task_not_found(self):
        """Test edge case: get function returns None for a non-existent task"""
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_db.get.return_value = None

        # Test the get function
        result = crud_task.get(mock_db, id=999)

        # Assertions
        assert result is None
        mock_db.get.assert_called_once_with(Task, 999)

    def test_get_by_filters_database_error(self):
        """Test edge case: database error handling in get_by_filters"""
        # Mock database session that raises an exception
        mock_db = Mock(spec=Session)
        mock_db.execute.side_effect = Exception("Database connection failed")

        # Test that DatabaseError is raised
        with pytest.raises(DatabaseError, match="Failed to fetch tasks"):
            crud_task.get_by_filters(
                mock_db,
                completed=True,
                priority=1,
                q="test",
                skip=0,
                limit=10
            )
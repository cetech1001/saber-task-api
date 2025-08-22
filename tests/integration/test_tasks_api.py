from fastapi.testclient import TestClient
from datetime import datetime, timedelta


class TestTasksAPI:

    def test_create_task_success(self, client: TestClient):
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "priority": 1,
            "due_date": "2024-12-31T23:59:59"
        }

        response = client.post("/api/v1/tasks/", json=task_data)
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "Test Description"
        assert data["priority"] == 1
        assert data["completed"] is False
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_task_validation_error(self, client: TestClient):
        # Missing required title
        task_data = {
            "description": "Test Description",
            "priority": 1
        }

        response = client.post("/api/v1/tasks/", json=task_data)
        assert response.status_code == 422

    def test_create_task_invalid_priority(self, client: TestClient):
        task_data = {
            "title": "Test Task",
            "priority": 5  # Invalid priority
        }

        response = client.post("/api/v1/tasks/", json=task_data)
        assert response.status_code == 422

    def test_list_tasks_empty(self, client: TestClient):
        response = client.get("/api/v1/tasks/")
        assert response.status_code == 200

        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1

    def test_list_tasks_with_data(self, client: TestClient):
        # Create test tasks
        for i in range(3):
            task_data = {
                "title": f"Task {i}",
                "priority": (i % 3) + 1,
                "completed": i == 2
            }
            client.post("/api/v1/tasks/", json=task_data)

        response = client.get("/api/v1/tasks/")
        assert response.status_code == 200

        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 3

    def test_list_tasks_with_filters(self, client: TestClient):
        # Create test tasks
        completed_task = {
            "title": "Completed Task",
            "priority": 1,
            "completed": True
        }
        pending_task = {
            "title": "Pending Task",
            "priority": 2,
            "completed": False
        }

        client.post("/api/v1/tasks/", json=completed_task)
        client.post("/api/v1/tasks/", json=pending_task)

        # Filter by completed=True
        response = client.get("/api/v1/tasks/?completed=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["completed"] is True

    def test_get_task_success(self, client: TestClient):
        # Create a task first
        task_data = {"title": "Test Task", "priority": 1}
        create_response = client.post("/api/v1/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Get the task
        response = client.get(f"/api/v1/tasks/{task_id}/")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task"

    def test_get_task_not_found(self, client: TestClient):
        response = client.get("/api/v1/tasks/999/")
        assert response.status_code == 404

    def test_update_task_success(self, client: TestClient):
        # Create a task first
        task_data = {"title": "Original Task", "priority": 1}
        create_response = client.post("/api/v1/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Update the task
        update_data = {
            "title": "Updated Task",
            "completed": True
        }
        response = client.put(f"/api/v1/tasks/{task_id}/", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["completed"] is True
        assert data["priority"] == 1  # Unchanged

    def test_update_task_not_found(self, client: TestClient):
        update_data = {"title": "Updated Task"}
        response = client.put("/api/v1/tasks/999/", json=update_data)
        assert response.status_code == 404

    def test_delete_task_success(self, client: TestClient):
        # Create a task first
        task_data = {"title": "Task to Delete", "priority": 1}
        create_response = client.post("/api/v1/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Delete the task
        response = client.delete(f"/api/v1/tasks/{task_id}/")
        assert response.status_code == 200
        assert response.json()["message"] == "Task deleted successfully."

        # Verify task is deleted
        get_response = client.get(f"/api/v1/tasks/{task_id}/")
        assert get_response.status_code == 404

    def test_delete_task_not_found(self, client: TestClient):
        response = client.delete("/api/v1/tasks/999/")
        assert response.status_code == 404

    def test_task_summary(self, client: TestClient):
        # Create test tasks
        tasks = [
            {"title": "High Priority", "priority": 1, "completed": False},
            {"title": "Completed Task", "priority": 2, "completed": True},
            {"title": "Overdue Task", "priority": 3, "completed": False,
             "due_date": (datetime.now() - timedelta(days=1)).isoformat()},
        ]

        for task in tasks:
            client.post("/api/v1/tasks/", json=task)

        response = client.get("/api/v1/tasks/summary")
        assert response.status_code == 200

        data = response.json()
        assert data["total_tasks"] == 3
        assert data["completed_tasks"] == 1
        assert data["pending_tasks"] == 2
        assert data["high_priority_tasks"] == 1
        assert data["overdue_tasks"] == 1

    def test_pagination(self, client: TestClient):
        # Create 5 tasks
        for i in range(5):
            task_data = {"title": f"Task {i}", "priority": 1}
            client.post("/api/v1/tasks/", json=task_data)

        # Test first page
        response = client.get("/api/v1/tasks/?page=1&size=2")
        assert response.status_code == 200

        data = response.json()
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["size"] == 2
        assert data["total"] == 5
        assert data["pages"] == 3

    def test_search_functionality(self, client: TestClient):
        # Create test tasks
        tasks = [
            {"title": "Important Meeting", "priority": 1},
            {"title": "Buy Groceries", "priority": 2},
            {"title": "Meeting with Client", "priority": 1},
        ]

        for task in tasks:
            client.post("/api/v1/tasks/", json=task)

        # Search for "meeting"
        response = client.get("/api/v1/tasks/?q=meeting")
        assert response.status_code == 200

        data = response.json()
        assert len(data["items"]) == 2
        # Both tasks containing "meeting" should be returned
        titles = [item["title"] for item in data["items"]]
        assert "Important Meeting" in titles
        assert "Meeting with Client" in titles
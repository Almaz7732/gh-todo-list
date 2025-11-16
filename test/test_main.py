import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app, get_repository
from app.repository import TaskRepository

TEST_FILE = "tasks_test.json"

@pytest.fixture(autouse=True)
def cleanup():
    yield
    Path(TEST_FILE).unlink(missing_ok=True)

@pytest.fixture(autouse=True)
def override_repo():
    repo = TaskRepository(TEST_FILE)
    app.dependency_overrides[get_repository] = lambda: repo
    yield
    app.dependency_overrides = {}

client = TestClient(app)


def test_get_empty_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_create_task():
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
    }

    response = client.post("/tasks", json=task_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert "id" in data


def test_get_tasks_after_creation():
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
    }
    client.post("/tasks", json=task_data)

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == task_data["title"]


def test_update_task():
    task_data = {
        "title": "Original Task",
        "description": "Original Description",
    }
    create_response = client.post("/tasks", json=task_data)
    task_id = create_response.json()["id"]

    update_data = {
        "title": "Updated Task",
    }
    response = client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["description"] == task_data["description"]


def test_delete_task():
    task_data = {
        "title": "Task to delete",
        "description": "Will be deleted",
    }
    create_response = client.post("/tasks", json=task_data)
    task_id = create_response.json()["id"]

    response = client.get("/tasks")
    assert len(response.json()) == 1

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    response = client.get("/tasks")
    assert len(response.json()) == 0

def test_delete_nonexistent_task():
    response = client.delete("/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_create_task_validation():
    invalid_data = {
        "description": "Only description"
    }
    response = client.post("/tasks", json=invalid_data)
    assert response.status_code == 422


def test_complete_workflow():
    tasks = [
        {"title": "Task 1", "description": "Description 1"},
        {"title": "Task 2", "description": "Description 2"},
        {"title": "Task 3", "description": "Description 3"}
    ]

    created_tasks = []
    for task_data in tasks:
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 201
        created_tasks.append(response.json())

    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 3

    task_to_update = created_tasks[0]
    update_data = {"title": "Updated Task 1"}
    response = client.put(f"/tasks/{task_to_update['id']}", json=update_data)
    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task["title"] == "Updated Task 1"

    task_to_delete = created_tasks[1]
    response = client.delete(f"/tasks/{task_to_delete['id']}")
    assert response.status_code == 204

    response = client.get("/tasks")
    assert response.status_code == 200
    remaining_tasks = response.json()
    assert len(remaining_tasks) == 2
    remaining_ids = [task["id"] for task in remaining_tasks]
    assert task_to_delete["id"] not in remaining_ids
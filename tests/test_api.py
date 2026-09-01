import pytest
from fastapi.testclient import TestClient
from models import ValidStatuses
from main_api import app, get_service
from services import TaskService
from tests.fakes import FakeTaskRepository


@pytest.fixture
def repository():
    return FakeTaskRepository()


@pytest.fixture
def service(repository):
    return TaskService(repository)


@pytest.fixture
def client(service):
    app.dependency_overrides[get_service] = lambda: service

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_create_task_returns_created_task(client):
    response = client.post(
        "/tasks",
        json={
            "description": "Learn API testing",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 0
    assert data["description"] == "Learn API testing"
    assert data["status"] == "todo"
    assert "createdAt" in data
    assert "updatedAt" in data


def test_create_task_returns_422_when_description_is_too_short(client):
    response = client.post(
        "/tasks",
        json={
            "description": "ab",
        },
    )

    assert response.status_code == 422


def test_create_task_returns_422_when_description_is_missing(client):
    response = client.post(
        "/tasks",
        json={},
    )

    assert response.status_code == 422


def test_get_tasks_returns_200_and_all_tasks(client, repository):
    first = repository.create(
        "First task",
        ValidStatuses.TODO,
    )
    second = repository.create(
        "Second task",
        ValidStatuses.DONE,
    )

    response = client.get("/tasks")

    assert response.status_code == 200

    data = response.json()

    assert [task["id"] for task in data] == [
        first.id,
        second.id,
    ]


def test_get_tasks_filters_by_status(client, repository):
    first_todo = repository.create(
        "First task",
        ValidStatuses.DONE,
    )
    repository.create(
        "Second task",
        ValidStatuses.TODO,
    )
    second_todo = repository.create(
        "Third task",
        ValidStatuses.DONE,
    )

    response = client.get("/tasks?status=done")

    assert response.status_code == 200

    data = response.json()
    assert {task["id"] for task in data} == {
        first_todo.id,
        second_todo.id,
    }


def test_get_tasks_returns_422_when_status_is_invalid(client):
    response = client.get("/tasks?status=banana")

    assert response.status_code == 422


def test_get_task_by_id_returns_task(client, repository):
    task = repository.create(
        "Learn API testing",
        ValidStatuses.TODO,
    )

    response = client.get(f"/tasks/{task.id}")

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == task.id
    assert data["description"] == task.description
    assert data["status"] == "todo"


def test_get_task_by_id_returns_422_when_id_not_int(client):
    response = client.get("/tasks/ab")

    assert response.status_code == 422


def test_get_task_by_id_returns_404_when_task_not_found(client):
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task with id 999 not found"}


def test_update_task_updates_description(client, repository):
    task = repository.create(
        "Learn API testing",
        ValidStatuses.TODO,
    )

    response = client.patch(
        f"/tasks/{task.id}",
        json={
            "description": "New task description.",
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == task.id
    assert response.json()["description"] == "New task description."
    assert response.json()["status"] == "todo"


def test_update_task_returns_422_when_description_is_too_short(client):
    response = client.patch("/tasks/999", json={"description": "ab"})

    assert response.status_code == 422


def test_update_task_updates_status(client, repository):
    task = repository.create(
        "Learn API testing",
        ValidStatuses.TODO,
    )

    response = client.patch(
        f"/tasks/{task.id}",
        json={
            "status": "done",
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == task.id
    assert response.json()["status"] == "done"
    assert response.json()["description"] == "Learn API testing"


def test_update_task_updates_description_and_status(
    client,
    repository,
):
    task = repository.create(
        "Old description",
        ValidStatuses.TODO,
    )

    response = client.patch(
        f"/tasks/{task.id}",
        json={
            "description": "New description",
            "status": "done",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["description"] == "New description"
    assert data["status"] == "done"


def test_update_task_returns_422_when_body_is_empty(client):
    response = client.patch(
        "/tasks/1",
        json={},
    )

    assert response.status_code == 422


def test_update_task_returns_404_when_task_not_found(client):
    response = client.patch(
        "/tasks/999",
        json={
            "status": "done",
        },
    )

    assert response.status_code == 404


def test_update_task_returns_422_when_status_is_invalid(
    client,
):

    response = client.patch(
        "/tasks/1",
        json={
            "status": "banana",
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "payload",
    [
        {
            "description": None,
            "status": "done",
        },
        {
            "description": "New description",
            "status": None,
        },
    ],
)
def test_update_task_returns_422_when_field_is_null(
    client,
    payload,
):
    response = client.patch(
        "/tasks/1",
        json=payload,
    )

    assert response.status_code == 422


def test_delete_task_deletes_task(client, repository):
    task = repository.create("Learn API testing", ValidStatuses.TODO)
    response = client.delete(f"/tasks/{task.id}")

    assert response.status_code == 204
    assert repository.get_by_id(task.id) is None


def test_delete_task_returns_404_when_task_not_found(client):
    response = client.delete("/tasks/999")

    assert response.status_code == 404

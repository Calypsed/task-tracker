from models import ValidStatuses
from repositories.json_repository import JsonTaskRepository
from repositories.db_repository import DatabaseTaskRepository
import pytest
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture(params=["json", "postgres"])
def repository(request, tmp_path):
    if request.param == "json":
        filename = tmp_path / "tasks.json"

        yield JsonTaskRepository(str(filename))
        return
    
    elif request.param == "postgres":
        dsn = os.environ["TEST_DATABASE_URL"]

        with psycopg.connect(dsn) as conn:
            conn.execute("DELETE FROM tasks")

        yield DatabaseTaskRepository(dsn)

        with psycopg.connect(dsn) as conn:
            conn.execute("DELETE FROM tasks")


def test_create_returns_created_task(repository):
    task = repository.create(
        description="Buy groceries",
        status=ValidStatuses.TODO,
    )

    assert task.description == "Buy groceries"
    assert task.status == ValidStatuses.TODO

def test_create_sets_timestamps(repository):
    task = repository.create(
        "Buy groceries",
        ValidStatuses.TODO,
    )

    assert task.created_at is not None
    assert task.updated_at is not None
    assert task.created_at == task.updated_at
    assert task.created_at.tzinfo is not None

def test_create_assigns_unique_ids(repository):
    first_task = repository.create(
        "First task",
        ValidStatuses.TODO,
    )
    second_task = repository.create(
        "Second task",
        ValidStatuses.TODO,
    )

    assert first_task.id != second_task.id

def test_get_all_returns_all_tasks(repository):
    first_task = repository.create(
        "First task",
        ValidStatuses.TODO,
    )

    second_task = repository.create(
        "Second task",
        ValidStatuses.DONE,
    )

    tasks = repository.get_all()

    assert tasks == [first_task, second_task]

def test_get_all_filters_by_status(repository):
    todo_task = repository.create(
        "Todo task",
        ValidStatuses.TODO,
    )

    repository.create(
        "Done task",
        ValidStatuses.DONE,
    )

    second_todo_task = repository.create(
        "Another todo task",
        ValidStatuses.TODO,
    )

    tasks = repository.get_all(ValidStatuses.TODO)

    assert tasks == [todo_task, second_todo_task]

def test_get_by_id_returns_existing_task(repository):
    created_task = repository.create(
        "Learn pytest",
        ValidStatuses.TODO,
    )

    found_task = repository.get_by_id(
        created_task.id
    )

    assert found_task is not None
    assert found_task.id == created_task.id
    assert found_task.description == "Learn pytest"

def test_get_by_id_returns_none_when_task_not_found(repository):
    task = repository.get_by_id(999)

    assert task is None

def test_update_description_changes_description(repository):
    task = repository.create(
        "Old description",
        ValidStatuses.TODO,
    )

    old_updated_at = task.updated_at

    updated_task = repository.update_description(
        task.id,
        "New description",
    )

    assert updated_task is not None
    assert updated_task.id == task.id
    assert updated_task.description == "New description"
    assert updated_task.status == ValidStatuses.TODO
    assert updated_task.updated_at >= old_updated_at

def test_update_description_returns_none_when_task_not_found(repository):
    task = repository.update_description(
        999,
        "New description",
    )

    assert task is None

def test_update_description_preserves_status(repository):
    task = repository.create(
        "Old description",
        ValidStatuses.DONE,
    )

    updated_task = repository.update_description(
        task.id,
        "New description",
    )

    assert updated_task.status == ValidStatuses.DONE

def test_update_status_changes_status(repository):
    task = repository.create(
        "Learn pytest",
        ValidStatuses.TODO,
    )

    updated_task = repository.update_status(
        task.id,
        ValidStatuses.DONE,
    )

    assert updated_task is not None
    assert updated_task.status == ValidStatuses.DONE

def test_update_status_returns_none_when_task_not_found(repository):
    task = repository.update_status(
        999,
        ValidStatuses.DONE,
    )

    assert task is None

def test_update_status_preserves_description(repository):
    task = repository.create(
        "Learn pytest",
        ValidStatuses.TODO,
    )

    updated_task = repository.update_status(
        task.id,
        ValidStatuses.DONE,
    )

    assert updated_task.description == "Learn pytest"

def test_delete_returns_true_when_task_exists(repository):
    task = repository.create(
        "Buy groceries",
        ValidStatuses.TODO,
    )

    deleted = repository.delete(task.id)

    assert deleted is True
    assert repository.get_by_id(task.id) is None

def test_delete_returns_false_when_task_not_found(repository):
    deleted = repository.delete(999)

    assert deleted is False

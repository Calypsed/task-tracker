from task_tracker.models import ValidStatuses
from task_tracker.repositories.json_repository import JsonTaskRepository
import pytest
import json


@pytest.fixture
def filename(tmp_path):
    return tmp_path / "tasks.json"


@pytest.fixture
def repository(filename):
    return JsonTaskRepository(str(filename))


def test_creating_repository_does_not_create_a_file_if_one_does_not_exist(filename):
    assert filename.exists() is False

    JsonTaskRepository(str(filename))

    assert filename.exists() is False


def test_create_creates_file_when_it_does_not_exist(filename):
    assert filename.exists() is False

    repository = JsonTaskRepository(str(filename))

    task = repository.create(description="Task description", status=ValidStatuses.TODO)

    assert filename.exists() is True


def test_create_persists_task(filename):
    repository = JsonTaskRepository(str(filename))

    created_task = repository.create(
        "Learn pytest",
        ValidStatuses.TODO,
    )
    new_repository = JsonTaskRepository(str(filename))
    loaded_task = new_repository.get_by_id(created_task.id)

    assert loaded_task == created_task


def test_update_persists_changes(repository, filename):
    task = repository.create(
        "Old description",
        ValidStatuses.TODO,
    )
    repository.update(task.id, description="New description", status=ValidStatuses.DONE)
    new_repository = JsonTaskRepository(str(filename))
    loaded_task = new_repository.get_by_id(task.id)

    assert loaded_task is not None
    assert loaded_task.description == "New description"
    assert loaded_task.status == ValidStatuses.DONE


def test_delete_persists_changes(repository, filename):
    task = repository.create(
        "Learn pytest",
        ValidStatuses.TODO,
    )
    repository.delete(task.id)

    new_repository = JsonTaskRepository(str(filename))

    assert new_repository.get_by_id(task.id) is None


def test_repository_does_not_overwrite_corrupted_json(tmp_path):
    filename = tmp_path / "tasks.json"
    corrupted_data = "{ broken json"

    filename.write_text(corrupted_data)

    repo = JsonTaskRepository(str(filename))

    with pytest.raises(json.JSONDecodeError):
        repo.get_all()
    assert filename.read_text() == corrupted_data

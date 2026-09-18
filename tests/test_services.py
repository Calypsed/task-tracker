import pytest

from task_tracker.exceptions import TaskNotFoundError, InvalidTaskDescriptionError
from task_tracker.models import ValidStatuses
from task_tracker.services import TaskService
from tests.fakes import FakeTaskRepository
from datetime import datetime, timezone


@pytest.fixture
def repository():
    return FakeTaskRepository()


@pytest.fixture
def service(repository):
    return TaskService(repository)


def test_create_task_creates_todo_task(service):
    due_at = datetime(2030, 1, 2, 3, 45, 6, 789, tzinfo=timezone.utc)
    task = service.create_task(description="Learn pytest", due_at=due_at)

    assert task is not None
    assert task.description == "Learn pytest"
    assert task.status == ValidStatuses.TODO
    assert task.due_at == due_at


def test_create_task_raises_when_description_is_too_short(service):
    with pytest.raises(InvalidTaskDescriptionError):
        service.create_task(description="ab")


def test_create_task_raises_when_description_contains_only_spaces(service):
    with pytest.raises(InvalidTaskDescriptionError):
        service.create_task(description="   ")


def test_create_task_strips_description(service):
    task = service.create_task(description="  Learn pytest  ")

    assert task.description == "Learn pytest"


def test_get_task_by_id_returns_task(service, repository):
    created_task = repository.create(
        description="Learn pytest",
        status=ValidStatuses.TODO,
    )

    task = service.get_task_by_id(created_task.id)

    assert task == created_task


def test_get_task_by_id_raises_with_correct_id(service):
    with pytest.raises(TaskNotFoundError) as error:
        service.get_task_by_id(999)

    assert error.value.task_id == 999


def test_update_task_changes_description(service, repository):
    task = repository.create(
        description="Old description",
        status=ValidStatuses.TODO,
    )

    updated_task = service.update_task(
        task.id,
        description="New description",
    )

    assert updated_task.description == "New description"


def test_update_task_raises_when_description_is_too_short(
    service,
    repository,
):
    task = repository.create(
        description="Old description",
        status=ValidStatuses.TODO,
    )

    with pytest.raises(InvalidTaskDescriptionError):
        service.update_task(
            task.id,
            description="ab",
        )


def test_update_task_strips_description(
    service,
    repository,
):
    task = repository.create(
        description="Old description",
        status=ValidStatuses.TODO,
    )

    updated_task = service.update_task(
        task.id,
        description="  New description  ",
    )

    assert updated_task.description == "New description"


def test_update_task_raises_when_description_contains_only_spaces(
    service,
    repository,
):
    task = repository.create(
        description="Old description",
        status=ValidStatuses.TODO,
    )

    with pytest.raises(InvalidTaskDescriptionError):
        service.update_task(
            task.id,
            description="   ",
        )


def test_update_task_changes_status(service, repository):
    task = repository.create(
        description="Learn pytest",
        status=ValidStatuses.TODO,
    )

    updated_task = service.update_task(
        task.id,
        status=ValidStatuses.DONE,
    )

    assert updated_task.status == ValidStatuses.DONE


def test_update_task_raises_when_task_not_found(service):
    with pytest.raises(TaskNotFoundError):
        service.update_task(
            999,
            status=ValidStatuses.DONE,
        )


def test_delete_task_deletes_task(service, repository):
    task = repository.create(
        description="Learn pytest",
        status=ValidStatuses.TODO,
    )

    service.delete_task(task.id)

    assert repository.get_by_id(task.id) is None


def test_delete_task_raises_when_task_not_found(service):
    with pytest.raises(TaskNotFoundError):
        service.delete_task(999)

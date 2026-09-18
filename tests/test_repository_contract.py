from task_tracker.models import ValidStatuses
from task_tracker.repositories.json_repository import JsonTaskRepository
from task_tracker.repositories.psycopg_repository import PsycopgTaskRepository
from task_tracker.repositories.sqlalchemy_orm_repository import (
    SqlAlchemyOrmTaskRepository,
)
from task_tracker.repositories.sqlalchemy_core_repository import (
    SqlAlchemyCoreTaskRepository,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
import os
import psycopg
from dotenv import load_dotenv
from task_tracker.constants import RepositoryType
from typing import assert_never
from task_tracker.database.connection import make_sqlalchemy_url
from datetime import datetime, timezone

load_dotenv()


def clear_database(dsn: str) -> None:
    with psycopg.connect(dsn) as conn:
        conn.execute("TRUNCATE TABLE tasks RESTART IDENTITY")


@pytest.fixture(
    params=[
        RepositoryType.JSON,
        RepositoryType.PSYCOPG,
        RepositoryType.SQLALCHEMY_ORM,
        RepositoryType.SQLALCHEMY_CORE,
    ]
)
def repository_factory(request, tmp_path):
    repository_type: RepositoryType = request.param

    match repository_type:
        case RepositoryType.JSON:
            filename = tmp_path / "tasks.json"

            def create_json_repository():
                return JsonTaskRepository(str(filename))

            yield create_json_repository
            return

        case RepositoryType.PSYCOPG:
            request.getfixturevalue("migrate_test_database")

            dsn = os.environ["TEST_DATABASE_URL"]

            def create_psycopg_repository():
                return PsycopgTaskRepository(dsn)

            clear_database(dsn)
            yield create_psycopg_repository
            clear_database(dsn)
            return

        case RepositoryType.SQLALCHEMY_ORM:
            request.getfixturevalue("migrate_test_database")

            dsn = os.environ["TEST_DATABASE_URL"]
            engine = create_engine(make_sqlalchemy_url(dsn))
            session_factory = sessionmaker(
                bind=engine,
                expire_on_commit=False,
            )

            def create_orm_repository():
                return SqlAlchemyOrmTaskRepository(session_factory)

            clear_database(dsn)
            yield create_orm_repository
            clear_database(dsn)
            engine.dispose()
            return

        case RepositoryType.SQLALCHEMY_CORE:
            request.getfixturevalue("migrate_test_database")

            dsn = os.environ["TEST_DATABASE_URL"]
            engine = create_engine(make_sqlalchemy_url(dsn))

            def create_core_repository():
                return SqlAlchemyCoreTaskRepository(engine)

            clear_database(dsn)
            yield create_core_repository
            clear_database(dsn)
            engine.dispose()
            return

    assert_never(repository_type)


@pytest.fixture
def repository(repository_factory):
    return repository_factory()


@pytest.mark.parametrize(
    "due_at",
    [
        None,
        datetime(2030, 1, 2, 3, 45, 6, 789, tzinfo=timezone.utc),
    ],
)
def test_create_returns_tasks_with_provided_values(repository, due_at):
    task = repository.create(
        description="Buy groceries", status=ValidStatuses.TODO, due_at=due_at
    )

    assert task.description == "Buy groceries"
    assert task.status == ValidStatuses.TODO
    assert task.due_at == due_at


@pytest.mark.parametrize(
    "due_at",
    [
        None,
        datetime(2030, 1, 2, 3, 45, 6, 789, tzinfo=timezone.utc),
    ],
)
def test_create_persists_task(repository_factory, due_at):
    repo1 = repository_factory()
    created_task = repo1.create(
        description="Learn pytest",
        status=ValidStatuses.TODO,
        due_at=due_at,
    )
    repo2 = repository_factory()

    loaded_task = repo2.get_by_id(created_task.id)

    assert loaded_task == created_task


def test_created_task_dates_have_timestamps(repository):
    task = repository.create(
        "Buy groceries",
        ValidStatuses.TODO,
        due_at=datetime(2030, 1, 2, 3, 45, 6, 789, tzinfo=timezone.utc),
    )

    assert task.created_at is not None
    assert task.updated_at is not None
    assert task.created_at == task.updated_at
    assert task.created_at.tzinfo is not None
    assert task.updated_at.tzinfo is not None
    assert task.due_at.tzinfo is not None


def test_created_task_has_unique_id(repository):
    first_task = repository.create(
        "First task",
        ValidStatuses.TODO,
    )
    second_task = repository.create(
        "Second task",
        ValidStatuses.TODO,
    )

    assert first_task.id != second_task.id


def test_get_all_returns_tasks_ordered_by_id(repository):
    repository.create(
        "First task",
        ValidStatuses.TODO,
    )
    repository.create(
        "Second task",
        ValidStatuses.DONE,
    )

    tasks = repository.get_all()

    assert [task.id for task in tasks] == sorted(task.id for task in tasks)


def test_get_all_can_return_tasks_filtered_by_status(repository):
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


def test_get_by_id_returns_a_single_task(repository):
    repository.create(
        "First task",
        ValidStatuses.TODO,
    )
    created_task = repository.create(
        "Second task",
        ValidStatuses.TODO,
    )

    found_task = repository.get_by_id(created_task.id)

    assert found_task is not None
    assert found_task.id == created_task.id
    assert found_task.description == "Second task"


def test_get_by_id_returns_none_when_task_not_found(repository):
    task = repository.get_by_id(999)

    assert task is None


def test_update_changes_description(repository):
    task = repository.create(
        "Old description",
        ValidStatuses.DONE,
    )

    updated = repository.update(
        task.id,
        description="New description",
    )

    assert updated is not None
    assert updated.description == "New description"
    assert updated.status == ValidStatuses.DONE


def test_update_returns_task_when_changes_status(repository):
    task = repository.create(
        "Learn pytest",
        ValidStatuses.TODO,
    )

    updated = repository.update(
        task.id,
        status=ValidStatuses.DONE,
    )

    assert updated is not None
    assert updated.status == ValidStatuses.DONE
    assert updated.description == "Learn pytest"


def test_update_changes_description_and_status(repository):
    task = repository.create(
        "Old description",
        ValidStatuses.TODO,
    )

    updated = repository.update(
        task.id,
        description="New description",
        status=ValidStatuses.DONE,
    )

    assert updated is not None
    assert updated.description == "New description"
    assert updated.status == ValidStatuses.DONE


def test_update_returns_none_when_task_not_found(repository):
    updated = repository.update(
        999,
        description="New description",
    )

    assert updated is None


def test_update_without_changes_does_not_change_updated_at(repository):
    task = repository.create(
        "Some task",
        ValidStatuses.TODO,
    )

    updated = repository.update(task.id)

    assert updated is not None
    assert updated.updated_at == task.updated_at


def test_delete_returns_true_when_task_exists(repository):
    repository.create(
        "First task",
        ValidStatuses.TODO,
    )
    task = repository.create(
        "Second task",
        ValidStatuses.TODO,
    )

    deleted = repository.delete(task.id)

    assert deleted is True
    assert repository.get_by_id(task.id) is None


def test_delete_returns_false_when_task_not_found(repository):
    deleted = repository.delete(999)

    assert deleted is False


def test_mutating_returned_task_does_not_change_persisted_task(repository):
    task = repository.create(
        "Created description",
        ValidStatuses.TODO,
    )

    task.description = "New description"

    persisted = repository.get_by_id(task.id)

    assert persisted is not None
    assert persisted.description == "Created description"

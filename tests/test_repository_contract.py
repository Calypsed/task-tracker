from models import ValidStatuses
from repositories.json_repository import JsonTaskRepository
from repositories.psycopg_repository import PsycopgTaskRepository
from repositories.sqlalchemy_orm_repository import SqlAlchemyOrmTaskRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
import os
import psycopg
from dotenv import load_dotenv
from constants import RepositoryType
from typing import assert_never

load_dotenv()


def clear_database(dsn: str) -> None:
    with psycopg.connect(dsn) as conn:
        conn.execute("DELETE FROM tasks")


def make_sqlalchemy_url(dsn: str) -> str:
    if dsn.startswith("postgresql://"):
        return dsn.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )

    return dsn


@pytest.fixture(
    params=[
        RepositoryType.JSON,
        RepositoryType.PSYCOPG,
        RepositoryType.SQLALCHEMY_ORM,
    ]
)
def repository(request, tmp_path):
    repository_type: RepositoryType = request.param

    match repository_type:
        case RepositoryType.JSON:
            filename = tmp_path / "tasks.json"

            yield JsonTaskRepository(str(filename))
            return

        case RepositoryType.PSYCOPG:
            dsn = os.environ["TEST_DATABASE_URL"]
            clear_database(dsn)

            yield PsycopgTaskRepository(dsn)

            clear_database(dsn)
            return

        case RepositoryType.SQLALCHEMY_ORM:
            dsn = os.environ["TEST_DATABASE_URL"]
            clear_database(dsn)

            engine = create_engine(make_sqlalchemy_url(dsn))

            session_factory = sessionmaker(
                bind=engine,
                expire_on_commit=False,
            )

            yield SqlAlchemyOrmTaskRepository(session_factory)

            engine.dispose()
            clear_database(dsn)
            return

    assert_never(repository_type)


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


def test_update_changes_status(repository):
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

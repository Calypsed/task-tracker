import os

from typing import assert_never
from constants import JSON_FILENAME, RepositoryType
from database.connection import create_session_factory
from repositories.json_repository import JsonTaskRepository
from repositories.protocol import TaskRepository
from repositories.psycopg_repository import PsycopgTaskRepository
from repositories.sqlalchemy_orm_repository import SqlAlchemyOrmTaskRepository


def create_repository() -> TaskRepository:
    repository_type_raw = os.getenv(
        "REPOSITORY_TYPE",
        RepositoryType.JSON.value,
    )

    try:
        repository_type = RepositoryType(repository_type_raw)
    except ValueError:
        raise ValueError(f"Unknown repository type: {repository_type_raw}") from None

    match repository_type:
        case RepositoryType.JSON:
            filename = os.getenv(
                "JSON_FILENAME",
                JSON_FILENAME,
            )
            return JsonTaskRepository(filename)

        case RepositoryType.PSYCOPG:
            database_url = os.environ["DATABASE_URL"]
            return PsycopgTaskRepository(database_url)

        case RepositoryType.SQLALCHEMY_ORM:
            database_url = os.environ["DATABASE_URL"]
            session_factory = create_session_factory(database_url)

            return SqlAlchemyOrmTaskRepository(session_factory)

    assert_never(repository_type)

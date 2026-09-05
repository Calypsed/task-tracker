import os

from typing import assert_never
from constants import JSON_FILENAME, RepositoryType
from database.connection import make_session_factory, make_engine
from repositories.json_repository import JsonTaskRepository
from repositories.protocol import TaskRepository
from repositories.psycopg_repository import PsycopgTaskRepository
from repositories.sqlalchemy_orm_repository import SqlAlchemyOrmTaskRepository
from repositories.sqlalchemy_core_repository import SqlAlchemyCoreTaskRepository


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
            engine = make_engine(database_url)
            session_factory = make_session_factory(engine)

            return SqlAlchemyOrmTaskRepository(session_factory)

        case RepositoryType.SQLALCHEMY_CORE:
            database_url = os.environ["DATABASE_URL"]
            engine = make_engine(database_url)

            return SqlAlchemyCoreTaskRepository(engine)

    assert_never(repository_type)

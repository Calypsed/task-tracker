import os

import constants
from database.connection import create_session_factory
from repositories.json_repository import JsonTaskRepository
from repositories.protocol import TaskRepository
from repositories.psycopg_repository import PsycopgTaskRepository
from repositories.sqlalchemy_repository import SqlAlchemyTaskRepository


def create_repository() -> TaskRepository:
    repository_type = os.getenv("REPOSITORY_TYPE", "json")

    if repository_type == "json":
        filename = os.getenv(
            "JSON_FILENAME",
            constants.JSON_FILENAME,
        )
        return JsonTaskRepository(filename)

    if repository_type == "psycopg":
        database_url = os.environ["DATABASE_URL"]
        return PsycopgTaskRepository(database_url)

    if repository_type == "sqlalchemy":
        database_url = os.environ["DATABASE_URL"]
        session_factory = create_session_factory(database_url)

        return SqlAlchemyTaskRepository(session_factory)

    raise ValueError(f"Unknown repository type: {repository_type}")

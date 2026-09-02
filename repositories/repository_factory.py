import os
import constants
from repositories.protocol import TaskRepository
from repositories.db_repository import DatabaseTaskRepository
from repositories.json_repository import JsonTaskRepository


def create_repository() -> TaskRepository:
    repository_type = os.getenv("REPOSITORY_TYPE", "json")

    if repository_type == "postgres":
        database_url = os.environ["DATABASE_URL"]

        return DatabaseTaskRepository(database_url)

    if repository_type == "json":
        filename = os.getenv(
            "JSON_FILENAME",
            constants.JSON_FILENAME,
        )
        return JsonTaskRepository(filename)

    raise ValueError(f"Unknown repository type: {repository_type}")

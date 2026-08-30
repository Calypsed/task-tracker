import os

import psycopg
import pytest
from dotenv import load_dotenv

from models import ValidStatuses
from repositories.db_repository import DatabaseTaskRepository

load_dotenv()


@pytest.fixture
def repository():
    dsn = os.environ["TEST_DATABASE_URL"]

    with psycopg.connect(dsn) as conn:
        conn.execute("DELETE FROM tasks")

    repository = DatabaseTaskRepository(dsn)

    yield repository

    with psycopg.connect(dsn) as conn:
        conn.execute("DELETE FROM tasks")


def test_database_rejects_too_short_description(repository):
    with pytest.raises(psycopg.errors.CheckViolation):
        repository.create(
            "ab",
            ValidStatuses.TODO,
        )

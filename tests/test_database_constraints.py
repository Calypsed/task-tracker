import os

import psycopg
import pytest
from dotenv import load_dotenv

load_dotenv()


def test_database_rejects_too_short_description():
    dsn = os.environ["TEST_DATABASE_URL"]

    with pytest.raises(psycopg.errors.CheckViolation):
        with psycopg.connect(dsn) as conn:
            conn.execute(
                """
                INSERT INTO tasks (description, status)
                VALUES (%s, %s)
                """,
                ("ab", "todo"),
            )

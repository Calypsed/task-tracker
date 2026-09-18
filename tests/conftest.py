import os
import pytest
from alembic import command
from alembic.config import Config


@pytest.fixture(scope="session")
def migrate_test_database():
    old_url = os.environ["ALEMBIC_DATABASE_URL"]
    test_url = os.environ["TEST_DATABASE_URL"]

    try:
        os.environ["ALEMBIC_DATABASE_URL"] = test_url

        config = Config("alembic.ini")
        command.upgrade(config, "head")

    finally:
        os.environ["ALEMBIC_DATABASE_URL"] = old_url

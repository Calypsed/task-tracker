from repositories.repository_factory import create_repository
from repositories.json_repository import JsonTaskRepository
from repositories.psycopg_repository import PsycopgTaskRepository
from repositories.sqlalchemy_orm_repository import SqlAlchemyOrmTaskRepository
import pytest
from constants import RepositoryType


def test_factory_creates_json_repository(monkeypatch, tmp_path):
    monkeypatch.setenv("REPOSITORY_TYPE", RepositoryType.JSON.value)
    monkeypatch.setenv(
        "JSON_FILENAME",
        str(tmp_path / "tasks.json"),
    )

    repository = create_repository()

    assert isinstance(repository, JsonTaskRepository)


def test_factory_creates_psycopg_repository(monkeypatch):
    monkeypatch.setenv("REPOSITORY_TYPE", RepositoryType.PSYCOPG.value)
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://test:test@localhost:5432/test_db",
    )

    repository = create_repository()

    assert isinstance(repository, PsycopgTaskRepository)


def test_factory_creates_sqlalchemy_orm_repository(monkeypatch):
    monkeypatch.setenv("REPOSITORY_TYPE", RepositoryType.SQLALCHEMY_ORM.value)
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://test:test@localhost:5432/test_db",
    )

    repository = create_repository()

    assert isinstance(repository, SqlAlchemyOrmTaskRepository)


def test_factory_rejects_unknown_repository_type(monkeypatch):
    monkeypatch.setenv("REPOSITORY_TYPE", "banana")

    with pytest.raises(ValueError, match="banana"):
        create_repository()

from repositories.repository_factory import create_repository
from repositories.json_repository import JsonTaskRepository
from repositories.db_repository import DatabaseTaskRepository
import pytest

def test_factory_creates_json_repository(monkeypatch, tmp_path):
    monkeypatch.setenv("REPOSITORY_TYPE", "json")
    monkeypatch.setenv(
        "JSON_FILENAME",
        str(tmp_path / "tasks.json"),
    )

    repository = create_repository()

    assert isinstance(repository, JsonTaskRepository)

def test_factory_creates_database_repository(monkeypatch):
    monkeypatch.setenv("REPOSITORY_TYPE", "postgres")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://test:test@localhost:5432/test_db",
    )

    repository = create_repository()

    assert isinstance(repository, DatabaseTaskRepository)

def test_factory_rejects_unknown_repository_type(monkeypatch):
    monkeypatch.setenv("REPOSITORY_TYPE", "banana")

    with pytest.raises(ValueError, match="banana"):
        create_repository()
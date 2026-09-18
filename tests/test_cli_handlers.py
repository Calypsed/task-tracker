import pytest
import argparse
from task_tracker.main_cli import (
    add_task,
    list_tasks,
    update_task,
    mark_done,
    mark_in_progress,
    delete_task,
    parse_due_at,
)
from task_tracker.services import TaskService
from tests.fakes import FakeTaskRepository
from task_tracker.models import ValidStatuses
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo


FIXED_NOW = datetime(2025, 1, 2, 3, 45, 6, 789, tzinfo=timezone.utc)

FUTURE_DUE_AT = datetime(2030, 1, 2, 3, 45, 6, 789, tzinfo=timezone.utc)

test_timezone = ZoneInfo("Europe/Moscow")


@pytest.fixture
def repository():
    return FakeTaskRepository()


@pytest.fixture
def service(repository):
    return TaskService(
        repository,
        now_provider=lambda: FIXED_NOW,
    )


@pytest.mark.parametrize(
    ("raw_due_at", "expected_due_at"),
    [
        (None, None),
        (
            FUTURE_DUE_AT.isoformat(),
            FUTURE_DUE_AT,
        ),
        (
            "2030-02-01",
            datetime(
                year=2030,
                month=2,
                day=1,
                hour=23,
                minute=59,
                second=59,
                tzinfo=test_timezone,
            ),
        ),
        (
            "2030-02-01T18:30",
            datetime(
                year=2030, month=2, day=1, hour=18, minute=30, tzinfo=test_timezone
            ),
        ),
        (
            "2030-02-01T18:30+05:00",
            datetime(
                year=2030,
                month=2,
                day=1,
                hour=18,
                minute=30,
                tzinfo=timezone(offset=timedelta(hours=5)),
            ),
        ),
        (
            "01.02.2030",
            datetime(
                year=2030,
                month=2,
                day=1,
                hour=23,
                minute=59,
                second=59,
                tzinfo=test_timezone,
            ),
        ),
        (
            "01.02.2030 18:30",
            datetime(
                year=2030, month=2, day=1, hour=18, minute=30, tzinfo=test_timezone
            ),
        ),
    ],
)
def test_parse_due_at(raw_due_at, expected_due_at):
    parsed_due_at = parse_due_at(raw_due_at=raw_due_at, default_timezone=test_timezone)

    assert parsed_due_at == expected_due_at


def test_prase_due_at_raises_when_format_is_unknown():
    with pytest.raises(ValueError):
        parse_due_at("25/09/2035 12:45")


@pytest.mark.parametrize(
    ("parsed_args", "expected_due_at"),
    [
        (
            {
                "description": "Learn pytest",
                "due_at": None,
            },
            None,
        ),
        (
            {"description": "Learn pytest", "due_at": FUTURE_DUE_AT.isoformat()},
            FUTURE_DUE_AT,
        ),
    ],
)
def test_cli_adds_task(parsed_args, expected_due_at, service, repository, capsys):
    args = argparse.Namespace(**parsed_args)

    add_task(args, service)
    tasks = repository.get_all()
    captured = capsys.readouterr()

    assert len(tasks) == 1
    assert tasks[0].description == "Learn pytest"
    assert tasks[0].status == ValidStatuses.TODO
    assert tasks[0].due_at == expected_due_at
    assert "Task added successfully" in captured.out


def test_cli_add_task_prints_error_when_description_is_too_short(
    service, repository, capsys
):
    args = argparse.Namespace(
        description="ab",
        due_at=None,
    )

    add_task(args, service)
    captured = capsys.readouterr()

    assert repository.get_all() == []
    assert "Description must contain at least 3 characters." in captured.out
    assert "Task added successfully" not in captured.out


def test_add_task_prints_error_when_due_at_is_not_in_the_future(
    service, capsys, repository
):
    args = argparse.Namespace(description="Description", due_at="01.02.2003")

    add_task(args, service)
    captured = capsys.readouterr()

    assert repository.get_all() == []
    assert "Due date must be later then current time" in captured.out
    assert "Task added successfully" not in captured.out


def test_add_task_print_error_when_due_at_format_is_not_supported(
    service, capsys, repository
):
    args = argparse.Namespace(description="Description", due_at="25/09/2030 18:30")

    add_task(args, service)
    captured = capsys.readouterr()

    assert repository.get_all() == []
    assert "Invalid deadline format" in captured.out
    assert "Task added successfully" not in captured.out


def test_cli_lists_all_tasks(service, repository, capsys):
    repository.create(description="First task", status=ValidStatuses.TODO)

    repository.create(description="Second task", status=ValidStatuses.DONE)

    repository.create(description="Third task", status=ValidStatuses.IN_PROGRESS)

    args = argparse.Namespace(status=None)

    list_tasks(args, service)
    captured = capsys.readouterr()

    assert "First task" in captured.out
    assert "Second task" in captured.out
    assert "Third task" in captured.out


def test_cli_list_tasks_prints_message_when_empty_repo(service, capsys):
    args = argparse.Namespace(status=None)

    list_tasks(args, service)
    captured = capsys.readouterr()

    assert "No tasks found" in captured.out


def test_cli_lists_tasks_filtered_by_status(service, repository, capsys):
    repository.create(description="First TODO", status=ValidStatuses.TODO)

    repository.create(description="DONE task", status=ValidStatuses.DONE)

    repository.create(description="Second TODO", status=ValidStatuses.TODO)

    args = argparse.Namespace(status="todo")

    list_tasks(args, service)
    captured = capsys.readouterr()

    assert "First TODO" in captured.out
    assert "Second TODO" in captured.out
    assert "DONE task" not in captured.out


def test_cli_list_tasks_prints_message_when_filter_has_no_results(
    service,
    repository,
    capsys,
):
    repository.create(
        description="Todo task",
        status=ValidStatuses.TODO,
    )
    args = argparse.Namespace(
        status="done",
    )

    list_tasks(args, service)
    captured = capsys.readouterr()

    assert "No tasks found" in captured.out


def test_cli_updates_task(service, repository, capsys):
    task = repository.create(description="Old description", status=ValidStatuses.TODO)
    args = argparse.Namespace(task_id=task.id, description="New Description")

    update_task(args, service)
    captured = capsys.readouterr()
    updated_task = repository.get_by_id(task.id)

    assert "Task updated successfully" in captured.out
    assert updated_task is not None
    assert updated_task.description == "New Description"
    assert updated_task.status == ValidStatuses.TODO


def test_cli_update_task_prints_error_when_id_is_missing(service, capsys):
    args = argparse.Namespace(task_id=999, description="New Description")

    update_task(args, service)
    captured = capsys.readouterr()

    assert "Task with id 999 not found" in captured.out
    assert "Task updated successfully" not in captured.out


def test_cli_update_task_rejects_short_description(service, repository, capsys):
    task = repository.create(
        description="Old Description",
        status=ValidStatuses.TODO,
    )
    args = argparse.Namespace(task_id=task.id, description="ab")

    update_task(args, service)
    captured = capsys.readouterr()
    updated_task = repository.get_by_id(task.id)

    assert updated_task is not None
    assert updated_task.description == "Old Description"
    assert updated_task.status == ValidStatuses.TODO
    assert "Description must contain at least 3 characters." in captured.out
    assert "Task updated successfully" not in captured.out


def test_cli_marks_task_done(service, repository, capsys):
    task = repository.create(
        description="Description",
        status=ValidStatuses.TODO,
    )
    args = argparse.Namespace(task_id=task.id)

    mark_done(args, service)
    captured = capsys.readouterr()
    updated_task = repository.get_by_id(task.id)

    assert "Task marked as done" in captured.out
    assert updated_task is not None
    assert updated_task.status == ValidStatuses.DONE
    assert updated_task.description == "Description"


def test_cli_mark_done_prints_error_when_id_is_missing(service, capsys):
    args = argparse.Namespace(task_id=999)

    mark_done(args, service)

    captured = capsys.readouterr()
    assert "Task with id 999 not found" in captured.out
    assert "Task marked as done" not in captured.out


def test_cli_marks_task_in_progress(service, repository, capsys):
    task = repository.create(
        description="Description",
        status=ValidStatuses.TODO,
    )
    args = argparse.Namespace(task_id=task.id)

    mark_in_progress(args, service)
    captured = capsys.readouterr()
    updated_task = repository.get_by_id(task.id)

    assert "Task marked as in progress" in captured.out
    assert updated_task is not None
    assert updated_task.status == ValidStatuses.IN_PROGRESS
    assert updated_task.description == "Description"


def test_cli_mark_in_progress_prints_error_when_id_is_missing(service, capsys):
    args = argparse.Namespace(task_id=999)

    mark_in_progress(args, service)

    captured = capsys.readouterr()
    assert "Task with id 999 not found" in captured.out
    assert "Task marked as in progress" not in captured.out


def test_cli_deletes_task(service, repository, capsys):
    task = repository.create(description="Description", status=ValidStatuses.TODO)
    args = argparse.Namespace(task_id=task.id)

    delete_task(args, service)

    captured = capsys.readouterr()
    assert "Task deleted successfully" in captured.out
    assert repository.get_by_id(task.id) is None


def test_cli_delete_missing_task_prints_error(service, capsys):
    args = argparse.Namespace(task_id=999)

    delete_task(args, service)

    captured = capsys.readouterr()
    assert "Task with id 999 not found" in captured.out
    assert "Task deleted successfully" not in captured.out

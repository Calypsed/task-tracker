import pytest
import argparse
from main_cli import (
    add_task,
    list_tasks,
    update_task,
    mark_done,
    mark_in_progress,
    delete_task,
)
from services import TaskService
from fakes import FakeTaskRepository
from models import ValidStatuses


@pytest.fixture
def repository():
    return FakeTaskRepository()


@pytest.fixture
def service(repository):
    return TaskService(repository)


def test_cli_adds_task(service, repository, capsys):
    args = argparse.Namespace(
        description="Learn pytest",
    )

    add_task(args, service)

    tasks = repository.get_all()
    captured = capsys.readouterr()

    assert len(tasks) == 1
    assert tasks[0].description == "Learn pytest"
    assert tasks[0].status == ValidStatuses.TODO
    assert "Task added successfully" in captured.out


def test_cli_add_task_prints_error_when_description_is_too_short(
    service, repository, capsys
):
    args = argparse.Namespace(
        description="ab",
    )

    add_task(args, service)

    captured = capsys.readouterr()

    assert repository.get_all() == []
    assert "Description must contain at least 3 characters." in captured.out
    assert "Task added successfully" not in captured.out


def test_cli_lists_all_tasks(service, repository, capsys):
    repository.create("First task", ValidStatuses.TODO)
    repository.create("Second task", ValidStatuses.DONE)
    repository.create("Third task", ValidStatuses.IN_PROGRESS)

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
    repository.create("First TODO", ValidStatuses.TODO)
    repository.create("DONE task", ValidStatuses.DONE)
    repository.create("Second TODO", ValidStatuses.TODO)

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
        "Todo task",
        ValidStatuses.TODO,
    )

    args = argparse.Namespace(
        status="done",
    )

    list_tasks(args, service)

    captured = capsys.readouterr()

    assert "No tasks found" in captured.out


def test_cli_updates_task(service, repository, capsys):
    task = repository.create("Old description", ValidStatuses.TODO)

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
    task = repository.create("Old Description", ValidStatuses.TODO)

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
    task = repository.create("Description", ValidStatuses.TODO)

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
    task = repository.create("Description", ValidStatuses.TODO)

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
    task = repository.create("Description", ValidStatuses.TODO)

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

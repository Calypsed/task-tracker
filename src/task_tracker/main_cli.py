import argparse

from task_tracker.exceptions import (
    TaskNotFoundError,
    InvalidTaskDescriptionError,
    InvalidTaskDueAtError,
)
from task_tracker.models import ValidStatuses
from task_tracker.repositories.repository_factory import create_repository
from task_tracker.services import TaskService
from dotenv import load_dotenv
from datetime import datetime, tzinfo, date, time
from tzlocal import get_localzone


def parse_iso_date(raw_due_at: str) -> datetime:
    due_at_date = date.fromisoformat(raw_due_at)
    due_at_datetime = datetime.combine(date=due_at_date, time=time(23, 59, 59))
    return due_at_datetime


def parse_iso_datetime(raw_due_at: str) -> datetime:
    return datetime.fromisoformat(raw_due_at)


def parse_human_date(raw_due_at: str) -> datetime:
    due_at_datetime = datetime.strptime(raw_due_at, "%d.%m.%Y")
    due_at_datetime = due_at_datetime.replace(hour=23, minute=59, second=59)
    return due_at_datetime


def parse_human_datetime(raw_due_at: str) -> datetime:
    return datetime.strptime(raw_due_at, "%d.%m.%Y %H:%M")


def parse_due_at(
    raw_due_at: str | None,
    default_timezone: tzinfo | None = None,
) -> datetime | None:
    if raw_due_at is None:
        return None

    parsers = [
        parse_iso_date,
        parse_iso_datetime,
        parse_human_date,
        parse_human_datetime,
    ]

    for parser in parsers:
        try:
            due_at = parser(raw_due_at)
        except ValueError:
            continue
        break
    else:
        raise ValueError

    if due_at.tzinfo is None:
        if default_timezone is None:
            default_timezone = get_localzone()

        due_at = due_at.replace(tzinfo=default_timezone)

    return due_at


def add_task(args, service: TaskService):
    try:
        due_at = parse_due_at(args.due_at)
    except ValueError:
        print(
            "Invalid deadline format\n"
            "Supported formats:\n"
            "DD.MM.YYYY\n"
            "DD.MM.YYYY HH:MM\n"
            "ISO 8601, e.g. 2030-02-01T18:30:00+03:00"
        )
        return

    try:
        task = service.create_task(description=args.description, due_at=due_at)
    except InvalidTaskDescriptionError:
        print("Description must contain at least 3 characters.")
        return
    except InvalidTaskDueAtError:
        print("Due date must be later then current time.")
        return

    print(f"Task added successfully (ID={task.id})")


def update_task(args, service: TaskService):
    try:
        service.update_task(
            args.task_id,
            description=args.description,
        )
    except TaskNotFoundError as error:
        print(error)
        return
    except InvalidTaskDescriptionError:
        print("Description must contain at least 3 characters.")
        return

    print("Task updated successfully")


def delete_task(args, service: TaskService):
    try:
        service.delete_task(args.task_id)
    except TaskNotFoundError as error:
        print(error)
        return

    print("Task deleted successfully")


def mark_in_progress(args, service: TaskService):
    try:
        service.update_task(
            args.task_id,
            status=ValidStatuses.IN_PROGRESS,
        )
    except TaskNotFoundError as error:
        print(error)
        return

    print("Task marked as in progress")


def mark_done(args, service: TaskService):
    try:
        service.update_task(
            args.task_id,
            status=ValidStatuses.DONE,
        )
    except TaskNotFoundError as error:
        print(error)
        return

    print("Task marked as done")


def list_tasks(args, service: TaskService):
    status = None

    if args.status is not None:
        status = ValidStatuses(args.status)

    tasks = service.get_tasks(status)

    if not tasks:
        print("No tasks found")
        return

    for task in tasks:
        print(f"{task.id}: {task.description} [{task.status.value}]")


def create_parser():
    parser = argparse.ArgumentParser(
        prog="task-tracker",
        description="Task Tracker CLI",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # add
    add_parser = subparsers.add_parser(
        "add",
        help="Add a new task",
    )
    add_parser.add_argument(
        "description",
        help="Task description",
    )
    add_parser.add_argument(
        "-d",
        "--due",
        dest="due_at",
        help="Task deadline",
    )
    add_parser.set_defaults(func=add_task)

    # update
    update_parser = subparsers.add_parser(
        "update",
        help="Update task description",
    )
    update_parser.add_argument(
        "task_id",
        type=int,
        help="Task ID",
    )
    update_parser.add_argument(
        "description",
        help="New task description",
    )
    update_parser.set_defaults(func=update_task)

    # delete
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete a task",
    )
    delete_parser.add_argument(
        "task_id",
        type=int,
        help="Task ID",
    )
    delete_parser.set_defaults(func=delete_task)

    # mark-in-progress
    progress_parser = subparsers.add_parser(
        "mark-in-progress",
        help="Mark task as in progress",
    )
    progress_parser.add_argument(
        "task_id",
        type=int,
        help="Task ID",
    )
    progress_parser.set_defaults(func=mark_in_progress)

    # mark-done
    done_parser = subparsers.add_parser(
        "mark-done",
        help="Mark task as done",
    )
    done_parser.add_argument(
        "task_id",
        type=int,
        help="Task ID",
    )
    done_parser.set_defaults(func=mark_done)

    # list
    list_parser = subparsers.add_parser(
        "list",
        help="List tasks",
    )
    list_parser.add_argument(
        "status",
        nargs="?",
        choices=[status.value for status in ValidStatuses],
        help="Filter tasks by status",
    )
    list_parser.set_defaults(func=list_tasks)

    return parser


def main():
    load_dotenv()

    parser = create_parser()

    args = parser.parse_args()

    repository = create_repository()
    service = TaskService(repository)

    args.func(args, service)


if __name__ == "__main__":
    main()

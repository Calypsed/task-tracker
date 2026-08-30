import argparse

from exceptions import TaskNotFoundError, InvalidTaskDescriptionError
from models import ValidStatuses
from repositories.factory import create_repository
from services import TaskService
from dotenv import load_dotenv

load_dotenv()

repository = create_repository()
service = TaskService(repository)


def add_task(args):
    try:
        task = service.create_task(args.description)
    except InvalidTaskDescriptionError:
        print("Description must contain at least 3 characters.")

    print(f"Task added successfully (ID: {task.id})")


def update_task(args):
    try:
        service.update_task_description(
            args.task_id,
            args.description,
        )
    except TaskNotFoundError as error:
        print(error)
        return

    print("Task updated successfully")


def delete_task(args):
    try:
        service.delete_task(args.task_id)
    except TaskNotFoundError as error:
        print(error)
        return

    print("Task deleted successfully")


def mark_in_progress(args):
    try:
        service.update_task_status(
            args.task_id,
            ValidStatuses.IN_PROGRESS,
        )
    except TaskNotFoundError as error:
        print(error)
        return

    print("Task marked as in progress")


def mark_done(args):
    try:
        service.update_task_status(
            args.task_id,
            ValidStatuses.DONE,
        )
    except TaskNotFoundError as error:
        print(error)
        return

    print("Task marked as done")


def list_tasks(args):
    status = None

    if args.status is not None:
        status = ValidStatuses(args.status)

    tasks = service.get_tasks(status)

    if not tasks:
        print("No tasks found")
        return

    for task in tasks:
        print(f"{task.id}: {task.description} [{task.status.value}]")


def main():
    parser = argparse.ArgumentParser(
        prog="task-cli",
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

    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    main()

import sys
import json
from datetime import datetime

FILENAME = "tasks.json"
STATUS_DONE = "done"
STATUS_TODO = "todo"
STATUS_IN_PROGRESS = "in-progress"
KEY_NEXT_ID = "nextID"
KEY_DELETED_IDS = "deletedIDs"
KEY_TASKS = "tasks"
KEY_ID = "task_id"
KEY_DESCRIPTION = "description"
KEY_STATUS = "status"
KEY_CREATED_AT = "createdAt"
KEY_UPDATED_AT = "updatedAt"
ERROR_NO_TASKS = "No tasks at the moment!"
ERROR_ID_NOT_FOUND = "No task with such id found!"
ERROR_ID_NOT_INT = "Error: ID must be a number"
ARGS_NUM_FOR_ADD_COMMAND = 3
ARGS_NUM_FOR_DELETE_COMMAND = 3
ARGS_NUM_FOR_UPDATE_COMMAND = 4
ARGS_NUM_FOR_LIST_ALL_COMMAND = 2
ARGS_NUM_FOR_LIST_STATUS_COMMAND = 3
ARGS_NUM_FOR_SET_STATUS_COMMAND = 3
ARGS_NUM_MINIMAL = 2


class TaskTracker:
    def __init__(self, filename):
        self.filename = filename
        data = self._load_tasks()
        self.next_ID = data[KEY_NEXT_ID]
        self.deleted_IDs = data[KEY_DELETED_IDS]
        tasks_data = data[KEY_TASKS]
        self.tasks = [
            Task(
                t[KEY_ID],
                t[KEY_DESCRIPTION],
                t[KEY_STATUS],
                datetime.fromisoformat(t[KEY_CREATED_AT]),
                datetime.fromisoformat(t[KEY_UPDATED_AT]),
            )
            for t in tasks_data
        ]

    def _load_tasks(self):
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # File doesn't exist or JSON is corrupted
            empty_data = {KEY_NEXT_ID: 0, KEY_DELETED_IDS: [], KEY_TASKS: []}
            with open(self.filename, "w") as f:
                json.dump(empty_data, f)
            return empty_data

    def _write_tasks(self):
        with open(self.filename, "w") as f:
            json.dump(
                {
                    KEY_NEXT_ID: self.next_ID,
                    KEY_DELETED_IDS: self.deleted_IDs,
                    KEY_TASKS: [t.to_dict() for t in self.tasks],
                },
                f,
            )

    def list_tasks(self, status=None):
        if self.tasks:
            if status:
                task_found = False
                for t in self.tasks:
                    if t.get_status() == status:
                        print(t)
                        task_found = True
                if not task_found:
                    print(f'No tasks found with status "{status}"')
            else:
                for t in self.tasks:
                    print(t)
        else:
            print(ERROR_NO_TASKS)

    def add_task(self, description):
        if (
            description and description.strip()
        ):  # ' ' - whitespace is not a valid description
            new_ID = 0
            if self.deleted_IDs:
                new_ID = min(self.deleted_IDs)
                self.deleted_IDs.remove(new_ID)
            else:
                new_ID = self.next_ID
                self.next_ID += 1

            now = datetime.now()
            new_task = Task(new_ID, description, STATUS_TODO, now, now)
            self.tasks.append(new_task)
            self._write_tasks()
            print(f"Task added successfully (ID: {self.tasks[-1].get_id()})")
        else:
            print("The description is empty!")

    def delete_task(self, task_id):
        id_found = False
        for i, t in enumerate(self.tasks):
            if t.get_id() == task_id:
                id_found = True
                self.tasks.pop(i)
                self.deleted_IDs.append(task_id)
                break
        if id_found:
            print("Task deleted successfully!")
        else:
            print(ERROR_ID_NOT_FOUND)
        self._write_tasks()

    def _find_task(self, task_id):
        for t in self.tasks:
            if t.get_id() == task_id:
                return t
        return None

    def update_task_description(self, task_id, description):
        task = self._find_task(task_id)
        if task:
            task.set_description(description)
            task.set_updated_at(datetime.now())
            print("Task description updated successfully!")
        else:
            print(ERROR_ID_NOT_FOUND)
            return
        self._write_tasks()

    def update_task_status(self, task_id, status):
        valid_statuses = {STATUS_DONE, STATUS_IN_PROGRESS, STATUS_TODO}
        if status not in valid_statuses:
            print(
                f"Available statuses: "
                f"{STATUS_TODO}, {STATUS_IN_PROGRESS}, {STATUS_DONE}"
            )
            return

        task = self._find_task(task_id)
        if task:
            task.set_status(status)
            task.set_updated_at(datetime.now())
            print(f"Task status updated to '{status}' successfully!")
        else:
            print(ERROR_ID_NOT_FOUND)
        self._write_tasks()


class Task:
    def __init__(self, task_id, description, status, created_at, updated_at):
        self.task_id = task_id
        self.description = description
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            KEY_ID: self.task_id,
            KEY_DESCRIPTION: self.description,
            KEY_STATUS: self.status,
            KEY_CREATED_AT: self.created_at.isoformat(),
            KEY_UPDATED_AT: self.updated_at.isoformat(),
        }

    def get_id(self):
        return self.task_id

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status

    def set_description(self, description):
        self.description = description

    def set_updated_at(self, updated_at):
        self.updated_at = updated_at

    def __str__(self):
        return f"{self.task_id}) {self.description} | {self.status}"


def main():
    if len(sys.argv) < ARGS_NUM_MINIMAL:
        print_help()
        return

    tracker = TaskTracker(FILENAME)
    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) != ARGS_NUM_FOR_ADD_COMMAND:
            print("Usage: task-cli add <description>")
            return
        tracker.add_task(sys.argv[2])

    elif command == "list":
        if len(sys.argv) == ARGS_NUM_FOR_LIST_ALL_COMMAND:
            tracker.list_tasks()
        elif len(sys.argv) == ARGS_NUM_FOR_LIST_STATUS_COMMAND:
            tracker.list_tasks(sys.argv[2])
        else:
            print("Usage: task-cli list [todo|done|in-progress]")
            return

    elif command == "update":
        if len(sys.argv) != ARGS_NUM_FOR_UPDATE_COMMAND:
            print("Usage: task-cli update <id> <new_description>")
            return
        try:
            task_id = int(sys.argv[2])
        except ValueError:
            print(ERROR_ID_NOT_INT)
            return
        description = sys.argv[3]
        tracker.update_task_description(task_id, description)

    elif command == "delete":
        if len(sys.argv) != ARGS_NUM_FOR_DELETE_COMMAND:
            print("Usage: task-cli delete <id>")
            return
        try:
            task_id = int(sys.argv[2])
        except ValueError:
            print(ERROR_ID_NOT_INT)
            return
        tracker.delete_task(task_id)

    elif command == "mark-in-progress":
        if len(sys.argv) != ARGS_NUM_FOR_SET_STATUS_COMMAND:
            print("Usage: task-cli mark-in-progress <id>")
            return
        try:
            task_id = int(sys.argv[2])
        except ValueError:
            print(ERROR_ID_NOT_INT)
        tracker.update_task_status(task_id, STATUS_IN_PROGRESS)

    elif command == "mark-done":
        if len(sys.argv) != ARGS_NUM_FOR_SET_STATUS_COMMAND:
            print("Usage: task-cli mark-done <id>")
            return
        try:
            task_id = int(sys.argv[2])
        except ValueError:
            print(ERROR_ID_NOT_INT)
        tracker.update_task_status(task_id, STATUS_DONE)

    elif command == "help":
        print_help()

    else:
        print(f"Unknown command: {command}")
        print("Type 'help' for available commands")


def print_help():
    print("""
Task Tracker CLI - Manage your tasks

Commands:
  add <description>              - Add a new task
  list                           - List all tasks
  list <status>                  - List tasks by status (todo, done, in-progress)
  update <id> <description>      - Update task description
  delete <id>                    - Delete a task
  mark-in-progress <id>          - Mark task as in-progress
  mark-done <id>                 - Mark task as done
  help                           - Show this help message

Examples:
  task-cli add "Buy groceries"
  task-cli list done
  task-cli update 1 "Buy groceries and cook dinner"
    """)


if __name__ == "__main__":
    main()

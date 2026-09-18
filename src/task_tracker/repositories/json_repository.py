import json
from task_tracker.models import Task
import task_tracker.constants as constants
from datetime import datetime, timezone
from task_tracker.models import ValidStatuses


class JsonTaskRepository:
    def __init__(self, filename: str) -> None:
        self._filename = filename

    @staticmethod
    def _to_dict(task: Task) -> dict:
        str_due_at = task.due_at.isoformat() if task.due_at is not None else None
        return {
            constants.KEY_STORAGE_ID: task.id,
            constants.KEY_STORAGE_DESCRIPTION: task.description,
            constants.KEY_STORAGE_STATUS: task.status,
            constants.KEY_STORAGE_CREATED_AT: task.created_at.isoformat(),
            constants.KEY_STORAGE_UPDATED_AT: task.updated_at.isoformat(),
            constants.KEY_STORAGE_DUE_AT: str_due_at,
        }

    @staticmethod
    def _to_task(data: dict) -> Task:
        raw_due_at = data.get(constants.KEY_STORAGE_DUE_AT)
        due_at = datetime.fromisoformat(raw_due_at) if raw_due_at is not None else None
        return Task(
            id=data[constants.KEY_STORAGE_ID],
            description=data[constants.KEY_STORAGE_DESCRIPTION],
            status=ValidStatuses(data[constants.KEY_STORAGE_STATUS]),
            created_at=datetime.fromisoformat(data[constants.KEY_STORAGE_CREATED_AT]),
            updated_at=datetime.fromisoformat(data[constants.KEY_STORAGE_UPDATED_AT]),
            due_at=due_at,
        )

    def _load_data(self) -> dict:
        try:
            with open(self._filename, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            empty_data = {
                constants.KEY_JSON_NEXT_ID: 1,
                constants.KEY_TASKS: [],
            }
            return empty_data

    def _save_data(self, data: dict):
        with open(self._filename, "w") as f:
            json.dump(
                data,
                f,
            )

    def create(
        self, description: str, status: ValidStatuses, due_at: datetime | None = None
    ) -> Task:
        data = self._load_data()
        next_id = data[constants.KEY_JSON_NEXT_ID]
        dict_tasks = data[constants.KEY_TASKS]

        now = datetime.now(timezone.utc)
        task = Task(
            id=next_id,
            description=description,
            status=status,
            created_at=now,
            updated_at=now,
            due_at=due_at,
        )
        dict_task = self._to_dict(task)
        dict_tasks.append(dict_task)
        next_id += 1

        data = {constants.KEY_JSON_NEXT_ID: next_id, constants.KEY_TASKS: dict_tasks}
        self._save_data(data)
        return task

    def get_all(self, status: ValidStatuses | None = None) -> list[Task]:
        data = self._load_data()
        dict_tasks = data[constants.KEY_TASKS]

        if status is None:
            tasks = [self._to_task(dict_task) for dict_task in dict_tasks]
        else:
            str_status = status.value
            tasks = [
                self._to_task(dict_task)
                for dict_task in dict_tasks
                if dict_task[constants.KEY_STORAGE_STATUS] == str_status
            ]

        return tasks

    def get_by_id(self, task_id: int) -> Task | None:
        data = self._load_data()
        dict_tasks = data[constants.KEY_TASKS]

        for dict_task in dict_tasks:
            if dict_task[constants.KEY_STORAGE_ID] == task_id:
                task = self._to_task(dict_task)
                return task
        return None

    def update(
        self,
        task_id: int,
        *,
        description: str | None = None,
        status: ValidStatuses | None = None,
    ) -> Task | None:
        data = self._load_data()
        dict_tasks = data[constants.KEY_TASKS]

        for index, dict_task in enumerate(dict_tasks):
            if dict_task[constants.KEY_STORAGE_ID] == task_id:
                task = self._to_task(dict_task)

                if description is None and status is None:
                    return task

                if description is not None:
                    task.description = description
                if status is not None:
                    task.status = status

                task.updated_at = datetime.now(timezone.utc)

                updated_dict_task = self._to_dict(task)
                dict_tasks[index] = updated_dict_task
                self._save_data(data)
                return task

        return None

    def delete(self, task_id: int) -> bool:
        data = self._load_data()
        dict_tasks = data[constants.KEY_TASKS]

        for index, dict_task in enumerate(dict_tasks):
            if dict_task[constants.KEY_STORAGE_ID] == task_id:
                dict_tasks.pop(index)
                self._save_data(data)
                return True

        return False

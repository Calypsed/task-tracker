import json
from models import Task
import constants
from datetime import datetime, timezone
from models import ValidStatuses


class JsonTaskRepository:
    def __init__(self, filename: str) -> None:
        self._filename = filename
        data = self._load_tasks()
        self._next_ID = data[constants.KEY_NEXT_ID]
        tasks_data = data[constants.KEY_TASKS]
        self._tasks = [self._to_task(t) for t in tasks_data]

    @staticmethod
    def _to_dict(task: Task) -> dict:
        return {
            constants.KEY_ID: task.id,
            constants.KEY_DESCRIPTION: task.description,
            constants.KEY_STATUS: task.status,
            constants.KEY_CREATED_AT: task.created_at.isoformat(),
            constants.KEY_UPDATED_AT: task.updated_at.isoformat(),
        }

    @staticmethod
    def _to_task(data: dict) -> Task:
        return Task(
            id=data[constants.KEY_ID],
            description=data[constants.KEY_DESCRIPTION],
            status=ValidStatuses(data[constants.KEY_STATUS]),
            created_at=datetime.fromisoformat(data[constants.KEY_CREATED_AT]),
            updated_at=datetime.fromisoformat(data[constants.KEY_UPDATED_AT]),
        )

    def _load_tasks(self):
        try:
            with open(self._filename, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            empty_data = {
                constants.KEY_NEXT_ID: 0,
                constants.KEY_TASKS: [],
            }
            with open(self._filename, "w") as f:
                json.dump(empty_data, f)
            return empty_data

    def _write_tasks(self):
        with open(self._filename, "w") as f:
            json.dump(
                {
                    constants.KEY_NEXT_ID: self._next_ID,
                    constants.KEY_TASKS: [self._to_dict(t) for t in self._tasks],
                },
                f,
            )

    def create(self, description: str, status: ValidStatuses) -> Task:
        new_ID = self._next_ID
        self._next_ID += 1

        now = datetime.now(timezone.utc)
        task = Task(
            id=new_ID,
            description=description,
            status=status,
            created_at=now,
            updated_at=now,
        )

        self._tasks.append(task)
        self._write_tasks()

        return task

    def get_all(self, status: ValidStatuses | None = None) -> list[Task]:
        if status is None:
            return self._tasks.copy()

        return [t for t in self._tasks if t.status == status]

    def get_by_id(self, task_id: int) -> Task | None:
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def update(
        self,
        task_id: int,
        *,
        description: str | None = None,
        status: ValidStatuses | None = None,
    ) -> Task | None:
        task = self.get_by_id(task_id)

        if task is None:
            return None

        if description is not None:
            task.description = description

        if status is not None:
            task.status = status

        task.updated_at = datetime.now(timezone.utc)

        self._write_tasks()

        return task

    def delete(self, task_id: int) -> bool:
        for i, task in enumerate(self._tasks):
            if task.id == task_id:
                self._tasks.pop(i)
                self._write_tasks()
                return True

        return False

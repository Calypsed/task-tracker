import json
from models import Task
import constants
from datetime import datetime
from typing import List
from models import ValidStatuses

class JsonTaskRepository:
    def __init__(self, filename: str) -> None:
        self._filename = filename
        data = self._load_tasks()
        self._next_ID = data[constants.KEY_NEXT_ID]
        self._deleted_IDs = data[constants.KEY_DELETED_IDS]
        tasks_data = data[constants.KEY_TASKS]
        self._tasks = [
            Task(
                t[constants.KEY_ID],
                t[constants.KEY_DESCRIPTION],
                t[constants.KEY_STATUS],
                datetime.fromisoformat(t[constants.KEY_CREATED_AT]),
                datetime.fromisoformat(t[constants.KEY_UPDATED_AT]),
            )
            for t in tasks_data
        ]

    def _load_tasks(self):
            try:
                with open(self._filename, "r") as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                # File doesn't exist or JSON is corrupted
                empty_data = {constants.KEY_NEXT_ID: 0,
                               constants.KEY_DELETED_IDS: [], constants.KEY_TASKS: []}
                with open(self._filename, "w") as f:
                    json.dump(empty_data, f)
                return empty_data
    
    def _write_tasks(self):
            with open(self._filename, "w") as f:
                json.dump(
                    {
                        constants.KEY_NEXT_ID: self._next_ID,
                        constants.KEY_DELETED_IDS: self._deleted_IDs,
                        constants.KEY_TASKS: [t.to_dict() for t in self._tasks],
                    },
                    f,
                )

    def create(self, task: Task) -> Task:
        new_ID = 0
        if self._deleted_IDs:
            new_ID = min(self._deleted_IDs)
            self._deleted_IDs.remove(new_ID)
        else:
            new_ID = self._next_ID
            self._next_ID += 1

        task.id = new_ID
        self._tasks.append(task)
        self._write_tasks()

        return task

    def get_all(self, status=None) -> List[Task]:
         if status is None:
             return self._tasks
         
         return [t for t in self._tasks if t.status == status]

    def get_by_id(self, task_id: int) -> Task | None:
        for t in self._tasks:
            if t.id == task_id:
                return t
        return None

    def update_description(self, task_id: int, description: str) -> Task | None:
        task = self.get_by_id(task_id)

        if task is None:
            return None

        task.description = description
        task.updated_at = datetime.now()

        self._write_tasks()

        return task

    def update_status(self, task_id: int, status: ValidStatuses) -> Task | None:
        task = self.get_by_id(task_id)

        if task is None:
            return None

        task.status = status
        task.updated_at = datetime.now()

        self._write_tasks()

        return task

    def delete(self, task_id: int) -> None:
        for i, t in enumerate(self._tasks):
            if t.id == task_id:
                self._tasks.pop(i)
                self._deleted_IDs.append(task_id)
                break
        self._write_tasks()

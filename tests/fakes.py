from datetime import datetime, timezone

from models import Task, ValidStatuses


class FakeTaskRepository:
    def __init__(self) -> None:
        self.tasks: list[Task] = []
        self.next_id = 0

    def create(self, description: str, status: ValidStatuses) -> Task:
        now = datetime.now(timezone.utc)

        task = Task(
            id=self.next_id,
            description=description,
            status=status,
            created_at=now,
            updated_at=now,
        )

        self.tasks.append(task)
        self.next_id += 1

        return task

    def get_all(self, status: ValidStatuses | None = None) -> list[Task]:
        if status is None:
            return self.tasks.copy()

        return [task for task in self.tasks if task.status == status]

    def get_by_id(self, task_id: int) -> Task | None:
        for task in self.tasks:
            if task.id == task_id:
                return task

        return None

    def update_description(
        self,
        task_id: int,
        description: str,
    ) -> Task | None:
        task = self.get_by_id(task_id)

        if task is None:
            return None

        task.description = description
        task.updated_at = datetime.now(timezone.utc)

        return task

    def update_status(
        self,
        task_id: int,
        status: ValidStatuses,
    ) -> Task | None:
        task = self.get_by_id(task_id)

        if task is None:
            return None

        task.status = status
        task.updated_at = datetime.now(timezone.utc)

        return task

    def delete(self, task_id: int) -> bool:
        task = self.get_by_id(task_id)

        if task is None:
            return False

        self.tasks.remove(task)

        return True

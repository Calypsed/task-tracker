from typing import Protocol
from task_tracker.models import Task, ValidStatuses
from datetime import datetime


class TaskRepository(Protocol):
    def create(
        self, *, description: str, status: ValidStatuses, due_at: datetime | None = None
    ) -> Task: ...

    def get_all(
        self,
        *,
        status: ValidStatuses | None = None,
    ) -> list[Task]:
        """Return tasks ordered by id in ascending order."""
        ...

    def get_by_id(self, task_id: int) -> Task | None: ...

    def update(
        self,
        task_id: int,
        *,
        description: str | None = None,
        status: ValidStatuses | None = None,
    ) -> Task | None: ...

    def delete(self, task_id: int) -> bool: ...

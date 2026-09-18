from task_tracker.models import Task, ValidStatuses
from task_tracker.exceptions import (
    TaskNotFoundError,
    InvalidTaskDescriptionError,
    InvalidTaskDueAtError,
)
from task_tracker.repositories.protocol import TaskRepository
from datetime import datetime, timezone
from collections.abc import Callable


class TaskService:
    def __init__(
        self,
        repository: TaskRepository,
        now_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = repository
        self._now_provider = (
            now_provider
            if now_provider is not None
            else lambda: datetime.now(timezone.utc)
        )

    def _validate_description(self, description: str) -> str:
        description = description.strip()

        if len(description) < 3:
            raise InvalidTaskDescriptionError()

        return description

    def _validate_due_at(self, due_at: datetime | None = None) -> datetime | None:
        if due_at is None:
            return None

        if due_at.tzinfo is None or due_at.utcoffset() is None:
            raise InvalidTaskDueAtError()

        now = self._now_provider()

        if due_at <= now:
            raise InvalidTaskDueAtError()

        return due_at

    def get_tasks(self, status: ValidStatuses | None = None) -> list[Task]:
        return self.repository.get_all(status=status)

    def create_task(self, *, description: str, due_at: datetime | None = None) -> Task:
        description = self._validate_description(description)
        due_at = self._validate_due_at(due_at)

        return self.repository.create(
            description=description, status=ValidStatuses.TODO, due_at=due_at
        )

    def delete_task(self, task_id: int) -> None:
        deleted = self.repository.delete(task_id)

        if not deleted:
            raise TaskNotFoundError(task_id)

    def get_task_by_id(self, task_id: int) -> Task:
        task = self.repository.get_by_id(task_id)

        if task is None:
            raise TaskNotFoundError(task_id)

        return task

    def update_task(
        self,
        task_id: int,
        *,
        description: str | None = None,
        status: ValidStatuses | None = None,
    ) -> Task:
        if description is not None:
            description = self._validate_description(description)

        task = self.repository.update(
            task_id,
            description=description,
            status=status,
        )

        if task is None:
            raise TaskNotFoundError(task_id)

        return task

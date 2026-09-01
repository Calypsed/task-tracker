from models import Task, ValidStatuses
from exceptions import TaskNotFoundError, InvalidTaskDescriptionError
from repositories.protocol import TaskRepository


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def _validate_description(self, description: str) -> str:
        description = description.strip()

        if len(description) < 3:
            raise InvalidTaskDescriptionError()

        return description

    def get_tasks(self, status: ValidStatuses | None = None) -> list[Task]:
        return self.repository.get_all(status)

    def create_task(self, description: str) -> Task:
        description = self._validate_description(description)

        return self.repository.create(
            description,
            ValidStatuses.TODO,
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

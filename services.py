from models import Task, ValidStatuses
from exceptions import TaskNotFoundError
from repositories.protocol import TaskRepository


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def get_tasks(self, status: ValidStatuses | None = None) -> list[Task]:
        return self.repository.get_all(status)

    def create_task(self, description: str) -> Task:
        return self.repository.create(
            description=description, status=ValidStatuses.TODO
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

    def update_task_description(self, task_id: int, description: str) -> Task:
        task = self.repository.update_description(task_id, description)

        if task is None:
            raise TaskNotFoundError(task_id)

        return task

    def update_task_status(self, task_id: int, status: ValidStatuses) -> Task:
        task = self.repository.update_status(task_id, status)

        if task is None:
            raise TaskNotFoundError(task_id)

        return task

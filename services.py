from models import Task, ValidStatuses
from datetime import datetime
from typing import List
from exceptions import TaskNotFoundError
from protocol import TaskRepository

class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def get_tasks(self, status:ValidStatuses | None = None) -> List[Task]:
        return self.repository.get_all(status)

    def create_task(self, description) -> Task:
        task = Task(
            task_id=None,
            description=description,
            status=ValidStatuses.todo,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        return self.repository.create(task)


    def delete_task(self, task_id) -> None:
        task = self.repository.get_by_id(task_id)

        if task is None:
            raise TaskNotFoundError(task_id)

        return self.repository.delete(task_id)

    def get_task_by_id(self, task_id) -> Task:
        task = self.repository.get_by_id(task_id)

        if task is None:
            raise TaskNotFoundError(task_id)

        return task

    def update_task_description(self, task_id: int, description: str) -> Task:
        task = self.repository.update_description(task_id, description)

        if task is None:
            raise TaskNotFoundError(task_id)
        
        return task

    def update_task_status(self, task_id, status) -> Task:
        task = self.repository.update_status(task_id, status)

        if task is None:
            raise TaskNotFoundError(task_id)
        
        return task
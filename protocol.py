from typing import Protocol, List
from models import Task, ValidStatuses

class TaskRepository(Protocol):
    def create(self, task: Task) -> Task:
        ...

    def get_all(self, status: ValidStatuses | None = None) -> List[Task]:
        ...

    def get_by_id(self, task_id: int) -> Task | None:
        ...

    def update_description(self, task_id: int, description: str) -> Task | None:
        ...

    def update_status(self, task_id: int, status: ValidStatuses) -> Task | None:
        ...

    def delete(self, task_id: int) -> None:
        ...
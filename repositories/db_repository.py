import psycopg
from models import Task, ValidStatuses
from typing import List

class DatabaseTaskRepository:
    def __init__(self) -> None:
        conn = psycopg.connect(
        "dbname=task_tracker user=task_tracker_user password=12345 host=localhost port=5432"
        )

    def create(self, task: Task) -> Task:
        pass

    def get_all(self) -> List[Task]:
        pass

    def get_by_id(self, task_id: int) -> Task | None:
        pass

    def update_description(self, task_id: int, description: str) -> Task | None:
        pass

    def update_status(self, task_id: int, status: ValidStatuses) -> Task | None:
        pass

    def delete(self, task_id: int) -> None:
        pass
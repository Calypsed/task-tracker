from models import Task, ValidStatuses
from database.models import TaskModel
from sqlalchemy import Engine, Table, delete, func, insert, select, update
from sqlalchemy.engine import Row
from typing import cast


class SqlAlchemyCoreTaskRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._table = cast(Table, TaskModel.__table__)

    @staticmethod
    def _to_task(row: Row) -> Task:
        return Task(
            id=row.id,
            description=row.description,
            status=ValidStatuses(row.status),
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def create(
        self,
        description: str,
        status: ValidStatuses,
    ) -> Task:
        statement = (
            insert(self._table)
            .values(
                description=description,
                status=status.value,
            )
            .returning(self._table)
        )

        with self._engine.begin() as connection:
            row = connection.execute(statement).one()

        return self._to_task(row)

    def get_all(
        self,
        status: ValidStatuses | None = None,
    ) -> list[Task]:
        """Return tasks ordered by id in ascending order."""
        statement = select(self._table)

        if status is not None:
            statement = statement.where(self._table.c.status == status.value)

        statement = statement.order_by(self._table.c.id)

        with self._engine.connect() as connection:
            rows = connection.execute(statement).all()

        return [self._to_task(row) for row in rows]

    def get_by_id(
        self,
        task_id: int,
    ) -> Task | None:
        statement = select(self._table).where(self._table.c.id == task_id)

        with self._engine.connect() as connection:
            row = connection.execute(statement).one_or_none()

        if row is None:
            return None

        return self._to_task(row)

    def update(
        self,
        task_id: int,
        *,
        description: str | None = None,
        status: ValidStatuses | None = None,
    ) -> Task | None:
        if description is None and status is None:
            return self.get_by_id(task_id)

        values = {}

        if description is not None:
            values["description"] = description

        if status is not None:
            values["status"] = status.value

        values["updated_at"] = func.now()

        statement = (
            update(self._table)
            .where(self._table.c.id == task_id)
            .values(**values)
            .returning(self._table)
        )

        with self._engine.begin() as connection:
            row = connection.execute(statement).one_or_none()

        if row is None:
            return None

        return self._to_task(row)

    def delete(
        self,
        task_id: int,
    ) -> bool:
        statement = (
            delete(self._table)
            .where(self._table.c.id == task_id)
            .returning(self._table.c.id)
        )

        with self._engine.begin() as connection:
            deleted_id = connection.execute(statement).scalar_one_or_none()

        return deleted_id is not None

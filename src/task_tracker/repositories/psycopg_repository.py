import psycopg
from psycopg.rows import dict_row
from task_tracker.models import Task, ValidStatuses
from datetime import datetime
import task_tracker.constants as constants


class PsycopgTaskRepository:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def _connect(self):
        return psycopg.connect(self._dsn)

    @staticmethod
    def _to_task(row) -> Task:
        return Task(
            id=row[constants.KEY_STORAGE_ID],
            description=row[constants.KEY_STORAGE_DESCRIPTION],
            status=ValidStatuses(row[constants.KEY_STORAGE_STATUS]),
            created_at=row[constants.KEY_STORAGE_CREATED_AT],
            updated_at=row[constants.KEY_STORAGE_UPDATED_AT],
            due_at=row[constants.KEY_STORAGE_DUE_AT],
        )

    def create(
        self, description: str, status: ValidStatuses, due_at: datetime | None = None
    ) -> Task:
        with self._connect() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                row = cursor.execute(
                    """
                    INSERT INTO tasks (description, status, due_at)
                    VALUES (%s, %s, %s)
                    RETURNING *
                    """,
                    (
                        description,
                        status.value,
                        due_at,
                    ),
                ).fetchone()

        return self._to_task(row)

    def get_all(
        self,
        status: ValidStatuses | None = None,
    ) -> list[Task]:

        with self._connect() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                if status is None:
                    rows = cursor.execute("""
                        SELECT *
                        FROM tasks
                        ORDER BY id
                        """).fetchall()
                else:
                    rows = cursor.execute(
                        """
                        SELECT *
                        FROM tasks
                        WHERE status = %s
                        ORDER BY id
                        """,
                        (status.value,),
                    ).fetchall()

        return [self._to_task(row) for row in rows]

    def get_by_id(self, task_id: int) -> Task | None:
        with self._connect() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                row = cursor.execute(
                    """
                    SELECT
                        id,
                        description,
                        status,
                        created_at,
                        updated_at,
                        due_at
                    FROM tasks
                    WHERE id = %s
                    """,
                    (task_id,),
                ).fetchone()

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

        with self._connect() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                row = cursor.execute(
                    """
                    UPDATE tasks
                    SET
                        description = COALESCE(%s, description),
                        status = COALESCE(%s, status),
                        updated_at = NOW()
                    WHERE id = %s
                    RETURNING *
                    """,
                    (
                        description,
                        status.value if status is not None else None,
                        task_id,
                    ),
                ).fetchone()

        if row is None:
            return None

        return self._to_task(row)

    def delete(self, task_id: int) -> bool:
        with self._connect() as conn:
            with conn.cursor() as cursor:
                row = cursor.execute(
                    """
                    DELETE FROM tasks
                    WHERE id = %s
                    RETURNING id
                    """,
                    (task_id,),
                ).fetchone()

        return row is not None

import psycopg
from psycopg.rows import dict_row
from models import Task, ValidStatuses


class DatabaseTaskRepository:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def _connect(self):
        return psycopg.connect(self._dsn)

    @staticmethod
    def _to_task(row) -> Task:
        return Task(
            id=row["id"],
            description=row["description"],
            status=ValidStatuses(row["status"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create(self, description: str, status: ValidStatuses) -> Task:
        with self._connect() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                row = cursor.execute(
                    """
                    INSERT INTO tasks (description, status)
                    VALUES (%s, %s)
                    RETURNING
                        id,
                        description,
                        status,
                        created_at,
                        updated_at
                    """,
                    (
                        description,
                        status.value,
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
                        SELECT
                            id,
                            description,
                            status,
                            created_at,
                            updated_at
                        FROM tasks
                        ORDER BY id
                        """).fetchall()
                else:
                    rows = cursor.execute(
                        """
                        SELECT
                            id,
                            description,
                            status,
                            created_at,
                            updated_at
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
                        updated_at
                    FROM tasks
                    WHERE id = %s
                    """,
                    (task_id,),
                ).fetchone()

        if row is None:
            return None

        return self._to_task(row)

    def update_description(self, task_id: int, description: str) -> Task | None:
        with self._connect() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                row = cursor.execute(
                    """
                    UPDATE tasks
                    SET
                        description = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    RETURNING
                        id,
                        description,
                        status,
                        created_at,
                        updated_at
                    """,
                    (
                        description,
                        task_id,
                    ),
                ).fetchone()

        if row is None:
            return None

        return self._to_task(row)

    def update_status(self, task_id: int, status: ValidStatuses) -> Task | None:
        with self._connect() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                row = cursor.execute(
                    """
                    UPDATE tasks
                    SET
                        status = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    RETURNING
                        id,
                        description,
                        status,
                        created_at,
                        updated_at
                    """,
                    (
                        status.value,
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

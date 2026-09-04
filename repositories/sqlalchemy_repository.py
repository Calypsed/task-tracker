from models import Task, ValidStatuses
from database.models import TaskModel
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker


class SqlAlchemyTaskRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    @staticmethod
    def _to_task(model: TaskModel) -> Task:
        return Task(
            id=model.id,
            description=model.description,
            status=ValidStatuses(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def create(self, description: str, status: ValidStatuses) -> Task:
        with self._session_factory() as session:
            model = TaskModel(
                description=description,
                status=status.value,
            )

            session.add(model)
            session.commit()
            session.refresh(model)

            return self._to_task(model)

    def get_all(
        self,
        status: ValidStatuses | None = None,
    ) -> list[Task]:
        """Return tasks ordered by id in ascending order."""
        with self._session_factory() as session:
            statement = select(TaskModel)

            if status is not None:
                statement = statement.where(TaskModel.status == status.value)

            statement = statement.order_by(TaskModel.id)

            models = session.scalars(statement).all()

            return [self._to_task(model) for model in models]

    def get_by_id(self, task_id: int) -> Task | None:
        with self._session_factory() as session:
            model = session.get(TaskModel, task_id)

            if model is None:
                return None

            return self._to_task(model)

    def update(
        self,
        task_id: int,
        *,
        description: str | None = None,
        status: ValidStatuses | None = None,
    ) -> Task | None:
        with self._session_factory() as session:
            model = session.get(TaskModel, task_id)

            if model is None:
                return None

            if description is not None:
                model.description = description

            if status is not None:
                model.status = status.value

            session.commit()
            session.refresh(model)

            return self._to_task(model)

    def delete(self, task_id: int) -> bool:
        with self._session_factory() as session:
            model = session.get(TaskModel, task_id)

            if model is None:
                return False

            session.delete(model)
            session.commit()

            return True

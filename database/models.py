from datetime import datetime

from sqlalchemy import DateTime, func, CheckConstraint, Identity, text, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TaskModel(Base):
    __tablename__ = "tasks"

    __table_args__ = (
        CheckConstraint(
            "length(trim(description)) >= 3",
            name="tasks_description_check",
        ),
        CheckConstraint(
            "status IN ('todo', 'in-progress', 'done')",
            name="tasks_status_check",
        ),
    )

    id: Mapped[int] = mapped_column(
        Identity(),
        primary_key=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'todo'"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

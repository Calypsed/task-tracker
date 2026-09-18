from enum import Enum
from pydantic import BaseModel, field_validator, model_validator, Field
from datetime import datetime
from dataclasses import dataclass
import task_tracker.constants as constants


class ValidStatuses(str, Enum):
    TODO = "todo"
    DONE = "done"
    IN_PROGRESS = "in-progress"


@dataclass
class Task:
    id: int
    description: str
    status: ValidStatuses
    created_at: datetime
    updated_at: datetime
    due_at: datetime | None = None


class TaskCreate(BaseModel):
    description: str
    due_at: datetime | None = Field(
        validation_alias=constants.KEY_API_DUE_AT, default=None
    )

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str):
        value = value.strip()

        if len(value) < 3:
            raise ValueError("Description must be at least 3 characters long")

        return value


class TaskUpdate(BaseModel):
    description: str | None = None
    status: ValidStatuses | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: ValidStatuses | None):
        if value is None:
            raise ValueError("Status cannot be null")

        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None):
        if value is None:
            raise ValueError("Description cannot be null")

        value = value.strip()

        if len(value) < 3:
            raise ValueError("Description must be at least 3 characters long")

        return value

    @model_validator(mode="after")
    def validate_update(self):
        if self.description is None and self.status is None:
            raise ValueError("At least one field must be provided.")

        return self


class TaskResponse(BaseModel):
    id: int
    description: str
    status: ValidStatuses
    created_at: datetime = Field(serialization_alias=constants.KEY_API_CREATED_AT)
    updated_at: datetime = Field(serialization_alias=constants.KEY_API_UPDATED_AT)
    due_at: datetime | None = Field(
        serialization_alias=constants.KEY_API_DUE_AT, default=None
    )

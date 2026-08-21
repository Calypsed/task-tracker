from enum import Enum
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

STATUS_DONE = "done"
STATUS_TODO = "todo"
STATUS_IN_PROGRESS = "in-progress"

class ValidStatuses(str, Enum):
    todo = STATUS_TODO
    done = STATUS_DONE
    in_progress = STATUS_IN_PROGRESS

class TaskCreate(BaseModel):
    description: str

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str):
        value = value.strip()

        if len(value) < 3:
            raise ValueError("Description must be at least 3 characters long")

        return value

class TaskUpdate(BaseModel):
    description: str

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str):
        value = value.strip()

        if len(value) < 3:
            raise ValueError("Description must be at least 3 characters long")

        return value

class TaskStatusUpdate(BaseModel):
    status: ValidStatuses

class TaskResponse(BaseModel):
    id: int
    description: str
    status: ValidStatuses
    createdAt: datetime
    updatedAt: datetime

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str):
        value = value.strip()

        if len(value) < 3:
            raise ValueError("Description must be at least 3 characters long")

        return value
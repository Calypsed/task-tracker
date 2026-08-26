from enum import Enum
from pydantic import BaseModel, field_validator
from datetime import datetime
from dataclasses import dataclass


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

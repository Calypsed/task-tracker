from enum import Enum
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import constants

class Task:
    def __init__(self, task_id, description, status, created_at, updated_at):
        self.id = task_id
        self.description = description
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            constants.KEY_ID: self.id,
            constants.KEY_DESCRIPTION: self.description,
            constants.KEY_STATUS: self.status,
            constants.KEY_CREATED_AT: self.created_at.isoformat(),
            constants.KEY_UPDATED_AT: self.updated_at.isoformat(),
        }

    def to_response(self):
        return TaskResponse(
            id=self.id,
            description=self.description,
            status=self.status,
            createdAt=self.created_at,
            updatedAt=self.updated_at
        )

    def __str__(self):
        return f"{self.id}) {self.description} | {self.status}"


class ValidStatuses(str, Enum):
    todo = 'todo'
    done = 'done'
    in_progress = 'in-progress'

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
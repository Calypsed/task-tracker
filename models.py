from enum import Enum
from pydantic import BaseModel

STATUS_DONE = "done"
STATUS_TODO = "todo"
STATUS_IN_PROGRESS = "in-progress"

class ValidStatuses(str, Enum):
    todo = STATUS_TODO
    done = STATUS_DONE
    in_progress = STATUS_IN_PROGRESS

class TaskCreate(BaseModel):
    description: str

class TaskUpdate(BaseModel):
    description: str

class TaskStatusUpdate(BaseModel):
    status: ValidStatuses
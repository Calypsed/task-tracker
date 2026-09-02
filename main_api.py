from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from models import ValidStatuses, TaskCreate, TaskUpdate, TaskResponse
from services import TaskService
from repositories.repository_factory import create_repository
from exceptions import TaskNotFoundError
from dotenv import load_dotenv
from models import Task
from functools import lru_cache


def to_task_response(task: Task) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        description=task.description,
        status=task.status,
        createdAt=task.created_at,
        updatedAt=task.updated_at,
    )


load_dotenv()

app = FastAPI()


@lru_cache
def get_service() -> TaskService:
    repository = create_repository()
    return TaskService(repository)


@app.exception_handler(TaskNotFoundError)
def task_not_found_handler(request: Request, exc: TaskNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks(
    status: ValidStatuses | None = None, service: TaskService = Depends(get_service)
):
    return [to_task_response(t) for t in service.get_tasks(status)]


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, service: TaskService = Depends(get_service)):
    return to_task_response(service.get_task_by_id(task_id))


@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    service: TaskService = Depends(get_service),
):
    task = service.update_task(
        task_id,
        description=task_update.description,
        status=task_update.status,
    )

    return to_task_response(task)


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, service: TaskService = Depends(get_service)):
    service.delete_task(task_id)


@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate, service: TaskService = Depends(get_service)):
    return to_task_response(service.create_task(task.description))

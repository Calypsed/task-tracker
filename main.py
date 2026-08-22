from fastapi import FastAPI, HTTPException
from models import ValidStatuses, TaskCreate, TaskUpdate, TaskStatusUpdate, TaskResponse
from services import TaskService
from repositories.json_repository import JsonTaskRepository
from repositories.db_repository import DatabaseTaskRepository
import constants
from exceptions import TaskNotFoundError

JSON_repo = JsonTaskRepository(filename=constants.JSON_FILENAME)
postgreSQL_repo = DatabaseTaskRepository()
service = TaskService(JSON_repo)
app = FastAPI()

@app.get("/tasks", response_model=list[TaskResponse])
async def get_tasks(status: ValidStatuses | None = None):
    return [t.to_response() for t in service.get_tasks(status)]

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int):
    try:
        return service.get_task_by_id(task_id).to_response()
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task_description(task_id: int, task_update: TaskUpdate):
    try:
        return service.update_task_description(
            task_id, 
            task_update.description
            ).to_response()
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
        
@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int):
    try:
        service.delete_task(task_id)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.patch("/tasks/{task_id}/status", response_model=TaskResponse)
async def update_task_status(task_id: int, status: TaskStatusUpdate):
    try:
        return service.update_task_status(task_id, status.status).to_response()
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@app.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(task: TaskCreate):
    return service.create_task(task.description).to_response()
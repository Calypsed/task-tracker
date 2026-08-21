from fastapi import FastAPI, HTTPException
import json
from datetime import datetime
from models import ValidStatuses, TaskCreate, TaskUpdate, TaskStatusUpdate, TaskResponse

FILENAME = "tasks.json"
KEY_NEXT_ID = "nextID"
KEY_DELETED_IDS = "deletedIDs"
KEY_TASKS = "tasks"
KEY_ID = "task_id"
KEY_DESCRIPTION = "description"
KEY_STATUS = "status"
KEY_CREATED_AT = "createdAt"
KEY_UPDATED_AT = "updatedAt"
ERROR_NO_TASKS = "No tasks at the moment!"
ERROR_ID_NOT_FOUND = "No task with such id found!"
ERROR_ID_NOT_INT = "Error: ID must be a number"
ARGS_NUM_FOR_LIST_ALL_COMMAND = 2
ARGS_NUM_FOR_LIST_STATUS_COMMAND = 3
ARGS_NUM_FOR_SET_STATUS_COMMAND = 3
ARGS_NUM_MINIMAL = 2


class TaskTracker:
    def __init__(self, filename):
        self.filename = filename
        data = self._load_tasks()
        self.next_ID = data[KEY_NEXT_ID]
        self.deleted_IDs = data[KEY_DELETED_IDS]
        tasks_data = data[KEY_TASKS]
        self.tasks = [
            Task(
                t[KEY_ID],
                t[KEY_DESCRIPTION],
                t[KEY_STATUS],
                datetime.fromisoformat(t[KEY_CREATED_AT]),
                datetime.fromisoformat(t[KEY_UPDATED_AT]),
            )
            for t in tasks_data
        ]

    def _load_tasks(self):
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # File doesn't exist or JSON is corrupted
            empty_data = {KEY_NEXT_ID: 0, KEY_DELETED_IDS: [], KEY_TASKS: []}
            with open(self.filename, "w") as f:
                json.dump(empty_data, f)
            return empty_data

    def _write_tasks(self):
        with open(self.filename, "w") as f:
            json.dump(
                {
                    KEY_NEXT_ID: self.next_ID,
                    KEY_DELETED_IDS: self.deleted_IDs,
                    KEY_TASKS: [t.to_dict() for t in self.tasks],
                },
                f,
            )

    def list_tasks(self, status=None):
        if status:
            return [t.to_response() for t in self.tasks if t.get_status() == status]
        else: 
            return [t.to_response() for t in self.tasks]

    def add_task(self, description):
        new_ID = 0
        if self.deleted_IDs:
            new_ID = min(self.deleted_IDs)
            self.deleted_IDs.remove(new_ID)
        else:
            new_ID = self.next_ID
            self.next_ID += 1

        now = datetime.now()
        new_task = Task(new_ID, description, 'todo', now, now)
        self.tasks.append(new_task)
        self._write_tasks()

    def delete_task(self, task_id):
        for i, t in enumerate(self.tasks):
            if t.get_id() == task_id:
                self.tasks.pop(i)
                self.deleted_IDs.append(task_id)
                break
        self._write_tasks()

    def get_task_by_id(self, task_id):
        for t in self.tasks:
            if t.get_id() == task_id:
                return t
        return None

    def update_task_description(self, task_id, description):
        task = self.get_task_by_id(task_id)
        if task:
            task.set_description(description)
            task.set_updated_at(datetime.now())
            print("Task description updated successfully!")
        else:
            print(ERROR_ID_NOT_FOUND)
            return
        self._write_tasks()

    def update_task_status(self, task_id, status):
        task = self.get_task_by_id(task_id)
        if task:
            task.set_status(status)
            task.set_updated_at(datetime.now())
            print(f"Task status updated to '{status}' successfully!")
        else:
            print(ERROR_ID_NOT_FOUND)
        self._write_tasks()


class Task:
    def __init__(self, task_id, description, status, created_at, updated_at):
        self.task_id = task_id
        self.description = description
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            KEY_ID: self.task_id,
            KEY_DESCRIPTION: self.description,
            KEY_STATUS: self.status,
            KEY_CREATED_AT: self.created_at.isoformat(),
            KEY_UPDATED_AT: self.updated_at.isoformat(),
        }

    def to_response(self):
        return TaskResponse(
            id=self.task_id,
            description=self.description,
            status=self.status,
            createdAt=self.created_at,
            updatedAt=self.updated_at
        )

    def get_id(self):
        return self.task_id

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status

    def set_description(self, description):
        self.description = description

    def set_updated_at(self, updated_at):
        self.updated_at = updated_at

    def __str__(self):
        return f"{self.task_id}) {self.description} | {self.status}"


tracker = TaskTracker(FILENAME)
app = FastAPI()


@app.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(status: ValidStatuses | None = None):
    return tracker.list_tasks(status)

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int):
    task = tracker.get_task_by_id(task_id)
    if task:
        return task.to_response()
    else:
        raise HTTPException(status_code=404, detail=ERROR_ID_NOT_FOUND)

@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task_description(task_id: int, task_update: TaskUpdate):
    task = tracker.get_task_by_id(task_id)
    if task:
        tracker.update_task_description(task_id, task_update.description)
        return task.to_response()
    else:
        raise HTTPException(status_code=404, detail=ERROR_ID_NOT_FOUND)

@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int):
    task = tracker.get_task_by_id(task_id)
    if task:
        tracker.delete_task(task_id)
    else:
        raise HTTPException(status_code=404, detail=ERROR_ID_NOT_FOUND)

@app.patch("/tasks/{task_id}/status", response_model=TaskResponse)
async def update_task_status(task_id: int, status: TaskStatusUpdate):
    task = tracker.get_task_by_id(task_id)
    if task:
        tracker.update_task_status(task_id, status.status)
        return task.to_response()
    else:
        raise HTTPException(status_code=404, detail=ERROR_ID_NOT_FOUND)

@app.post("/tasks", response_model=TaskResponse, status_code=201)
async def add_task(task: TaskCreate):
    tracker.add_task(task.description)
    return tracker.tasks[-1].to_response()
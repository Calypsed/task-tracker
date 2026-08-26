# Task Tracker

A small task-tracking application written in Python. The project started as a CLI application and now supports both a command-line interface and a REST API built with FastAPI.

The application uses a service/repository architecture, so the same business logic can work with either JSON-file storage or PostgreSQL.

## Features

- Create tasks
- Update task descriptions
- Delete tasks
- Mark tasks as `todo`, `in-progress`, or `done`
- List all tasks
- Filter tasks by status
- Get a task by ID through the REST API
- Use either JSON or PostgreSQL as the storage backend
- Use the same `TaskService` from both CLI and FastAPI

## Project Structure

```text
task-tracker/
├── database/
│   └── schema.sql
├── repositories/
│   ├── db_repository.py
│   ├── factory.py
│   ├── json_repository.py
│   └── protocol.py
├── .env.example
├── .flake8
├── .gitignore
├── constants.py
├── exceptions.py
├── main_api.py
├── main_cli.py
├── models.py
├── services.py
├── tasks.json
├── pyproject.toml
└── uv.lock
```

## Architecture

```text
CLI ───────┐
           │
           ▼
      TaskService
           │
           ▼
     TaskRepository
       ┌───┴────┐
       ▼        ▼
     JSON    PostgreSQL

FastAPI ────┘
```

- `main_cli.py` handles command-line input and output.
- `main_api.py` exposes the REST API.
- `services.py` contains application logic.
- `TaskRepository` defines the repository contract using `Protocol`.
- `JsonTaskRepository` stores tasks in `tasks.json`.
- `DatabaseTaskRepository` stores tasks in PostgreSQL using Psycopg.
- `factory.py` chooses the repository implementation from environment configuration.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL, only if using the PostgreSQL repository

## Installation

Install dependencies:

```bash
uv sync
```

Black and Flake8 are included as development dependencies.

## Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### JSON repository

```env
REPOSITORY_TYPE=json
```

Tasks will be stored in `tasks.json`.

### PostgreSQL repository

```env
REPOSITORY_TYPE=postgres
DATABASE_URL=postgresql://task_tracker_user:password@localhost:5432/task_tracker
```

General PostgreSQL DSN format:

```text
postgresql://USER:PASSWORD@HOST:PORT/DATABASE_NAME
```

Do not commit `.env`. It is excluded by `.gitignore`.

## PostgreSQL Setup

Create a database and application user, for example:

```sql
CREATE USER task_tracker_user WITH PASSWORD 'your_password';

CREATE DATABASE task_tracker
    OWNER task_tracker_user;
```

Connect to the `task_tracker` database as `task_tracker_user` and execute:

```text
database/schema.sql
```

The schema creates the `tasks` table with:

- auto-generated integer IDs
- task descriptions with a minimum length of 3 characters
- statuses limited to `todo`, `in-progress`, and `done`
- automatic `created_at` and `updated_at` timestamps on creation

## CLI

Run the CLI directly with Python:

```bash
uv run python main_cli.py --help
```

### Add a task

```bash
uv run python main_cli.py add "Buy groceries"
```

Example output:

```text
Task added successfully (ID: 1)
```

### Update a task

```bash
uv run python main_cli.py update 1 "Buy groceries and cook dinner"
```

### Delete a task

```bash
uv run python main_cli.py delete 1
```

### Mark a task as in progress

```bash
uv run python main_cli.py mark-in-progress 1
```

### Mark a task as done

```bash
uv run python main_cli.py mark-done 1
```

### List all tasks

```bash
uv run python main_cli.py list
```

### Filter tasks by status

```bash
uv run python main_cli.py list todo
uv run python main_cli.py list in-progress
uv run python main_cli.py list done
```

## REST API

Start the FastAPI application:

```bash
uv run uvicorn main_api:app --reload
```

API URL:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

### Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/tasks` | Create a task |
| `GET` | `/tasks` | List tasks |
| `GET` | `/tasks?status=done` | Filter tasks by status |
| `GET` | `/tasks/{task_id}` | Get a task by ID |
| `PUT` | `/tasks/{task_id}` | Update task description |
| `PATCH` | `/tasks/{task_id}/status` | Update task status |
| `DELETE` | `/tasks/{task_id}` | Delete a task |

### Create task example

Request:

```json
{
  "description": "Learn PostgreSQL"
}
```

Example response:

```json
{
  "id": 1,
  "description": "Learn PostgreSQL",
  "status": "todo",
  "createdAt": "2026-08-26T12:00:00Z",
  "updatedAt": "2026-08-26T12:00:00Z"
}
```

### Update status example

```json
{
  "status": "done"
}
```

Valid statuses:

```text
todo
in-progress
done
```

## Repository Switching

Repository selection is handled by `repositories/factory.py`.

For JSON:

```env
REPOSITORY_TYPE=json
```

For PostgreSQL:

```env
REPOSITORY_TYPE=postgres
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/DATABASE_NAME
```

Both implementations follow the same `TaskRepository` protocol, so `TaskService` does not depend on a specific storage backend.

## Code Quality

Format with Black:

```bash
uv run black .
```

Check formatting without modifying files:

```bash
uv run black --check .
```

Run Flake8:

```bash
uv run flake8 .
```

## Future Improvements

- automated tests with pytest
- shared validation for CLI and API
- database migrations
- PostgreSQL connection pooling
- Docker setup
- pagination
- structured application configuration

## License

This project is licensed under the MIT License. See `LICENSE` for details.

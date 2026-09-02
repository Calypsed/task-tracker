# Task Tracker

A small task-tracking application written in Python. It provides both a command-line interface and a REST API built with FastAPI.

The project uses a service/repository architecture: the CLI and API share the same business logic, while persistence can be switched between a local JSON file and PostgreSQL.

## Features

- Create tasks
- Update task descriptions and statuses
- Delete tasks
- List all tasks
- Filter tasks by status
- Get a task by ID through the REST API
- Store tasks in JSON or PostgreSQL
- Share the same `TaskService` between CLI and FastAPI
- Validate task descriptions and statuses
- Test the service, CLI, API, repository implementations, and repository contract with pytest

Valid task statuses are:

- `todo`
- `in-progress`
- `done`

Task descriptions are trimmed and must contain at least 3 characters.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL only when using the PostgreSQL repository or running the PostgreSQL tests

## Quick Start

Install the project dependencies:

```bash
uv sync
```

The application uses the JSON repository by default, so no database or `.env` file is required for a basic local run.

Add a task:

```bash
uv run python main_cli.py add "Buy groceries"
```

List tasks:

```bash
uv run python main_cli.py list
```

Start the API:

```bash
uv run uvicorn main_api:app --reload
```

Then open:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

## Project Structure

```text
task-tracker/
├── database/
│   └── schema.sql
├── repositories/
│   ├── db_repository.py
│   ├── json_repository.py
│   ├── protocol.py
│   └── repository_factory.py
├── tests/
│   ├── fakes.py
│   ├── test_api.py
│   ├── test_cli_e2e.py
│   ├── test_cli_handlers.py
│   ├── test_cli_parser.py
│   ├── test_db_repository.py
│   ├── test_json_repository.py
│   ├── test_repository_contract.py
│   ├── test_repository_factory.py
│   └── test_services.py
├── .env.example
├── .gitignore
├── constants.py
├── exceptions.py
├── LICENSE
├── main_api.py
├── main_cli.py
├── models.py
├── pyproject.toml
├── README.md
├── services.py
└── uv.lock
```

`tasks.json` is created at runtime when the JSON repository is used with its default filename. It is intentionally ignored by Git.

## Architecture

```text
CLI ---------\
              \
               -> TaskService -> TaskRepository -> JSON
              /                              \\-> PostgreSQL
FastAPI -----/
```

The main responsibilities are:

- `main_cli.py` parses CLI commands and prints CLI output.
- `main_api.py` exposes the FastAPI endpoints and converts domain tasks to API responses.
- `services.py` contains application-level task operations and description validation.
- `models.py` contains the domain task model, status enum, and Pydantic API models.
- `repositories/protocol.py` defines the `TaskRepository` contract with `Protocol`.
- `repositories/json_repository.py` persists tasks to a JSON file.
- `repositories/db_repository.py` persists tasks to PostgreSQL with Psycopg.
- `repositories/repository_factory.py` selects the repository implementation from environment variables.

Both frontends depend on `TaskService`, and `TaskService` depends only on the repository contract rather than a concrete storage backend.

## Configuration

Environment variables are loaded from `.env` by both the CLI and API.

### JSON repository

JSON is the default repository. The following configuration is therefore optional:

```env
REPOSITORY_TYPE=json
JSON_FILENAME=tasks.json
```

`JSON_FILENAME` is optional. If it is not set, the application uses `tasks.json` in the current working directory.

If the file does not exist, `JsonTaskRepository` creates it automatically.

> Note: the JSON repository starts task IDs at `0`. PostgreSQL uses its own identity sequence, which normally starts at `1`. Client code should not assume a particular first ID.

### PostgreSQL repository

Set:

```env
REPOSITORY_TYPE=postgres
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/DATABASE_NAME
```

The included `.env.example` is a PostgreSQL configuration template. Copy it only when you want to configure PostgreSQL, then replace the placeholder credentials:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Do not commit `.env`; it is excluded by `.gitignore`.

## PostgreSQL Setup

Create a database and user, for example:

```sql
CREATE USER task_tracker_user WITH PASSWORD 'your_password';

CREATE DATABASE task_tracker
    OWNER task_tracker_user;
```

Set your connection URL:

```env
REPOSITORY_TYPE=postgres
DATABASE_URL=postgresql://task_tracker_user:your_password@localhost:5432/task_tracker
```

Apply the schema from `database/schema.sql`. With `psql`, for example:

```bash
psql "postgresql://task_tracker_user:your_password@localhost:5432/task_tracker" \
  -f database/schema.sql
```

The schema creates a `tasks` table with:

- an auto-generated integer primary key
- a non-null description whose trimmed length must be at least 3 characters
- a status limited to `todo`, `in-progress`, or `done`
- `created_at` and `updated_at` timestamp columns with timezone information

## CLI

Show CLI help:

```bash
uv run python main_cli.py --help
```

### Add a task

```bash
uv run python main_cli.py add "Buy groceries"
```

Output has the following form:

```text
Task added successfully (ID=<task_id>)
```

### Update a task description

```bash
uv run python main_cli.py update <task_id> "Buy groceries and cook dinner"
```

### Delete a task

```bash
uv run python main_cli.py delete <task_id>
```

### Mark a task as in progress

```bash
uv run python main_cli.py mark-in-progress <task_id>
```

### Mark a task as done

```bash
uv run python main_cli.py mark-done <task_id>
```

### List all tasks

```bash
uv run python main_cli.py list
```

Each task is printed as:

```text
<id>: <description> [<status>]
```

If there are no matching tasks, the CLI prints:

```text
No tasks found
```

### Filter tasks by status

```bash
uv run python main_cli.py list todo
uv run python main_cli.py list in-progress
uv run python main_cli.py list done
```

## REST API

Start the development server:

```bash
uv run uvicorn main_api:app --reload
```

### Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/tasks` | Create a task |
| `GET` | `/tasks` | List all tasks |
| `GET` | `/tasks?status=<status>` | Filter tasks by status |
| `GET` | `/tasks/{task_id}` | Get one task by ID |
| `PATCH` | `/tasks/{task_id}` | Update description and/or status |
| `DELETE` | `/tasks/{task_id}` | Delete a task |

### Task response

API task objects have this shape:

```json
{
  "id": 0,
  "description": "Learn FastAPI",
  "status": "todo",
  "createdAt": "2026-09-02T12:00:00Z",
  "updatedAt": "2026-09-02T12:00:00Z"
}
```

The exact ID and timestamps depend on the repository and time of creation.

### Create a task

```http
POST /tasks
Content-Type: application/json
```

```json
{
  "description": "Learn PostgreSQL"
}
```

Successful creation returns `201 Created` and the created task.

### List tasks

```http
GET /tasks
```

Filter by status:

```http
GET /tasks?status=done
```

An invalid status returns FastAPI validation error `422 Unprocessable Entity`.

### Get a task by ID

```http
GET /tasks/{task_id}
```

If the task does not exist, the API returns `404 Not Found`:

```json
{
  "detail": "Task with id 999 not found"
}
```

### Update a task

The API uses one partial-update endpoint:

```http
PATCH /tasks/{task_id}
Content-Type: application/json
```

Update only the description:

```json
{
  "description": "Updated task description"
}
```

Update only the status:

```json
{
  "status": "done"
}
```

Update both:

```json
{
  "description": "Updated task description",
  "status": "in-progress"
}
```

At least one field must be provided. Explicit `null` values are rejected. Invalid update payloads return `422 Unprocessable Entity`.

### Delete a task

```http
DELETE /tasks/{task_id}
```

Successful deletion returns `204 No Content`.

Deleting a missing task returns `404 Not Found`.

## Repository Switching

Repository selection is handled by `repositories/repository_factory.py`.

The factory reads `REPOSITORY_TYPE`:

- unset or `json` -> `JsonTaskRepository`
- `postgres` -> `DatabaseTaskRepository`
- any other value -> configuration error

For PostgreSQL, `DATABASE_URL` must also be set.

For JSON, `JSON_FILENAME` can optionally override the default `tasks.json` path.

Because both implementations satisfy the same `TaskRepository` protocol, `TaskService` does not need to know which persistence backend is active.

## Tests

The test suite covers:

- service logic
- CLI parsing and handlers
- CLI end-to-end flows
- FastAPI endpoints
- JSON repository behavior
- PostgreSQL repository behavior
- the shared repository contract
- repository factory selection

### Tests that do not require a live PostgreSQL database

After `uv sync`, run:

```bash
uv run pytest \
  --ignore=tests/test_db_repository.py \
  --ignore=tests/test_repository_contract.py
```

### Full test suite

The PostgreSQL tests expect `TEST_DATABASE_URL` to point to a test database containing the `tasks` table.

For example:

```env
TEST_DATABASE_URL=postgresql://task_tracker_user:your_password@localhost:5432/task_tracker_test
```

Create the test database and apply `database/schema.sql`, then run:

```bash
uv run pytest
```

The PostgreSQL tests delete rows from the `tasks` table during setup and teardown, so use a dedicated test database rather than development or production data.

### Coverage

With the test database configured, coverage can be collected with:

```bash
uv run pytest --cov=. --cov-report=term-missing
```

## Code Quality

The project uses Ruff for formatting and linting.

Format the code:

```bash
uv run ruff format .
```

Check formatting without modifying files:

```bash
uv run ruff format --check .
```

Run the linter:

```bash
uv run ruff check .
```

Apply automatically fixable lint fixes:

```bash
uv run ruff check --fix .
```

Ruff is configured in `pyproject.toml` for Python 3.13 with a line length of 88 characters.

## License

See `LICENSE`.

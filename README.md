# Task Tracker

A small task-tracking application written in Python with both a command-line interface and a REST API built with FastAPI.

The project is primarily an architecture and persistence exercise. The same business logic works with three interchangeable repository implementations:

- JSON file storage
- PostgreSQL through Psycopg and handwritten SQL
- PostgreSQL through SQLAlchemy ORM

All repositories implement the same `TaskRepository` contract, allowing the CLI, API, and service layer to remain independent of the persistence technology.

## Features

- Create tasks
- Update task descriptions
- Change task status
- Delete tasks
- List all tasks
- Filter tasks by status
- Retrieve a task by ID through the REST API
- Use JSON, Psycopg, or SQLAlchemy as the persistence implementation
- Share the same `TaskService` between the CLI and FastAPI
- Validate task descriptions and statuses
- Verify repository implementations with shared contract tests
- Verify PostgreSQL constraints with integration tests

Supported task statuses:

- `todo`
- `in-progress`
- `done`

Task descriptions are trimmed by the service layer and must contain at least 3 characters.

## Tech Stack

- Python 3.13+
- FastAPI
- Pydantic
- PostgreSQL
- Psycopg 3
- SQLAlchemy 2
- pytest
- Ruff
- uv

## Architecture

```text
CLI -------------------\
                        \
                         -> TaskService -> TaskRepository
                        /                       |
FastAPI ---------------/                        |
                                                +--> JsonTaskRepository -> JSON file
                                                |
                                                +--> PsycopgTaskRepository -> Psycopg -> PostgreSQL
                                                |
                                                +--> SqlAlchemyTaskRepository -> SQLAlchemy -> Psycopg -> PostgreSQL
```

The important dependency direction is:

```text
CLI / API
    |
    v
TaskService
    |
    v
TaskRepository protocol
    |
    +--> JSON implementation
    +--> Psycopg implementation
    +--> SQLAlchemy implementation
```

`TaskService` does not know which persistence technology is being used. Repository selection happens in `repositories/repository_factory.py`.

## Project Structure

```text
task-tracker/
├── database/
│   ├── connection.py
│   ├── models.py
│   └── schema.sql
├── repositories/
│   ├── json_repository.py
│   ├── protocol.py
│   ├── psycopg_repository.py
│   ├── repository_factory.py
│   └── sqlalchemy_repository.py
├── tests/
│   ├── fakes.py
│   ├── test_api.py
│   ├── test_cli_e2e.py
│   ├── test_cli_handlers.py
│   ├── test_cli_parser.py
│   ├── test_database_constraints.py
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

### Main modules

- `main_cli.py` — CLI commands and terminal output.
- `main_api.py` — FastAPI application and HTTP endpoints.
- `services.py` — application-level task operations and validation.
- `models.py` — domain `Task`, task statuses, and Pydantic request/response models.
- `repositories/protocol.py` — common `TaskRepository` interface.
- `repositories/json_repository.py` — JSON persistence implementation.
- `repositories/psycopg_repository.py` — PostgreSQL implementation using handwritten SQL and Psycopg.
- `repositories/sqlalchemy_repository.py` — PostgreSQL implementation using SQLAlchemy ORM.
- `repositories/repository_factory.py` — selects the active repository from environment variables.
- `database/models.py` — SQLAlchemy ORM models.
- `database/connection.py` — creates the SQLAlchemy engine/session factory.
- `database/schema.sql` — current PostgreSQL schema definition.

## Installation

Install dependencies with uv:

```bash
uv sync
```

The JSON repository is the default, so PostgreSQL is not required for a basic local run.

## Configuration

The application loads environment variables from `.env`.

`REPOSITORY_TYPE` supports three values:

```text
json
psycopg
sqlalchemy
```

If `REPOSITORY_TYPE` is not set, the application uses `json`.

### JSON repository

```env
REPOSITORY_TYPE=json
JSON_FILENAME=tasks.json
```

`JSON_FILENAME` is optional. If it is omitted, the application uses `tasks.json` in the current working directory.

The file is created automatically when it does not exist.

### PostgreSQL with Psycopg

```env
REPOSITORY_TYPE=psycopg
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/DATABASE_NAME
```

This implementation executes handwritten SQL directly through Psycopg.

### PostgreSQL with SQLAlchemy

```env
REPOSITORY_TYPE=sqlalchemy
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/DATABASE_NAME
```

The factory creates a SQLAlchemy session factory and injects it into `SqlAlchemyTaskRepository`.

A regular `postgresql://...` URL can be used for both PostgreSQL implementations. For SQLAlchemy, `database/connection.py` converts it internally to the `postgresql+psycopg://...` dialect URL.

## PostgreSQL Setup

Create a PostgreSQL user and database, for example:

```sql
CREATE USER task_tracker_user WITH PASSWORD 'your_password';

CREATE DATABASE task_tracker
    OWNER task_tracker_user;
```

Apply the schema:

```bash
psql "postgresql://task_tracker_user:your_password@localhost:5432/task_tracker" \
  -f database/schema.sql
```

Then configure either PostgreSQL repository.

Psycopg:

```env
REPOSITORY_TYPE=psycopg
DATABASE_URL=postgresql://task_tracker_user:your_password@localhost:5432/task_tracker
```

SQLAlchemy:

```env
REPOSITORY_TYPE=sqlalchemy
DATABASE_URL=postgresql://task_tracker_user:your_password@localhost:5432/task_tracker
```

Both implementations work with the same `tasks` table.

### Database schema

The current schema is managed by `database/schema.sql` and contains:

- integer identity primary key
- non-null task description
- a PostgreSQL `CHECK` constraint requiring at least 3 non-whitespace characters
- a `CHECK` constraint restricting status to `todo`, `in-progress`, or `done`
- `created_at` and `updated_at` timezone-aware timestamps

Alembic migrations are not part of the project yet.

## Repository Implementations

### `JsonTaskRepository`

Stores tasks in a JSON file and is useful for running the project without external infrastructure.

### `PsycopgTaskRepository`

Uses Psycopg directly and contains explicit SQL for `INSERT`, `SELECT`, `UPDATE`, and `DELETE` operations.

This implementation is intentionally kept alongside SQLAlchemy so the project contains a working example of direct PostgreSQL access with handwritten SQL.

### `SqlAlchemyTaskRepository`

Uses the SQLAlchemy 2 ORM API.

`TaskModel` represents the PostgreSQL `tasks` table, while the repository converts ORM objects into the domain `Task` dataclass before returning them to the service layer.

The repository receives a `sessionmaker` through its constructor instead of creating the engine itself:

```text
repository_factory
      |
      v
create_session_factory()
      |
      v
sessionmaker
      |
      v
SqlAlchemyTaskRepository
```

This keeps database connection setup separate from repository behavior and makes the repository easier to test.

## CLI

Show help:

```bash
uv run python main_cli.py --help
```

### Add a task

```bash
uv run python main_cli.py add "Buy groceries"
```

### Update a description

```bash
uv run python main_cli.py update 1 "Buy groceries and cook dinner"
```

### Mark a task as in progress

```bash
uv run python main_cli.py mark-in-progress 1
```

### Mark a task as done

```bash
uv run python main_cli.py mark-done 1
```

### Delete a task

```bash
uv run python main_cli.py delete 1
```

### List all tasks

```bash
uv run python main_cli.py list
```

### Filter by status

```bash
uv run python main_cli.py list todo
uv run python main_cli.py list in-progress
uv run python main_cli.py list done
```

Task output has the following form:

```text
1: Buy groceries [todo]
```

## REST API

Start the development server:

```bash
uv run uvicorn main_api:app --reload
```

Useful URLs:

- API base: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

### Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/tasks` | Create a task |
| `GET` | `/tasks` | List tasks |
| `GET` | `/tasks?status=<status>` | Filter tasks by status |
| `GET` | `/tasks/{task_id}` | Get a task by ID |
| `PATCH` | `/tasks/{task_id}` | Update description and/or status |
| `DELETE` | `/tasks/{task_id}` | Delete a task |

### Create a task

```http
POST /tasks
Content-Type: application/json
```

```json
{
  "description": "Learn SQLAlchemy"
}
```

A newly created task starts with status `todo`.

### Update a task

```http
PATCH /tasks/1
Content-Type: application/json
```

```json
{
  "description": "Learn SQLAlchemy ORM",
  "status": "in-progress"
}
```

At least one update field must be provided.

### Response shape

```json
{
  "id": 1,
  "description": "Learn SQLAlchemy",
  "status": "todo",
  "createdAt": "2026-09-04T12:00:00Z",
  "updatedAt": "2026-09-04T12:00:00Z"
}
```

## Testing

The project uses pytest.

### Full test suite

The complete test suite includes PostgreSQL integration tests and therefore requires a dedicated test database.

Create the test database, apply the same schema, and set:

```env
TEST_DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/TEST_DATABASE_NAME
```

Then run:

```bash
uv run pytest
```

> Important: repository contract tests clear the `tasks` table in `TEST_DATABASE_URL`. Use a dedicated test database, never a database containing real data.

### Repository contract tests

`tests/test_repository_contract.py` runs the same behavior tests against:

- `JsonTaskRepository`
- `PsycopgTaskRepository`
- `SqlAlchemyTaskRepository`

This verifies that all three implementations obey the same repository contract regardless of how tasks are stored.

The contract covers behavior such as:

- task creation
- timestamps
- unique IDs
- ordering
- status filtering
- lookup by ID
- updates
- no-op updates
- deletion
- missing-task behavior

Run only the repository contract tests:

```bash
uv run pytest tests/test_repository_contract.py
```

### Database constraint tests

`tests/test_database_constraints.py` tests PostgreSQL itself directly through Psycopg. For example, it verifies that the database rejects descriptions shorter than the schema allows.

This is intentionally separate from repository contract testing: repository tests verify application behavior, while database constraint tests verify guarantees enforced by PostgreSQL.

## Code Quality

Format the project:

```bash
uv run ruff format .
```

Run lint checks:

```bash
uv run ruff check .
```

Run tests:

```bash
uv run pytest
```

A typical pre-commit check is therefore:

```bash
uv run ruff format .
uv run ruff check .
uv run pytest
```

## Current Learning Focus

The project deliberately keeps both PostgreSQL implementations:

```text
Handwritten SQL                   SQLAlchemy ORM
       |                                |
       v                                v
PsycopgTaskRepository          SqlAlchemyTaskRepository
       \                                /
        \                              /
         +-------- PostgreSQL --------+
```

This makes it possible to compare direct SQL with ORM-based persistence while keeping the public repository behavior identical.

A natural next step is to introduce Alembic for versioned database schema migrations. At the moment, database setup still uses `database/schema.sql`.

## License

See [LICENSE](LICENSE).

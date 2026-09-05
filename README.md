# Task Tracker

A small task-tracking application written in Python with both a command-line interface and a REST API built with FastAPI.

The project is primarily an architecture and persistence exercise. The same service layer works with four interchangeable repository implementations:

- JSON file storage
- PostgreSQL through Psycopg and handwritten SQL
- PostgreSQL through SQLAlchemy Core
- PostgreSQL through SQLAlchemy ORM

All implementations satisfy the same `TaskRepository` protocol and are verified by the same repository contract tests.

## Features

- Create tasks
- Update task descriptions
- Change task status
- Delete tasks
- List all tasks
- Filter tasks by status
- Retrieve a task by ID through the REST API
- Switch persistence implementations through environment configuration
- Use the same `TaskService` from both CLI and FastAPI
- Validate task descriptions and statuses
- Verify repository behavior with shared contract tests
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
- pytest-cov
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
                                                +--> PsycopgTaskRepository
                                                |        -> Psycopg -> PostgreSQL
                                                |
                                                +--> SqlAlchemyCoreTaskRepository
                                                |        -> Engine / Connection
                                                |        -> SQLAlchemy Core -> Psycopg -> PostgreSQL
                                                |
                                                +--> SqlAlchemyOrmTaskRepository
                                                         -> Session
                                                         -> SQLAlchemy ORM -> Psycopg -> PostgreSQL
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
    +--> JSON
    +--> Psycopg
    +--> SQLAlchemy Core
    +--> SQLAlchemy ORM
```

`TaskService` does not know which persistence technology is being used. Repository selection happens in `repositories/repository_factory.py`.

## Why Both SQLAlchemy Core and ORM?

The project intentionally keeps both SQLAlchemy styles for learning purposes.

The same operations can be compared at three PostgreSQL abstraction levels:

```text
Psycopg                    SQLAlchemy Core             SQLAlchemy ORM

handwritten SQL            SQL expression API          mapped Python objects
INSERT INTO ...            insert(table)               session.add(model)
SELECT ...                 select(table)               session.get(...)
UPDATE ...                 update(table)               model.field = value
DELETE ...                 delete(table)               session.delete(model)
```

`SqlAlchemyCoreTaskRepository` works with an `Engine`, `Connection`, SQL expressions, and the table exposed by `TaskModel.__table__`.

`SqlAlchemyOrmTaskRepository` works with a `sessionmaker`, `Session`, and mapped `TaskModel` objects.

Both return the same domain `Task` dataclass to the service layer.

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
│   ├── sqlalchemy_core_repository.py
│   └── sqlalchemy_orm_repository.py
├── tests/
│   ├── fakes.py
│   ├── test_api.py
│   ├── test_cli_e2e.py
│   ├── test_cli_handlers.py
│   ├── test_cli_parser.py
│   ├── test_database_connection.py
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

### Main Modules

- `main_cli.py` — CLI parser, command handlers, and application startup.
- `main_api.py` — FastAPI application and HTTP endpoints.
- `services.py` — application-level task operations and description validation.
- `models.py` — domain `Task`, task statuses, and Pydantic request/response models.
- `repositories/protocol.py` — common `TaskRepository` protocol.
- `repositories/json_repository.py` — JSON persistence implementation.
- `repositories/psycopg_repository.py` — PostgreSQL implementation with handwritten SQL.
- `repositories/sqlalchemy_core_repository.py` — PostgreSQL implementation using SQLAlchemy Core.
- `repositories/sqlalchemy_orm_repository.py` — PostgreSQL implementation using SQLAlchemy ORM.
- `repositories/repository_factory.py` — selects and constructs the configured repository.
- `database/models.py` — SQLAlchemy declarative model for the `tasks` table.
- `database/connection.py` — SQLAlchemy URL conversion, `Engine`, and `sessionmaker` creation.
- `database/schema.sql` — current PostgreSQL schema definition.

## Installation

Install dependencies with `uv`:

```bash
uv sync
```

The application defaults to the JSON repository when `REPOSITORY_TYPE` is not set, so PostgreSQL is not required for a basic local run.

## Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

`REPOSITORY_TYPE` supports four values:

```text
json
psycopg
sqlalchemy_core
sqlalchemy_orm
```

If it is not set, the application uses `json`.

### JSON Repository

```env
REPOSITORY_TYPE=json
JSON_FILENAME=tasks.json
```

`JSON_FILENAME` is optional. If omitted, the application uses `tasks.json` in the current working directory.

The file is created automatically if it does not exist.

### PostgreSQL with Psycopg

```env
REPOSITORY_TYPE=psycopg
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/DATABASE_NAME
```

This implementation sends handwritten SQL directly through Psycopg.

### PostgreSQL with SQLAlchemy Core

```env
REPOSITORY_TYPE=sqlalchemy_core
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/DATABASE_NAME
```

The factory creates a SQLAlchemy `Engine` and injects it into `SqlAlchemyCoreTaskRepository`.

### PostgreSQL with SQLAlchemy ORM

```env
REPOSITORY_TYPE=sqlalchemy_orm
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/DATABASE_NAME
```

The factory creates a SQLAlchemy `Engine`, builds a `sessionmaker`, and injects it into `SqlAlchemyOrmTaskRepository`.

A regular `postgresql://...` URL can be used for all PostgreSQL implementations. `database/connection.py` converts it to `postgresql+psycopg://...` internally when SQLAlchemy is used.

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

Then choose any PostgreSQL repository:

```env
REPOSITORY_TYPE=psycopg
```

or:

```env
REPOSITORY_TYPE=sqlalchemy_core
```

or:

```env
REPOSITORY_TYPE=sqlalchemy_orm
```

All three PostgreSQL repositories work with the same `tasks` table.

### Database Schema

The current schema is managed by `database/schema.sql` and contains:

- integer identity primary key
- non-null task description
- a PostgreSQL `CHECK` constraint requiring at least 3 non-whitespace characters
- a `CHECK` constraint restricting status to `todo`, `in-progress`, or `done`
- timezone-aware `created_at` and `updated_at` timestamps

Alembic migrations are not part of the project yet.

## Running the CLI

Show available commands:

```bash
uv run python main_cli.py --help
```

Create a task:

```bash
uv run python main_cli.py add "Learn SQLAlchemy Core"
```

List tasks:

```bash
uv run python main_cli.py list
```

Filter tasks by status:

```bash
uv run python main_cli.py list done
```

Update a description:

```bash
uv run python main_cli.py update 1 "Learn SQLAlchemy deeply"
```

Change status:

```bash
uv run python main_cli.py mark-in-progress 1
uv run python main_cli.py mark-done 1
```

Delete a task:

```bash
uv run python main_cli.py delete 1
```

## Running the API

Start the FastAPI development server:

```bash
uv run fastapi dev main_api.py
```

The API exposes:

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/tasks` | Create a task |
| `GET` | `/tasks` | List tasks |
| `GET` | `/tasks?status=done` | Filter tasks by status |
| `GET` | `/tasks/{task_id}` | Get one task |
| `PATCH` | `/tasks/{task_id}` | Update description and/or status |
| `DELETE` | `/tasks/{task_id}` | Delete a task |

Example request body for creating a task:

```json
{
  "description": "Learn repository pattern"
}
```

Example update:

```json
{
  "description": "Learn SQLAlchemy Core",
  "status": "in-progress"
}
```

FastAPI provides interactive API documentation while the development server is running.

## Repository Contract

All four repositories implement the same interface:

```python
class TaskRepository(Protocol):
    def create(self, description: str, status: ValidStatuses) -> Task: ...

    def get_all(
        self,
        status: ValidStatuses | None = None,
    ) -> list[Task]: ...

    def get_by_id(self, task_id: int) -> Task | None: ...

    def update(
        self,
        task_id: int,
        *,
        description: str | None = None,
        status: ValidStatuses | None = None,
    ) -> Task | None: ...

    def delete(self, task_id: int) -> bool: ...
```

This keeps business logic independent of storage implementation and allows the same behavioral tests to be reused for every repository.

## Testing

### Test Database

The shared repository contract includes PostgreSQL-backed implementations, so running the full test suite requires a separate test database.

Create one and apply the same schema:

```sql
CREATE DATABASE task_tracker_test
    OWNER task_tracker_user;
```

```bash
psql "postgresql://task_tracker_user:your_password@localhost:5432/task_tracker_test" \
  -f database/schema.sql
```

Set its URL in `.env`:

```env
TEST_DATABASE_URL=postgresql://task_tracker_user:your_password@localhost:5432/task_tracker_test
```

Do not point `TEST_DATABASE_URL` at a database containing data you want to keep. Repository contract tests truncate the `tasks` table and restart its identity sequence to isolate test cases.

### Run Tests

Run the full suite:

```bash
uv run pytest
```

Run with coverage:

```bash
uv run pytest --cov=. --cov-report=term-missing
```

### Repository Contract Tests

`tests/test_repository_contract.py` parameterizes the same behavioral tests over:

```text
JsonTaskRepository
PsycopgTaskRepository
SqlAlchemyCoreTaskRepository
SqlAlchemyOrmTaskRepository
```

The contract verifies behavior such as:

- creation
- generated IDs
- timestamps
- ordering
- status filtering
- lookup by ID
- partial updates
- no-op updates
- deletion
- behavior for missing tasks

### Database-Specific Tests

`tests/test_database_constraints.py` checks behavior enforced directly by PostgreSQL, independently of a repository implementation.

For example, it verifies that the database rejects descriptions that violate the schema `CHECK` constraint.

`tests/test_database_connection.py` verifies SQLAlchemy connection URL conversion.

## Code Quality

Format the project with Ruff:

```bash
uv run ruff format .
```

Run lint checks:

```bash
uv run ruff check .
```

A useful pre-commit sequence is:

```bash
uv run ruff format .
uv run ruff check .
uv run pytest
git diff
git status
```

## Current Persistence Design

The PostgreSQL schema currently lives in `database/schema.sql`.

SQLAlchemy metadata describes the columns needed by the ORM and Core repositories, while PostgreSQL remains responsible for the database-level constraints defined in the SQL schema.

A natural next learning step is to introduce Alembic so schema changes can be versioned as migrations instead of being maintained only through a standalone SQL file.

## License

See [LICENSE](LICENSE).

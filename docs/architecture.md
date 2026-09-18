# Architecture

## Entry points

- CLI
- HTTP API

Both entry points use the same service layer.

## Persistence

Repositories implement a common repository interface.

Current implementations:

- JSON
- Psycopg
- SQLAlchemy ORM
- SQLAlchemy Core

## Validation

Entry points may normalize and validate input format.

Business rules are enforced in the service layer.

## Naming conventions

- Python: snake_case
- Storage: snake_case
- HTTP JSON: camelCase
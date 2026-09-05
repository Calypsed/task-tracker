from enum import StrEnum

JSON_FILENAME = "tasks.json"
KEY_NEXT_ID = "nextID"
KEY_TASKS = "tasks"
KEY_ID = "task_id"
KEY_DESCRIPTION = "description"
KEY_STATUS = "status"
KEY_CREATED_AT = "createdAt"
KEY_UPDATED_AT = "updatedAt"
ERROR_NO_TASKS = "No tasks at the moment!"
ERROR_ID_NOT_FOUND = "No task with such id found!"


class RepositoryType(StrEnum):
    JSON = "json"
    PSYCOPG = "psycopg"
    SQLALCHEMY_ORM = "sqlalchemy_orm"

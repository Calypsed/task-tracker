from enum import StrEnum

JSON_FILENAME = "tasks.json"
KEY_TASKS = "tasks"
ERROR_NO_TASKS = "No tasks at the moment!"
ERROR_ID_NOT_FOUND = "No task with such id found!"

KEY_API_ID = "id"
KEY_API_DESCRIPTION = "description"
KEY_API_STATUS = "status"
KEY_API_DUE_AT = "dueAt"
KEY_API_CREATED_AT = "createdAt"
KEY_API_UPDATED_AT = "updatedAt"

KEY_STORAGE_ID = "id"
KEY_STORAGE_DESCRIPTION = "description"
KEY_STORAGE_STATUS = "status"
KEY_STORAGE_DUE_AT = "due_at"
KEY_STORAGE_CREATED_AT = "created_at"
KEY_STORAGE_UPDATED_AT = "updated_at"

KEY_JSON_NEXT_ID = "next_id"


class RepositoryType(StrEnum):
    JSON = "json"
    PSYCOPG = "psycopg"
    SQLALCHEMY_ORM = "sqlalchemy_orm"
    SQLALCHEMY_CORE = "sqlalchemy_core"

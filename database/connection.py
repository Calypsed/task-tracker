from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker


def make_sqlalchemy_url(database_url: str) -> str:
    if database_url.startswith("postgresql+psycopg://"):
        return database_url

    if database_url.startswith("postgresql://"):
        return database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )

    return database_url


def make_engine(database_url: str) -> Engine:
    sqlalchemy_url = make_sqlalchemy_url(database_url)
    return create_engine(sqlalchemy_url)


def make_session_factory(
    engine: Engine,
) -> sessionmaker[Session]:
    return sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

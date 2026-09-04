from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def create_session_factory(
    database_url: str,
) -> sessionmaker[Session]:
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )

    engine = create_engine(database_url)

    return sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from app.core.config import settings

postgres_engine = create_engine(
    settings.postgres_connection_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False
)

PostgresSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=postgres_engine)

Base = declarative_base()

def get_postgres_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a PostgreSQL database session for Auth & Metadata.
    """
    db = PostgresSessionLocal()
    try:
        yield db
    finally:
        db.close()

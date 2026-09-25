from typing import Generator, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# Create MySQL Engine with connection pooling
mysql_engine = create_engine(
    settings.mysql_connection_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False
)

MySQLSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mysql_engine)

def get_mysql_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a SQLAlchemy database session
    and ensures it is properly closed after request completion.
    """
    db = MySQLSessionLocal()
    try:
        yield db
    finally:
        db.close()

def execute_readonly_query(sql_query: str) -> List[Dict[str, Any]]:
    """
    Executes a read-only SQL query against the MySQL company database
    and returns a list of dictionaries with column names as keys.
    """
    with mysql_engine.connect() as connection:
        result = connection.execute(text(sql_query))
        if result.returns_rows:
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            return rows
        return []

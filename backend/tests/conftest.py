import pytest
import pymysql
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.db.postgres_session import PostgresSessionLocal

@pytest.fixture(scope="session")
def mysql_conn():
    conn = pymysql.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DB,
        autocommit=True
    )
    yield conn
    conn.close()

@pytest.fixture(scope="function")
def mysql_cursor(mysql_conn):
    cursor = mysql_conn.cursor()
    yield cursor
    cursor.close()

@pytest.fixture(scope="session")
def postgres_db():
    db = PostgresSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client

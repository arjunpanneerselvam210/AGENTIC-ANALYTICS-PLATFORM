import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """
    Application Settings loaded from environment variables or .env file.
    Follows 12-factor application methodology.
    """
    # General
    APP_NAME: str = "Agentic Analytics Platform"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = "agentic-secret-key-change-in-production-only-for-local-dev"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Company Business Database (MySQL)
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DB: str = "company_analytics"

    # Metadata & Authentication Database (PostgreSQL)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "root"
    POSTGRES_DB: str = "company_auth"

    # Local LLM Engine (Ollama)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_AGENT_MODEL: str = "llama3.1:8b"
    OLLAMA_SQL_MODEL: str = "qwen2.5-coder:7b"

    # MCP Server Settings
    MCP_SERVER_NAME: str = "freshmart-analytics-mcp"
    MCP_MYSQL_USER: str | None = None
    MCP_MYSQL_PASSWORD: str | None = None
    MCP_MAX_RESULT_ROWS: int = 1000
    MCP_MAX_SQL_LENGTH: int = 10000
    MCP_QUERY_TIMEOUT_SECONDS: int = 10

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def mysql_connection_url(self) -> str:
        """SQLAlchemy URL for MySQL business database"""
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}?charset=utf8mb4"

    @property
    def mcp_mysql_user(self) -> str:
        """Read-only user for MCP queries, fallback to MYSQL_USER if not set"""
        return self.MCP_MYSQL_USER or self.MYSQL_USER

    @property
    def mcp_mysql_password(self) -> str:
        """Read-only password for MCP queries, fallback to MYSQL_PASSWORD if not set"""
        return self.MCP_MYSQL_PASSWORD or self.MYSQL_PASSWORD

    @property
    def mcp_mysql_connection_url(self) -> str:
        """Connection URL for MCP server with read-only credentials"""
        return f"mysql+pymysql://{self.mcp_mysql_user}:{self.mcp_mysql_password}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}?charset=utf8mb4"

    @property
    def postgres_connection_url(self) -> str:
        """SQLAlchemy URL for PostgreSQL auth & metadata database"""
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()


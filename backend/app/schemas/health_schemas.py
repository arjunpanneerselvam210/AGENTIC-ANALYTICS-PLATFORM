"""
Health and diagnostics response schemas for FreshMart API.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class HealthSimpleResponse(BaseModel):
    """Liveness probe response model."""
    status: str = Field("ok", description="Liveness status of the backend API", example="ok")

class ServiceFastAPIInfo(BaseModel):
    status: str = Field("online", description="FastAPI server execution status", example="online")

class ServiceOllamaInfo(BaseModel):
    status: str = Field("online", description="Ollama LLM service connectivity status", example="online")
    url: Optional[str] = Field(None, description="Configured Ollama base endpoint", example="http://localhost:11434")
    available_models: List[str] = Field(default_factory=list, description="Models currently pulled and available in Ollama", example=["llama3.1:8b", "qwen2.5-coder:7b"])
    required_sql_model: str = Field(..., description="Configured model for SQL generation", example="qwen2.5-coder:7b")
    required_agent_model: str = Field(..., description="Configured model for multi-agent reasoning", example="llama3.1:8b")
    sql_model_ready: bool = Field(True, description="Whether SQL model is ready", example=True)
    agent_model_ready: bool = Field(True, description="Whether agent model is ready", example=True)
    error: Optional[str] = Field(None, description="Error message if offline")

class ServiceDatabaseInfo(BaseModel):
    status: str = Field("online", description="Database connection status", example="online")
    host: Optional[str] = Field(None, description="Database host endpoint", example="localhost:3306")
    version: Optional[str] = Field(None, description="Database server software version", example="8.0.36")
    error: Optional[str] = Field(None, description="Error message if offline")

class HealthServicesMap(BaseModel):
    fastapi: ServiceFastAPIInfo = Field(..., description="FastAPI web application status")
    ollama: ServiceOllamaInfo = Field(..., description="Ollama local LLM engine status")
    mysql: ServiceDatabaseInfo = Field(..., description="MySQL business database status")
    postgresql: ServiceDatabaseInfo = Field(..., description="PostgreSQL auth database status")

class HealthDetailedResponse(BaseModel):
    """Detailed health check response model with component diagnostics."""
    status: str = Field("healthy", description="Overall system health status (healthy, degraded, offline)", example="healthy")
    python_version: str = Field(..., description="Python runtime environment version", example="3.13.15")
    services: HealthServicesMap = Field(..., description="Detailed statuses of connected backend dependencies")

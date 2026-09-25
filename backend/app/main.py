"""
FreshMart Agentic Analytics Platform - Main FastAPI Application.

Provides professional enterprise REST APIs for:
- JWT Bearer Authentication & RBAC Verification
- Natural-Language Analytics via LangGraph & Model Context Protocol (MCP)
- Executive Dashboards & Grounded Business Telemetry
- User and Role Administration
- Multi-Service Health & Connectivity Diagnostics
"""

import sys
import httpx
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.core.config import settings
from app.api import auth, admin, chat, analytics
from app.schemas.health_schemas import HealthSimpleResponse, HealthDetailedResponse
from app.schemas.auth_schemas import LoginRequest

API_TITLE = "FreshMart Agentic Analytics API"
API_VERSION = "1.0.0"

API_DESCRIPTION = """
# FreshMart Agentic Analytics API

Welcome to the **FreshMart Agentic Analytics Platform** enterprise API documentation.

FreshMart Agentic Analytics provides secure, AI-powered natural-language analytics for FreshMart enterprise business data across retail operations, customer relationship management, human resources, inventory warehousing, purchasing, and financial performance.

---

### Core Platform Capabilities

* **AI-Powered Natural-Language Analytics:** Inquire in plain English (e.g., *"Why did profit decrease in August?"* or *"Show monthly sales trend for the last 12 months"*).
* **LangGraph Multi-Agent Orchestration:** Specialized agents collaborate autonomously:
  * **Intent Classifier:** Detects analytical goal, business domain, and inquiry category.
  * **Permission Checker:** Enforces database table and column-level RBAC prior to query generation.
  * **Schema Planner:** Dynamically inspects schemas using the Model Context Protocol (MCP).
  * **SQL Generator & Corrector:** Synthesizes read-only SQL via local `qwen2.5-coder:7b`.
  * **SQL Validator:** Rigorous AST parser preventing non-SELECT, destructive, or unauthorized queries.
  * **SQL Executor:** Safely runs validated SQL through MCP with row bounding and timeout limits.
  * **Investigation Planner & Root-Cause Agent:** Formulates diagnostic hypotheses and performs multi-step period-over-period variance decomposition.
  * **Business Analyzer & Response Generator:** Grounded narrative synthesis powered by `llama3.1:8b`.
* **Model Context Protocol (MCP) Read-Only Database Layer:** Controlled, secure interface ensuring the AI agents only access approved business databases with read-only credentials.
* **Deterministic Executive Dashboard:** Direct real-time MySQL executive metrics, KPI cards, sales velocity, category distributions, and inventory deficits.
* **Enterprise Security & RBAC:** Authoritative PostgreSQL JWT Bearer authentication with 7 enterprise roles and 11 granular permission codes.
* **Data Provenance & Auditability:** Responses include citations of underlying database tables, columns, and metric calculations.

---

### Authentication & Authorization

All analytics, dashboard, admin, and chat endpoints require JWT Bearer authentication:
1. Obtain an access token via `POST /api/v1/auth/login` or click the **Authorize** button in Swagger UI.
2. Provide the token in the `Authorization` header as: `Bearer <token>`.
3. The platform validates role permissions on every request before any analytical workflow or database query is initiated.

---

### Interactive Swagger UI Testing

Use the **Authorize** button above to authenticate with one of the following demo credentials:
* **CEO (Full enterprise access):** `ceo` / `CeoPassword123!`
* **Sales Manager:** `sales.manager` / `SalesPassword123!`
* **Finance Manager:** `finance.manager` / `FinancePassword123!`
* **HR Manager:** `hr.manager` / `HrPassword123!`
* **Inventory Manager:** `inventory.manager` / `InventoryPassword123!`
* **ERP Manager:** `erp.manager` / `ErpPassword123!`
* **System Administrator:** `admin` / `AdminPassword123!`
"""

TAGS_METADATA = [
    {
        "name": "Authentication",
        "description": "User authentication, JWT token issuance, session verification, and permission introspection."
    },
    {
        "name": "Agentic Analytics",
        "description": "Natural-language enterprise analytics powered by LangGraph multi-agent orchestration and MCP database access."
    },
    {
        "name": "Executive Dashboard",
        "description": "Deterministic real-time KPI metrics, sales velocity trends, category distributions, and business telemetry."
    },
    {
        "name": "User Management",
        "description": "Administrative endpoints to list, provision, activate, and deactivate application users (Requires MANAGE_USERS permission)."
    },
    {
        "name": "Role Management",
        "description": "Administrative endpoints to inspect roles and assign permissions (Requires MANAGE_ROLES permission)."
    },
    {
        "name": "AI Chatbot",
        "description": "Role-scoped conversational AI assistant for business guidance and general analytics inquiries."
    },
    {
        "name": "Health & Diagnostics",
        "description": "Liveness probes and diagnostic health checks for FastAPI, Ollama LLM, MySQL, and PostgreSQL services."
    },
    {
        "name": "General",
        "description": "General service metadata and root greeting."
    }
]

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=TAGS_METADATA,
    contact={
        "name": "FreshMart Enterprise Analytics Engineering Team",
        "email": "analytics-engineering@freshmart.local"
    },
    license_info={
        "name": "Proprietary / Enterprise Edition"
    },
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "docExpansion": "list",
        "filter": True,
        "syntaxHighlight.theme": "monokai"
    }
)

# Enable CORS for local React/Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)
app.include_router(chat.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)

# Custom OpenAPI configuration ensuring bearerAuth security scheme & schema components
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
        contact=app.contact,
        license_info=app.license_info
    )
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    if "securitySchemes" not in openapi_schema["components"]:
        openapi_schema["components"]["securitySchemes"] = {}
    
    # Configure Bearer Authentication scheme for Swagger UI
    openapi_schema["components"]["securitySchemes"]["bearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "JWT Authorization header using the Bearer scheme. Enter token directly or as 'Bearer <token>'."
    }

    # Ensure LoginRequest schema is registered in components.schemas
    if "schemas" not in openapi_schema["components"]:
        openapi_schema["components"]["schemas"] = {}
    if "LoginRequest" not in openapi_schema["components"]["schemas"]:
        openapi_schema["components"]["schemas"]["LoginRequest"] = LoginRequest.model_json_schema()

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get(
    "/",
    tags=["General"],
    summary="API Welcome & Service Metadata",
    description="Returns basic application metadata, active environment, and links to documentation.",
    operation_id="getRootServiceInfo"
)
async def root():
    return {
        "message": "Welcome to FreshMart Agentic Analytics Platform API",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": API_VERSION,
        "docs": "/docs",
        "openapi": "/openapi.json",
        "redoc": "/redoc"
    }

@app.get(
    "/health",
    response_model=HealthSimpleResponse,
    tags=["Health & Diagnostics"],
    summary="API Health Check (Liveness Probe)",
    description="Lightweight liveness probe endpoint returning basic operational status.",
    operation_id="getLivenessHealthCheck",
    responses={
        200: {
            "model": HealthSimpleResponse,
            "description": "API is online and accepting connections."
        }
    }
)
async def root_health():
    """Simple liveness probe for load balancers and orchestrators."""
    return {"status": "ok"}

@app.get(
    f"{settings.API_V1_PREFIX}/health",
    response_model=HealthDetailedResponse,
    tags=["Health & Diagnostics"],
    summary="Detailed System & Services Diagnostic Check",
    description=(
        "Performs real-time connectivity and readiness diagnostics across all FreshMart backend dependencies:\n"
        "- FastAPI Web Server\n"
        "- Ollama LLM Service & Required Models (`llama3.1:8b`, `qwen2.5-coder:7b`)\n"
        "- FreshMart MySQL Business Database\n"
        "- PostgreSQL Authentication Database"
    ),
    operation_id="getDetailedSystemHealthCheck",
    responses={
        200: {
            "model": HealthDetailedResponse,
            "description": "Complete service diagnostic report returned."
        }
    }
)
async def health_check():
    """
    Verifies the status of all local services:
    - FastAPI Backend
    - Ollama LLM Server & configured models
    - MySQL connectivity
    - PostgreSQL connectivity
    """
    health_status = {
        "status": "healthy",
        "python_version": sys.version.split(" ")[0],
        "services": {
            "fastapi": {"status": "online"},
            "ollama": {
                "status": "unknown",
                "available_models": [],
                "required_sql_model": settings.OLLAMA_SQL_MODEL,
                "required_agent_model": settings.OLLAMA_AGENT_MODEL,
                "sql_model_ready": False,
                "agent_model_ready": False
            },
            "mysql": {"status": "unknown"},
            "postgresql": {"status": "unknown"}
        }
    }

    # 1. Check Ollama
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                model_names = [m.get("name") for m in data.get("models", [])]
                health_status["services"]["ollama"] = {
                    "status": "online",
                    "url": settings.OLLAMA_BASE_URL,
                    "available_models": model_names,
                    "required_sql_model": settings.OLLAMA_SQL_MODEL,
                    "required_agent_model": settings.OLLAMA_AGENT_MODEL,
                    "sql_model_ready": any(settings.OLLAMA_SQL_MODEL in m for m in model_names),
                    "agent_model_ready": any(settings.OLLAMA_AGENT_MODEL in m for m in model_names)
                }
            else:
                health_status["services"]["ollama"] = {
                    "status": "error",
                    "available_models": [],
                    "required_sql_model": settings.OLLAMA_SQL_MODEL,
                    "required_agent_model": settings.OLLAMA_AGENT_MODEL,
                    "sql_model_ready": False,
                    "agent_model_ready": False,
                    "error": f"Ollama HTTP {resp.status_code}"
                }
    except Exception as e:
        health_status["services"]["ollama"] = {
            "status": "offline",
            "available_models": [],
            "required_sql_model": settings.OLLAMA_SQL_MODEL,
            "required_agent_model": settings.OLLAMA_AGENT_MODEL,
            "sql_model_ready": False,
            "agent_model_ready": False,
            "error": str(e)
        }

    # 2. Check MySQL
    try:
        import pymysql
        conn = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            connect_timeout=2
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION();")
            ver = cursor.fetchone()
        conn.close()
        health_status["services"]["mysql"] = {
            "status": "online",
            "host": f"{settings.MYSQL_HOST}:{settings.MYSQL_PORT}",
            "version": ver[0] if ver else "unknown"
        }
    except Exception as e:
        health_status["services"]["mysql"] = {"status": "offline", "error": str(e)}

    # 3. Check PostgreSQL
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            dbname="postgres",
            connect_timeout=2
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            ver = cursor.fetchone()
        conn.close()
        health_status["services"]["postgresql"] = {
            "status": "online",
            "host": f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}",
            "version": ver[0].split(",")[0] if ver else "unknown"
        }
    except Exception as e:
        health_status["services"]["postgresql"] = {"status": "offline", "error": str(e)}

    # Set overall health based on database connectivity
    if health_status["services"]["mysql"]["status"] != "online" or health_status["services"]["postgresql"]["status"] != "online":
        health_status["status"] = "degraded"

    return health_status

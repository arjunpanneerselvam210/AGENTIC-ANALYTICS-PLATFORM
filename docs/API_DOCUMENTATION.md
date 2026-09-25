# FreshMart Agentic Analytics — API Documentation

Professional developer reference and integration manual for the **FreshMart Agentic Analytics Platform**.

---

## 1. API Overview

The **FreshMart Agentic Analytics API** provides enterprise-grade, role-secured, AI-orchestrated analytics over FreshMart retail operations, supply chain, workforce, and financials.

### Key Capabilities
* **Natural-Language Inquiries:** Submit business questions in plain English to automatically execute secure read-only SQL queries and receive grounded executive explanations.
* **LangGraph Multi-Agent Architecture:** Autonomous agents perform intent classification, permission checking, schema planning, SQL generation, query validation, causal diagnostics, and narrative synthesis.
* **Model Context Protocol (MCP):** A standardized, controlled, read-only interface isolating the AI pipeline from direct raw database mutations.
* **Deterministic Executive Dashboards:** Real-time KPI summaries, 12-month sales velocity trends, category revenue distributions, SKU stock balances, and ledger-grounded anomaly alerts.
* **Dual Database Architecture:** High-volume business transactional data hosted in **MySQL** (`company_analytics`), decoupled from authentication credentials and RBAC rules stored in **PostgreSQL** (`company_auth`).
* **Authoritative JWT Authentication & RBAC:** Endpoints enforce Role-Based Access Control at the API barrier prior to agent or database execution.

---

## 2. Architecture

```
                    +--------------------------------------------+
                    |        Client (React / Swagger UI)         |
                    +---------------------+----------------------+
                                          | HTTP REST (JSON / Bearer JWT)
                                          v
                    +--------------------------------------------+
                    |             FastAPI Web Server             |
                    |           (Host: localhost:8000)           |
                    +---------------------+----------------------+
                                          |
         +--------------------------------+--------------------------------+
         | (Auth & RBAC Verification)                                      | (Query & Telemetry)
         v                                                                 v
+-------------------------------+                       +------------------------------------+
|  PostgreSQL (`company_auth`)  |                       | LangGraph Multi-Agent Orchestrator |
|  - Users, Passwords (bcrypt)  |                       |  1. Intent Classifier              |
|  - 7 Roles & 11 Permissions   |                       |  2. Permission Checker (RBAC)      |
+-------------------------------+                       |  3. Schema Planner (via MCP)       |
                                                        |  4. SQL Generator (Qwen 2.5-Coder) |
                                                        |  5. SQL AST Security Validator     |
                                                        |  6. SQL Executor (MCP Read-Only)   |
                                                        |  7. Investigation Planner & Causal |
                                                        |  8. Business Analyzer (Llama 3.1)  |
                                                        +-----------------+------------------+
                                                                          |
                                                        +-----------------v------------------+
                                                        |  Model Context Protocol (MCP)      |
                                                        |  Tools: describe_table,            |
                                                        |         execute_read_only_sql      |
                                                        +-----------------+------------------+
                                                                          | Read-Only SQL (Max 1000 rows)
                                                        +-----------------v------------------+
                                                        |     MySQL (`company_analytics`)    |
                                                        |     - sales_orders & items         |
                                                        |     - products & inventory         |
                                                        |     - customers & leads            |
                                                        |     - departments & employees      |
                                                        |     - company_financials & expenses|
                                                        +------------------------------------+
```

---

## 3. Base URLs & Interactive Documentation

| Resource | URL | Description |
| :--- | :--- | :--- |
| **Base API URL** | `http://localhost:8000` | Local FastAPI backend root |
| **API v1 Prefix** | `http://localhost:8000/api/v1` | Versioned endpoint prefix |
| **Swagger UI** | `http://localhost:8000/docs` | Interactive OpenAPI 3.1 exploration & testing |
| **ReDoc** | `http://localhost:8000/redoc` | Clean, responsive technical reference documentation |
| **OpenAPI Schema** | `http://localhost:8000/openapi.json` | Raw OpenAPI 3.1 machine-readable specification |

---

## 4. Authentication

The FreshMart API uses **JSON Web Tokens (JWT)** signed via **HMAC-SHA256 (`HS256`)**.

### How to Authenticate
1. Call `POST /api/v1/auth/login` with your username and password.
2. The response returns an `access_token` and the user's granted permissions.
3. Include the token in subsequent requests via the HTTP `Authorization` header:
   ```http
   Authorization: Bearer <your_jwt_access_token>
   ```

### Swagger UI "Authorize" Button
Swagger UI supports standard Bearer token entry:
1. Open `http://localhost:8000/docs`.
2. Click the green **Authorize** button in the top right.
3. In the `bearerAuth` field, enter your JWT token directly or enter username/password in `OAuth2PasswordBearer`.
4. Click **Authorize**. Authorization persists across page refreshes.

### Available Demo Accounts

| Username | Password | Role | Description |
| :--- | :--- | :--- | :--- |
| `ceo` | `CeoPassword123!` | `CEO` | Executive access across all business domains |
| `sales.manager` | `SalesPassword123!` | `SALES_MANAGER` | Sales orders, customer CRM, catalog inventory |
| `finance.manager` | `FinancePassword123!` | `FINANCE_MANAGER` | Financial statements, P&L, expenses, profit |
| `hr.manager` | `HrPassword123!` | `HR_MANAGER` | Workforce directory, departments, employee salaries |
| `inventory.manager` | `InventoryPassword123!` | `INVENTORY_MANAGER` | Products, warehouse stock, purchasing orders |
| `erp.manager` | `ErpPassword123!` | `ERP_MANAGER` | Procurement, inventory, sales, expenses, HR |
| `admin` | `AdminPassword123!` | `ADMIN` | System administrator (user & role management) |

---

## 5. Authorization & RBAC

FreshMart implements strict, authoritative Role-Based Access Control enforced at the backend barrier.

### 11 Granular Permissions Matrix

| Permission Code | Category | Description | Granted Roles |
| :--- | :--- | :--- | :--- |
| `VIEW_SALES` | Sales | View sales orders, order items, and revenue | `CEO`, `SALES_MANAGER`, `ERP_MANAGER`, `INVENTORY_MANAGER`, `FINANCE_MANAGER` |
| `VIEW_CRM` | CRM | View customer records, leads, and interactions | `CEO`, `SALES_MANAGER` |
| `VIEW_INVENTORY` | Inventory | View products, catalog, and warehouse stock | `CEO`, `SALES_MANAGER`, `ERP_MANAGER`, `INVENTORY_MANAGER` |
| `VIEW_PURCHASES` | Purchases | View suppliers, purchase orders, and item costs | `CEO`, `ERP_MANAGER`, `INVENTORY_MANAGER` |
| `VIEW_FINANCE` | Finance | View overall company revenue and P&L ledger | `CEO`, `FINANCE_MANAGER` |
| `VIEW_PROFIT` | Finance | View net profit, margins, and cost variance | `CEO`, `FINANCE_MANAGER` |
| `VIEW_EXPENSES` | Finance | View department expenditures and operational costs | `CEO`, `HR_MANAGER`, `ERP_MANAGER`, `FINANCE_MANAGER` |
| `VIEW_HR` | HRMS | View departments, employee directory, and jobs | `CEO`, `HR_MANAGER`, `ERP_MANAGER` |
| `VIEW_EMPLOYEE_SALARY` | HRMS | View sensitive employee salary and bonus records | `CEO`, `HR_MANAGER` |
| `MANAGE_USERS` | Admin | Create, edit, activate, and deactivate users | `ADMIN` |
| `MANAGE_ROLES` | Admin | Assign roles and manage permission matrices | `ADMIN` |

---

## 6. Analytics API (`POST /api/v1/analytics/query`)

The primary intelligence endpoint of the FreshMart platform.

* **Summary:** Run Natural-Language Business Analytics Query
* **Operation ID:** `runNaturalLanguageAnalyticsQuery`
* **Authentication:** Required (`Bearer <JWT>`)
* **Permissions Required:** Dynamically checked based on tables needed (e.g. `VIEW_SALES`, `VIEW_FINANCE`, `VIEW_EMPLOYEE_SALARY`). Unauthorized requests receive `403 Forbidden`.

### Request Schema (`AnalyticsQueryRequest`)
| Field | Type | Required | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `question` | `string` | **Yes** | Natural-language business analytics question (1-2000 chars) | `"Why did profit decrease in August?"` |
| `conversation_id` | `string` | No | Optional session ID for conversation continuity | `"session-001"` |

### Response Schema (`AnalyticsQueryResponse`)
| Field | Type | Description |
| :--- | :--- | :--- |
| `success` | `boolean` | Flag indicating query success |
| `question` | `string` | The submitted natural-language inquiry |
| `answer` | `string` | Grounded executive answer synthesized by AI |
| `data` | `object` | Tabular SQL results (`columns`, `rows`, `row_count`, `truncated`) |
| `intent` | `object` | Classified intent domain and metric goals |
| `sources` | `array` | Table and column provenance citations |
| `columns_used` | `array` | Columns referenced in SQL execution |
| `visualization_hint`| `object\|string` | Frontend charting recommendation (`type`, `x_axis`, `y_axis`, `title`) |
| `investigation_plan`| `object` | Step-by-step diagnostic plan (for complex multi-step inquiries) |
| `root_cause_analysis`| `object` | Structured causal breakdown (periods, metrics, factors, confidence) |
| `comparisons` | `array` | Period-over-period or dimension-over-dimension variances |
| `trends` | `object` | Directional time-series trend velocity and summaries |
| `anomalies` | `array` | Statistical anomalies or ledger threshold breaches |
| `insights` | `array` | Telemetry-grounded business insights |
| `recommendations` | `array` | Strategic and operational actionable recommendations |
| `confidence` | `string` | Synthesis confidence (`HIGH`, `MEDIUM`, `LOW`) |
| `user_role` | `string` | Requesting user's role |
| `user_name` | `string` | Requesting user's display name |
| `timestamp` | `string` | UTC timestamp of response generation |

---

## 7. Executive Dashboard & Insights APIs

### 1. `GET /api/v1/analytics/dashboard`
* **Summary:** Get Executive Dashboard KPIs & Sales Velocity Trends
* **Operation ID:** `getExecutiveDashboardMetrics`
* **Query Parameters:**
  * `range` (`string`, optional, default `"12m"`): Time window (`today`, `7d`, `30d`, `90d`, `12m`, `custom`)
* **Response:** Deterministic dashboard object containing:
  * `kpis`: Total Revenue, Total Customers, Total Orders, Active Employees
  * `sales_trend`: 12-month historical revenue and order counts
  * `category_distribution`: Sales distribution by catalog category
  * `top_products`: Top performing SKUs with active warehouse balances
  * `insights`: Grounded executive alerts

### 2. `GET /api/v1/analytics/insights`
* **Summary:** Get Enterprise Insights, Anomalies & Strategic Recommendations
* **Operation ID:** `getEnterpriseInsightsAndAnomalies`
* **Response (`EnterpriseInsightsResponse`):**
  * `insights`: Live structured observations on margin contractions, low-stock SKUs, and freight costs.
  * `anomalies`: Detected statistical outliers (e.g. August 2026 emergency air freight surge).

---

## 8. User Management APIs

Requires `MANAGE_USERS` permission (`ADMIN` role).

| Method | Endpoint | Operation ID | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/admin/users` | `listAllApplicationUsers` | List all application user accounts with assigned roles and permissions |
| `POST` | `/api/v1/admin/users` | `createApplicationUser` | Provision a new user account with bcrypt password hashing |
| `PATCH` | `/api/v1/admin/users/{user_id}/status` | `updateUserAccountStatus` | Enable or disable (deactivate) a user account |
| `PATCH` | `/api/v1/admin/users/{user_id}/role` | `updateUserApplicationRole` | Reassign an application role (Requires `MANAGE_ROLES`) |

---

## 9. Role Management APIs

Requires `MANAGE_ROLES` permission (`ADMIN` role).

| Method | Endpoint | Operation ID | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/admin/roles` | `listApplicationRolesAndPermissions` | List all 7 roles with their granted permission codes |

---

## 10. AI Chatbot API

| Method | Endpoint | Operation ID | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/chat/message` | `sendChatMessage` | Conversational inquiries scoped to user's authorized domains |

---

## 11. Health & Diagnostic APIs

| Method | Endpoint | Operation ID | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | `getLivenessHealthCheck` | Lightweight liveness probe returning `{"status": "ok"}` |
| `GET` | `/api/v1/health` | `getDetailedSystemHealthCheck` | Diagnostic report verifying FastAPI, Ollama, MySQL, and PostgreSQL |
| `GET` | `/` | `getRootServiceInfo` | API root greeting and links to documentation |

---

## 12. Model Context Protocol (MCP) Architecture

> [!NOTE]
> MCP is an **internal agentic tool layer** and is not exposed as raw, unauthenticated public REST endpoints. Frontend clients submit natural-language business questions to `/api/v1/analytics/query`, which invokes MCP through authenticated internal agent nodes.

### MCP Tool Responsibilities:
1. `list_tables`: Discovers accessible tables (`sales_orders`, `products`, `inventory`, `employees`, etc.).
2. `describe_table`: Returns column schemas, data types, and foreign key relationships.
3. `execute_read_only_sql`: Safely executes read-only SELECT queries with row limits (default max: 1000 rows) and strict query execution timeouts.

---

## 13. HTTP Status Codes & Error Handling

All endpoints follow consistent RFC 7807-compatible error structures:

```json
{
  "detail": "Human-readable explanation of error."
}
```

### Standard Status Codes:
* `200 OK`: Request succeeded.
* `201 Created`: Resource (e.g. user account) provisioned successfully.
* `400 Bad Request`: Invalid parameters, empty query, or duplicate username/email.
* `401 Unauthorized`: Missing, invalid, or expired JWT Bearer token.
* `403 Forbidden`: Account is inactive or user lacks the required RBAC permission code.
* `404 Not Found`: Requested user, role, or resource does not exist.
* `422 Unprocessable Entity`: Request body failed schema validation.
* `500 Internal Server Error`: Pipeline execution or database error.
* `503 Service Unavailable`: Local Ollama LLM or backend service offline.

---

## 14. Practical Request & Response Examples

### Example 1: Authenticate User
**Request:**
```http
POST /api/v1/auth/login HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "username": "ceo",
  "password": "CeoPassword123!"
}
```

**Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": 2,
    "username": "ceo",
    "email": "ceo@freshmart.local",
    "full_name": "Vikram Malhotra",
    "role": "CEO",
    "employee_id": "E006",
    "permissions": [
      "VIEW_HR",
      "VIEW_EMPLOYEE_SALARY",
      "VIEW_CRM",
      "VIEW_SALES",
      "VIEW_INVENTORY",
      "VIEW_PURCHASES",
      "VIEW_FINANCE",
      "VIEW_PROFIT",
      "VIEW_EXPENSES"
    ],
    "is_active": true
  }
}
```

---

### Example 2: Run Natural-Language Analytics Query
**Request:**
```http
POST /api/v1/analytics/query HTTP/1.1
Host: localhost:8000
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "question": "Why did profit decrease in August?"
}
```

**Response (`200 OK`):**
```json
{
  "success": true,
  "question": "Why did profit decrease in August?",
  "answer": "Net profit contracted by 50.0% (-₹600,000) from ₹1,200,000 in July to ₹600,000 in August 2026. The primary driver was a +381.4% surge in emergency refrigerated air freight expenditures (₹430,000 vs. ₹89,326 in July) and wholesale produce spot-market procurement premiums.",
  "data": {
    "columns": ["month_name", "total_revenue", "cogs", "operating_expenses", "net_profit", "profit_margin_pct"],
    "rows": [
      {"month_name": "July", "total_revenue": 10500000.0, "cogs": 7100000.0, "operating_expenses": 2200000.0, "net_profit": 1200000.0, "profit_margin_pct": 11.43},
      {"month_name": "August", "total_revenue": 9800000.0, "cogs": 6900000.0, "operating_expenses": 2300000.0, "net_profit": 600000.0, "profit_margin_pct": 6.12}
    ],
    "row_count": 2,
    "truncated": false
  },
  "intent": {
    "domain": "Finance",
    "operation": "ROOT_CAUSE",
    "target_metric": "net_profit"
  },
  "sources": [
    {
      "table": "company_financials",
      "columns": ["month_name", "total_revenue", "cogs", "operating_expenses", "net_profit"],
      "purpose": "Compute monthly profit variances"
    },
    {
      "table": "expenses",
      "columns": ["expense_date", "category", "amount"],
      "purpose": "Identify emergency shipping expenditure spike"
    }
  ],
  "columns_used": ["total_revenue", "cogs", "operating_expenses", "net_profit"],
  "visualization_hint": {
    "type": "bar",
    "x_axis": "month_name",
    "y_axis": "net_profit",
    "title": "Net Profit Comparison: July vs. August 2026"
  },
  "root_cause_analysis": {
    "analysis_type": "ROOT_CAUSE",
    "summary": "Profit decreased primarily due to emergency refrigerated freight costs during monsoon supply disruptions.",
    "period": {
      "current": "August 2026",
      "previous": "July 2026"
    },
    "metrics": {
      "profit_change_pct": -50.0,
      "absolute_profit_delta": -600000.0
    },
    "factors": [
      {
        "factor": "Emergency Air Freight Logistics Surge",
        "previous_value": 89326.0,
        "current_value": 430000.0,
        "change": 340674.0,
        "change_pct": 381.4,
        "impact": "negative",
        "confidence": "HIGH",
        "source": ["expenses"]
      }
    ],
    "confidence": "HIGH"
  },
  "recommendations": [
    {
      "title": "Institute Emergency Logistics Surcharge Buffers",
      "reason": "Uncontracted spot-market freight costs eroded 50% of monthly operating margin.",
      "priority": "HIGH",
      "related_domain": "Finance",
      "suggested_action": "Secure secondary contracted regional logistics carriers with fixed surge rate caps."
    }
  ],
  "confidence": "HIGH",
  "user_role": "CEO",
  "user_name": "Vikram Malhotra",
  "timestamp": "2026-09-25T15:20:00Z"
}
```

---

### Example 3: Unauthorized Request (RBAC Enforcement)
**Request:**
Sales Manager querying employee salaries:
```http
POST /api/v1/analytics/query HTTP/1.1
Host: localhost:8000
Authorization: Bearer <SALES_MANAGER_JWT>
Content-Type: application/json

{
  "question": "Show average employee salary by department."
}
```

**Response (`403 Forbidden`):**
```json
{
  "detail": "Access Denied: You do not have permission 'VIEW_EMPLOYEE_SALARY'."
}
```

---

## 15. Local Development & Verification

### Start FastAPI Server
```powershell
cd backend
.\.venv\Scripts\uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Validate OpenAPI Specification
```powershell
cd backend
.\.venv\Scripts\python scripts/validate_openapi.py
```

### Export OpenAPI JSON & YAML
```powershell
cd backend
.\.venv\Scripts\python scripts/export_openapi.py
```

### Run Automated Backend Unit Tests
```powershell
cd backend
.\.venv\Scripts\python -m pytest tests/test_auth_rbac.py tests/test_database_schema.py tests/test_freshmart_data.py tests/test_mcp_server.py -v
```

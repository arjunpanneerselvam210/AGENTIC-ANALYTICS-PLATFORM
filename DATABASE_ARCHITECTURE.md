# FreshMart Database & Security Architecture Guide

**Phase 1 Complete Reference**  
**Agentic Analytics Platform for Enterprise Applications Using MCP & Multi-Agent AI**

---

## 1. Dual-Database Architectural Foundation

The platform strictly isolates business operational telemetry from security and application metadata:

```
                                FreshMart Enterprise
                                          │
            ┌─────────────────────────────┴─────────────────────────────┐
            ▼                                                           ▼
   MySQL Server (Port 3306)                                   PostgreSQL Server (Port 5432)
   Database: `company_analytics`                              Database: `company_auth`
   ──────────────────────────────────                         ─────────────────────────────
   • Human Resources (HRMS)                                   • System Roles (7 Roles)
   • CRM (Customers, Leads, Interactions)                     • Granular Permissions (11 Perms)
   • ERP & Purchasing (Suppliers, POs, Items)                 • Role-Permission Mappings
   • Inventory & Products                                     • Application Users (Bcrypt JWT)
   • Sales (Orders, Items, Revenue)                           • Mapped Employee Linkages
   • Finance & Accounting (P&L, Expenses)
   • 500 Workforce Employee Records
   • Read-only analytics scope for AI / MCP
```

### Core Architecture Principles:
1. **Single Company Scope**: Built exclusively for **FreshMart**. No multi-tenancy overhead, complex tenant routing, or cross-tenant leakage.
2. **Workforce vs Application User Decoupling**:
   - `MySQL.employees` represents corporate personnel entities (500 records).
   - `PostgreSQL.users` represents authorized application logins (7 accounts).
   - Pure system admins exist in PostgreSQL without workforce employee profiles.
   - Enterprise operators (e.g. Sales Manager Arun Kumar) link to their workforce profile via `employee_id = 'E001'`.
3. **Authoritative Backend RBAC**:
   - Permissions are never inferred by LLMs or UI flags.
   - FastAPI enforces cryptographic token validation (`HS256`) and RBAC guards on every request before query execution.

---

## 2. MySQL Schema: `company_analytics`

Covers 7 interconnected enterprise domains across 15 relational tables and 1 compatibility view:

### Domain 1: HRMS (Human Resources Management System)
* **`departments`** (10 records):
  - `dept_id` (PK, VARCHAR(10)): e.g., `D01` to `D10`.
  - `dept_name` (VARCHAR(100), UNIQUE): Sales, HR, Finance, IT, Logistics, Executive, Retail Operations, Procurement, Quality, CRM.
  - `location` (VARCHAR(100)): Physical office / facility / floor.
  - `budget` (DECIMAL(15, 2)): Annual departmental operating budget.
* **`employees`** (500 records):
  - `employee_id` (PK, VARCHAR(10)): `E001` to `E500`.
  - `first_name`, `last_name` (VARCHAR(50)).
  - `email` (VARCHAR(100), UNIQUE): `@freshmart.local`.
  - `phone` (VARCHAR(25)).
  - `department_id` (FK -> `departments.dept_id`).
  - `job_title` (VARCHAR(100)).
  - `hire_date` (DATE): Joining date (2020 - 2025).
  - `date_of_birth` (DATE): Birth date for age analytics.
  - `status` (ENUM('Active', 'On Leave', 'Terminated')).
  - `experience_years` (INT): Years of professional experience.
  - `manager_id` (FK -> `employees.employee_id`, NULLABLE): Self-referential reporting hierarchy.
* **`salaries`** (500 records):
  - `salary_id` (PK, INT AUTO_INCREMENT).
  - `employee_id` (FK -> `employees.employee_id`).
  - `base_salary` (DECIMAL(12, 2)): Monthly compensation (₹35,000 to ₹350,000).
  - `bonus` (DECIMAL(12, 2)): Performance incentive.
  - `effective_date` (DATE), `payment_status` (ENUM), `salary_period` (VARCHAR(20)).

### Domain 2: CRM (Customer Relationship Management)
* **`customers`** (320 records):
  - `customer_id` (PK, VARCHAR(10)): `C001` to `C320`.
  - `company_name` (VARCHAR(120)): B2B retail chains, hotels, restaurants, caterers, grocers.
  - `contact_person`, `email`, `phone`, `city`.
  - `region` (ENUM('North', 'South', 'East', 'West', 'Central')).
  - `industry` (VARCHAR(80)).
* **`leads`** (550 records):
  - `lead_id` (PK, VARCHAR(10)): `L001` to `L550`.
  - `lead_name`, `company_name`, `source` (ENUM).
  - `status` (ENUM('New', 'Contacted', 'Qualified', 'Lost', 'Converted')).
  - `estimated_value` (DECIMAL(12, 2)): Potential contract value.
  - `assigned_employee_id` (FK -> `employees.employee_id`).
  - `converted_customer_id` (FK -> `customers.customer_id`, NULLABLE): Direct conversion tracking.
* **`customer_interactions`** (1200 records):
  - `interaction_id` (PK, INT AUTO_INCREMENT).
  - `customer_id` (FK -> `customers.customer_id`).
  - `employee_id` (FK -> `employees.employee_id`).
  - `interaction_type` (ENUM('Call', 'Meeting', 'Email', 'Support Ticket')).
  - `notes` (TEXT): Detailed meeting notes, pricing inquiries, transit feedback.
  - `interaction_date` (TIMESTAMP).
* **`interactions`** (Compatibility View):
  - Mirrors `customer_interactions` to support both query styles seamlessly.

### Domain 3: ERP, Purchasing & Inventory
* **`suppliers`** (40 records):
  - `supplier_id` (PK, VARCHAR(10)): `S001` to `S040`.
  - `supplier_name`, `contact_person`, `email`, `phone`, `city`, `country`, `rating`.
* **`products`** (220 records):
  - `product_id` (PK, VARCHAR(10)): `P001` to `P220`.
  - `product_name` (VARCHAR(150)).
  - `category` (VARCHAR(100)): Fresh Produce, Dairy & Eggs, Bakery & Breads, Beverages, Packaged & Canned Foods, Meat & Seafood, Snacks & Confectionery, Personal Care, Household Essentials, Organic & Health.
  - `unit_cost` (DECIMAL(10, 2)): Procurement cost.
  - `unit_price` (DECIMAL(10, 2)): Retail selling price.
  - `reorder_level` (INT): Minimum threshold for reorder alerts (15 - 40 units).
  - `is_active` (BOOLEAN).
* **`purchase_orders`** (550 records):
  - `po_id` (PK, VARCHAR(15)): e.g. `PO-200001`.
  - `supplier_id` (FK -> `suppliers.supplier_id`).
  - `order_date`, `delivery_date` (DATE).
  - `total_amount` (DECIMAL(15, 2)).
  - `status` (ENUM('Draft', 'Submitted', 'Shipped', 'Received', 'Cancelled')).
* **`purchase_order_items`** (1637 records):
  - `item_id` (PK, INT AUTO_INCREMENT).
  - `po_id` (FK -> `purchase_orders.po_id`).
  - `product_id` (FK -> `products.product_id`).
  - `quantity` (INT), `unit_cost` (DECIMAL(10, 2)), `subtotal` (DECIMAL(12, 2)).
  - Directly establishes `suppliers -> purchase_orders -> purchase_order_items -> products`.
* **`inventory`** (220 records):
  - `inventory_id` (PK, INT AUTO_INCREMENT).
  - `product_id` (FK -> `products.product_id`, UNIQUE): 1-to-1 stock mapping.
  - `warehouse_location` (VARCHAR(80)): Distribution hub & rack placement.
  - `quantity_on_hand` (INT): Available stock (0 to 500 units).
  - `reserved_quantity` (INT): Allocated to pending dispatches.

### Domain 4: Sales
* **`sales_orders`** (2400 records):
  - `order_id` (PK, VARCHAR(15)): e.g. `SO-200001`.
  - `customer_id` (FK -> `customers.customer_id`).
  - `sales_rep_id` (FK -> `employees.employee_id`).
  - `order_date` (DATE): 21-month historical timeline (Jan 2025 - Sep 2026).
  - `total_amount` (DECIMAL(15, 2)).
  - `region` (ENUM('North', 'South', 'East', 'West', 'Central')).
  - `status` (ENUM('Pending', 'Processing', 'Completed', 'Cancelled')).
* **`sales_order_items`** (7817 records):
  - `item_id` (PK, INT AUTO_INCREMENT).
  - `order_id` (FK -> `sales_orders.order_id`).
  - `product_id` (FK -> `products.product_id`).
  - `quantity` (INT), `unit_price` (DECIMAL(10, 2)), `subtotal` (DECIMAL(12, 2)).
  - `sales_orders.total_amount` mathematically matches the sum of order item subtotals.

### Domain 5: Finance & Root-Cause Analytics
* **`expenses`** (365 records):
  - `expense_id` (PK, INT AUTO_INCREMENT).
  - `department_id` (FK -> `departments.dept_id`).
  - `category` (VARCHAR(100)): Salaries, Rent & Utilities, Marketing, Software & IT, Logistics & Shipping, Emergency Shipping, Procurement, Maintenance, Quality & Compliance.
  - `amount` (DECIMAL(12, 2)), `expense_date` (DATE), `description` (VARCHAR(255)), `payment_method` (ENUM).
* **`company_financials`** (21 records):
  - Monthly P&L statements spanning Jan 2025 to Sep 2026.
  - `total_revenue`, `cogs`, `operating_expenses`, `total_expenses`, `net_profit`, `profit_margin_pct`.
  - Strictly verified: `total_expenses = cogs + operating_expenses`, `net_profit = total_revenue - total_expenses`.

---

## 3. The Demonstrable Profit-Drop Scenario (August 2026)

The dataset contains a deliberate, multi-table root-cause pattern for the future multi-agent analytics:

```
                                 August 2026 Profit Drop
                                           │
          ┌────────────────────────────────┼────────────────────────────────┐
          ▼                                ▼                                ▼
  P&L Statement Spike             Surge in Supplier COGS           Emergency Logistics Spike
  ───────────────────             ──────────────────────           ─────────────────────────
  Revenue:  Rs. 3,850,000         POs in Aug 2026 show +30%        Emergency Shipping in
  COGS:     Rs. 1,950,000 (↑)     unit procurement costs from      expenses table:
  OpEx:     Rs. 1,300,000 (↑)     suppliers due to monsoon         • Rs. 250,000 (Air freight)
  Profit:   Rs.   600,000 (↓)     crop shortfalls.                 • Rs. 180,000 (Cold-chain)
  Margin:   15.58% (vs 28.57% in July)                              Total: Rs. 430,000
```

### Answering "Why did profit decrease in August 2026?"
1. `company_financials`: Reveals net profit plummeted from ₹1,200,000 (July) to ₹600,000 (August).
2. `expenses`: Shows non-standard emergency shipping costs of ₹430,000 in August due to highway disruptions.
3. `purchase_orders` & `purchase_order_items`: Confirms elevated procurement unit costs in August.
4. `customer_interactions`: Logs customer touchpoints discussing transit lead-time adjustments in August.

---

## 4. PostgreSQL Schema: `company_auth`

* **`roles`** (7 Roles): `ADMIN`, `CEO`, `SALES_MANAGER`, `HR_MANAGER`, `FINANCE_MANAGER`, `INVENTORY_MANAGER`, `ERP_MANAGER`.
* **`permissions`** (11 Granular Permissions):
  - `VIEW_HR`, `VIEW_EMPLOYEE_SALARY`, `VIEW_CRM`, `VIEW_SALES`, `VIEW_INVENTORY`, `VIEW_PURCHASES`, `VIEW_FINANCE`, `VIEW_PROFIT`, `VIEW_EXPENSES`, `MANAGE_USERS`, `MANAGE_ROLES`.
* **`role_permissions`**: Declarative junction table assigning allowed permissions to each role.
* **`users`** (7 Seeded Accounts):
  - Bcrypt-hashed passwords (`cost=12`).
  - Linkage to `employee_id` in MySQL.

### Default Local Credentials:
| Username | Role | Password | Mapped Employee | Permitted Access Scope |
| :--- | :--- | :--- | :--- | :--- |
| `admin` | `ADMIN` | `AdminPassword123!` | None (Technical Admin) | System Administration & User Management |
| `ceo` | `CEO` | `CeoPassword123!` | E006 - Vikram Malhotra | Full Company-wide Analytics |
| `sales.manager` | `SALES_MANAGER` | `SalesPassword123!` | E001 - Arun Kumar | CRM, Customers, Leads, Sales Orders |
| `hr.manager` | `HR_MANAGER` | `HrPassword123!` | E002 - Priya Sharma | HRMS, Workforce Directory, Salaries |
| `finance.manager`| `FINANCE_MANAGER`| `FinancePassword123!`| E003 - Rahul Kumar | P&L Summaries, Expenses, Profit Margins |
| `inventory.manager`| `INVENTORY_MANAGER`| `InventoryPassword123!`| E005 - Karthik Raj | Suppliers, Catalog Products, Warehouse Inventory |
| `erp.manager` | `ERP_MANAGER` | `ErpPassword123!` | E007 - Anita Desai | End-to-end Operations, POs, Stock, HR |

---

## 5. Database Management & Seeding Commands

All commands are run using the project virtualenv from the `backend/` directory:

### 1. Complete Re-Initialization & Seed (MySQL):
```powershell
cd "d:\Project\AGENTIC ANALYTICS PLATFORM\backend"
.\.venv\Scripts\python.exe scripts\seed_mysql.py
```

### 2. Complete Re-Initialization & Seed (PostgreSQL Auth & RBAC):
```powershell
cd "d:\Project\AGENTIC ANALYTICS PLATFORM\backend"
.\.venv\Scripts\python.exe scripts\seed_postgres.py
```

### 3. Run Automated Verification Suites:
```powershell
# Phase 1: Local Services (Ollama, MySQL, PostgreSQL, Python 3.13)
.\.venv\Scripts\python.exe scripts\verify_phase1.py

# Phase 2: MySQL Business Data (All 15 tables, 16,350+ records)
.\.venv\Scripts\python.exe scripts\verify_phase2.py

# Phase 3 & 4: PostgreSQL Auth, JWT Security & RBAC Guards
.\.venv\Scripts\python.exe scripts\verify_phase3.py

# Phase 5: Role-Aware Ollama AI Integration
.\.venv\Scripts\python.exe scripts\verify_phase5.py
```

### 4. Run Pytest Test Suite:
```powershell
cd "d:\Project\AGENTIC ANALYTICS PLATFORM\backend"
.\.venv\Scripts\pytest.exe -v
```

---

## 6. Example Analytical Queries (Tested & Supported)

### HR: Employee Distribution & Payroll
```sql
SELECT d.dept_name, COUNT(e.employee_id) AS employees, ROUND(AVG(s.base_salary), 2) AS avg_salary
FROM departments d
JOIN employees e ON d.dept_id = e.department_id
JOIN salaries s ON e.employee_id = s.employee_id
GROUP BY d.dept_id, d.dept_name
ORDER BY avg_salary DESC;
```

### CRM: Lead Pipeline by Status
```sql
SELECT status, COUNT(*) AS count, ROUND(SUM(estimated_value), 2) AS pipeline_value
FROM leads
GROUP BY status
ORDER BY count DESC;
```

### Sales: 12+ Month Revenue Trend
```sql
SELECT DATE_FORMAT(order_date, '%Y-%m') AS month, COUNT(order_id) AS orders, ROUND(SUM(total_amount), 2) AS revenue
FROM sales_orders
GROUP BY month
ORDER BY month ASC;
```

### Inventory: Low Stock Deficit
```sql
SELECT p.product_name, p.category, i.quantity_on_hand, p.reorder_level, (p.reorder_level - i.quantity_on_hand) AS deficit
FROM products p
JOIN inventory i ON p.product_id = i.product_id
WHERE i.quantity_on_hand <= p.reorder_level
ORDER BY i.quantity_on_hand ASC;
```

### Cross-Domain: High-Selling Products with Low Stock
```sql
SELECT p.product_name, p.category, SUM(soi.quantity) AS units_sold, i.quantity_on_hand, p.reorder_level
FROM products p
JOIN sales_order_items soi ON p.product_id = soi.product_id
JOIN inventory i ON p.product_id = i.product_id
WHERE i.quantity_on_hand <= p.reorder_level
GROUP BY p.product_id, p.product_name, p.category, i.quantity_on_hand, p.reorder_level
HAVING units_sold > 50
ORDER BY units_sold DESC;
```

### Root-Cause Analysis: August 2026 P&L and Expense Investigation
```sql
-- Step 1: Financial Drop
SELECT month_name, total_revenue, cogs, operating_expenses, net_profit, profit_margin_pct
FROM company_financials
WHERE fiscal_year = 2026 AND month_num IN (7, 8)
ORDER BY month_num;

-- Step 2: Underlying Cause in Expenses
SELECT category, SUM(amount) AS total_expense
FROM expenses
WHERE expense_date BETWEEN '2026-08-01' AND '2026-08-31'
GROUP BY category
ORDER BY total_expense DESC;
```

---

## 7. Phase 6: MCP Database Server Architecture & Security Boundary

### Architectural Flow:
```
User / Analyst
      │ (Natural Language Prompt + JWT)
      ▼
FastAPI Backend
      │ (RBAC Enforcement & Permission Check)
      ▼
LangGraph Multi-Agent Orchestrator (Phase 7)
      │ (Structured Tool Invocation)
      ▼
MCP Database Server (`freshmart-database-server`)
      │
      ├── Tool 1: `list_tables` (Dynamically introspects MySQL `information_schema.tables`)
      ├── Tool 2: `describe_table` (Inspects columns, types, PKs, FKs for requested table)
      └── Tool 3: `execute_read_only_sql` (Executes safe SELECT / WITH...SELECT queries)
      │
      ▼ Multi-Layer Security Boundary
      ├── Layer 1: Application-level AST & regex validator (`sql_validator.py`)
      │   - Enforces single-statement SELECT / WITH...SELECT only
      │   - Blocks INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, OUTFILE, etc.
      │   - Blocks multi-statement chaining (e.g. `; DROP TABLE...`)
      │   - Blocks locking statements (`FOR UPDATE`, `LOCK IN SHARE MODE`)
      ├── Layer 2: MySQL Session-level Read-Only Mode
      │   - `SET SESSION TRANSACTION READ ONLY;`
      │   - `SET max_execution_time = 10000;` (10s timeout)
      └── Layer 3: Database Engine User Privileges
          - User: `freshmart_mcp_reader`
          - Grants: `GRANT SELECT ON company_analytics.*` only
      │
      ▼
MySQL FreshMart Database (`company_analytics`)
      │ (Structured Data: columns, rows, row_count, truncated)
      ▼
Structured Serialized Response to Agents
```

### Why MCP as a Security Boundary?
1. **Never Trust LLM SQL Directly:** AI models (even fine-tuned SQL models like `Qwen2.5-Coder`) can hallucinate destructive queries, multi-statement payloads, or locking clauses. MCP intercepts all queries before they reach the database engine.
2. **Standardized Protocol:** Model Context Protocol (MCP) provides standard JSON-RPC tool definitions, schema declarations, and typed responses. Agents see consistent tool schemas without raw DB drivers.
3. **Defense-in-Depth:** Even if an attacker or prompt injection crafts malicious SQL that passes validation, the session transaction read-only mode and the MySQL engine-level `freshmart_mcp_reader` grant strictly prohibit write operations.
4. **Guard Against Denial-of-Service:** Query execution timeouts (10s), row count limits (1000 rows max), and SQL length constraints (4000 characters) protect the database from resource exhaustion.

---

## 8. Phase 7: LangGraph Multi-Agent Analytics Pipeline

### End-to-End Orchestration Architecture:
```text
User / Executive
      │ (Natural Language Analytics Question + Bearer JWT)
      ▼
FastAPI Backend (`/api/v1/analytics/query`)
      │ (Decodes JWT, extracts role & permission codes)
      ▼
LangGraph StateGraph (`AnalyticsState`)
      │
      ├── 1. `validate_request` (Rejects empty/malformed questions)
      │        └─► (Invalid -> `generate_response` -> END)
      │
      ├── 2. `classify_intent` (Llama 3.1 8B classifies domain, metric, candidate tables)
      │
      ├── 3. `check_permissions` (Authoritative PostgreSQL RBAC Guard)
      │        ├─► Missing permissions (e.g. Sales Manager querying salaries)
      │        │     └─► Blocked! Zero MCP/SQL access -> `generate_response` (HTTP 403)
      │        └─► Authorized -> proceed to Schema Discovery
      │
      ├── 4. `plan_schema` & `discover_schema` (MCP Tools: `list_tables`, `describe_table`)
      │        └─► Targeted column names, types, primary keys, and foreign keys
      │
      ├── 5. `generate_sql` (Qwen 2.5-Coder 7B generates read-only MySQL SELECT)
      │
      ├── 6. `validate_sql` (Phase 6 Security Validator checks single-statement, no DDL/DML)
      │        ├─► Invalid & retry_count < max_retries -> `correct_sql` self-correction
      │        └─► Valid -> proceed to MCP Execution
      │
      ├── 7. `execute_sql` (MCP Tool: `execute_read_only_sql`)
      │        ├─► Engine error & retry_count < max_retries -> `correct_sql`
      │        └─► Success -> `validate_result`
      │
      ├── 8. `validate_result` (Verifies column/row structure, empty result handling)
      │
      ├── 9. `analyze_results` (Llama 3.1 8B generates executive insights & trends)
      │
      └── 10. `generate_response` (Synthesizes direct answer, citations, visualization hint)
               └─► Structured JSON Response -> END
```

### Graph State Schema (`AnalyticsState`):
* `user_id`, `user_name`, `role`, `permissions`: Verified credentials from PostgreSQL auth.
* `original_question`, `conversation_history`: Natural language user question and conversational context.
* `intent`, `required_domains`, `required_tables`: Classified domain and candidate tables.
* `permission_granted`, `missing_permissions`: Authoritative RBAC gate decision.
* `schema_context`: Table metadata retrieved via MCP `describe_table`.
* `generated_sql`, `validated_sql`, `is_sql_valid`, `sql_error`: SQL generation and validation tracking.
* `query_result`, `result_valid`: Serialized database rows and column definitions from MCP.
* `retry_count`, `max_retries`: Self-correction loop budget (capped at 2 retries).
* `analysis`, `final_answer`, `sources`, `visualization_hint`: Executive answer, provenance citations, and chart hints.



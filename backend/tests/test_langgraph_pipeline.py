"""
Phase 7 Tests: LangGraph Multi-Agent Analytics Pipeline.
Validates:
1. Request validation node
2. Intent classification and domain planning
3. RBAC permission checks & unauthorized request blocking
4. MCP schema discovery integration
5. SQL generation & SQL security validation
6. MCP SQL execution & result validation
7. End-to-end analytical query execution (HR, Sales, Inventory, Cross-Domain, Root-Cause)
8. FastAPI /api/v1/analytics/query endpoint with JWT authentication
"""

import pytest
from app.agents.runner import run_analytics_query
from app.agents.nodes.request_validator import validate_request_node
from app.agents.nodes.intent_classifier import classify_intent_node
from app.agents.nodes.permission_checker import check_permissions_node
from app.agents.nodes.sql_validator_node import validate_sql_node
from app.agents.state import AnalyticsState

# ------------------------------------------------------------------------------
# 1. Request Validation Tests
# ------------------------------------------------------------------------------
def test_pipeline_request_validation_empty():
    """Verify empty query is rejected."""
    state: AnalyticsState = {"original_question": "   "}
    res = validate_request_node(state)
    assert res["is_valid_request"] is False
    assert "empty" in res["validation_error"].lower()

def test_pipeline_request_validation_too_short():
    """Verify overly brief query is rejected."""
    state: AnalyticsState = {"original_question": "hi"}
    res = validate_request_node(state)
    assert res["is_valid_request"] is False
    assert "too short" in res["validation_error"].lower()

def test_pipeline_request_validation_valid():
    """Verify valid query passes."""
    state: AnalyticsState = {"original_question": "Show monthly sales for the last 12 months."}
    res = validate_request_node(state)
    assert res["is_valid_request"] is True
    assert res["validation_error"] is None

# ------------------------------------------------------------------------------
# 2. Intent Classification Tests
# ------------------------------------------------------------------------------
def test_pipeline_intent_hr():
    """Verify HR query intent classification."""
    state: AnalyticsState = {"original_question": "How many employees are in each department?"}
    res = classify_intent_node(state)
    assert "HR" in res["required_domains"] or res["intent"].get("domain") == "HR"
    assert "departments" in res["required_tables"] or "employees" in res["required_tables"]

def test_pipeline_intent_sales():
    """Verify Sales query intent classification."""
    state: AnalyticsState = {"original_question": "Show monthly sales for the last 12 months."}
    res = classify_intent_node(state)
    assert "SALES" in res["required_domains"] or res["intent"].get("domain") == "SALES"
    assert "sales_orders" in res["required_tables"]

def test_pipeline_intent_cross_domain():
    """Verify Cross-domain query intent classification."""
    state: AnalyticsState = {"original_question": "Which products have high sales but low inventory?"}
    res = classify_intent_node(state)
    assert res["intent"].get("domain") == "CROSS_DOMAIN" or "SALES" in res["required_domains"]
    assert any(t in res["required_tables"] for t in ["products", "sales_order_items", "inventory"])

def test_pipeline_intent_root_cause():
    """Verify Root-cause query intent classification."""
    state: AnalyticsState = {"original_question": "Why did profit decrease in August?"}
    res = classify_intent_node(state)
    assert res["intent"].get("domain") in ["ROOT_CAUSE", "FINANCE"] or "ROOT_CAUSE" in res.get("required_domains", [])
    assert "company_financials" in res["required_tables"] or "expenses" in res["required_tables"]

# ------------------------------------------------------------------------------
# 3. RBAC Permission Checker Tests
# ------------------------------------------------------------------------------
def test_pipeline_rbac_sales_manager_blocked_from_salaries():
    """Verify Sales Manager cannot access salary records."""
    state: AnalyticsState = {
        "original_question": "Show employee salaries",
        "role": "SALES_MANAGER",
        "permissions": ["VIEW_CRM", "VIEW_SALES", "VIEW_INVENTORY"],
        "required_domains": ["HR", "SALARIES"],
        "required_tables": ["employees", "salaries"]
    }
    res = check_permissions_node(state)
    assert res["permission_granted"] is False
    assert "VIEW_EMPLOYEE_SALARY" in res["missing_permissions"]
    assert "Access Denied" in res["error"]

def test_pipeline_rbac_hr_manager_allowed_salaries():
    """Verify HR Manager is authorized to access salary records."""
    state: AnalyticsState = {
        "original_question": "Show employee salaries",
        "role": "HR_MANAGER",
        "permissions": ["VIEW_HR", "VIEW_EMPLOYEE_SALARY", "VIEW_EXPENSES"],
        "required_domains": ["HR", "SALARIES"],
        "required_tables": ["employees", "salaries"]
    }
    res = check_permissions_node(state)
    assert res["permission_granted"] is True
    assert res["missing_permissions"] == []

# ------------------------------------------------------------------------------
# 4. SQL Security Validator Node Tests
# ------------------------------------------------------------------------------
def test_pipeline_sql_validator_accepts_clean_select():
    """Verify valid SELECT query passes validation."""
    state: AnalyticsState = {"generated_sql": "SELECT dept_name, COUNT(employee_id) FROM departments JOIN employees ON dept_id=department_id GROUP BY dept_name;"}
    res = validate_sql_node(state)
    assert res["is_sql_valid"] is True
    assert res["validated_sql"] is not None

def test_pipeline_sql_validator_rejects_destructive_dml():
    """Verify destructive SQL is blocked by the pipeline."""
    for bad_sql in [
        "DELETE FROM employees WHERE employee_id = 'E001';",
        "UPDATE products SET unit_price = 0;",
        "DROP TABLE customers;",
        "SELECT * FROM employees; DROP TABLE employees;"
    ]:
        state: AnalyticsState = {"generated_sql": bad_sql}
        res = validate_sql_node(state)
        assert res["is_sql_valid"] is False
        assert res["sql_error"] is not None

# ------------------------------------------------------------------------------
# 5. End-to-End Analytics Pipeline Scenarios
# ------------------------------------------------------------------------------
def test_pipeline_e2e_hr_ceo():
    """Scenario 1: CEO asks how many employees are in each department."""
    res = run_analytics_query(
        question="How many employees are in each department?",
        user_id=2,
        user_name="Vikram Malhotra",
        role="CEO",
        permissions=["VIEW_HR", "VIEW_EMPLOYEE_SALARY", "VIEW_CRM", "VIEW_SALES", "VIEW_INVENTORY", "VIEW_PURCHASES", "VIEW_FINANCE", "VIEW_PROFIT", "VIEW_EXPENSES"]
    )
    assert res["success"] is True
    assert res["data"]["row_count"] == 10
    assert "departments" in res["sources"]
    assert "employees" in res["sources"]
    assert res["visualization_hint"] in ["bar_chart", "table"]

def test_pipeline_e2e_sales_manager_valid_sales():
    """Scenario 2: Sales Manager asks for monthly sales."""
    res = run_analytics_query(
        question="Show monthly sales for the last 12 months.",
        user_id=4,
        user_name="Arun Kumar",
        role="SALES_MANAGER",
        permissions=["VIEW_CRM", "VIEW_SALES", "VIEW_INVENTORY"]
    )
    assert res["success"] is True
    assert res["data"]["row_count"] > 0
    assert "sales_orders" in res["sources"]
    assert res["visualization_hint"] in ["line_chart", "bar_chart", "table"]

def test_pipeline_e2e_sales_manager_blocked_from_salaries():
    """Scenario 3: Sales Manager tries to query employee salaries -> blocked."""
    res = run_analytics_query(
        question="Show employee salaries",
        user_id=4,
        user_name="Arun Kumar",
        role="SALES_MANAGER",
        permissions=["VIEW_CRM", "VIEW_SALES", "VIEW_INVENTORY"]
    )
    assert res["success"] is False
    assert "Access Denied" in res["error"]
    assert res["data"]["row_count"] == 0
    assert res["sources"] == []

def test_pipeline_e2e_cross_domain_query():
    """Scenario 4: High sales but low inventory cross-domain query."""
    res = run_analytics_query(
        question="Which products have high sales but low inventory?",
        user_id=2,
        user_name="Vikram Malhotra",
        role="CEO",
        permissions=["VIEW_HR", "VIEW_EMPLOYEE_SALARY", "VIEW_CRM", "VIEW_SALES", "VIEW_INVENTORY", "VIEW_PURCHASES", "VIEW_FINANCE", "VIEW_PROFIT", "VIEW_EXPENSES"]
    )
    assert res["success"] is True
    assert res["data"]["row_count"] > 0
    assert "products" in res["sources"]
    assert any(c in ["units_sold", "quantity_on_hand", "product_name"] for c in res["data"]["columns"])

def test_pipeline_e2e_root_cause_august_profit_drop():
    """Scenario 5: Root-cause investigation on August profit decrease."""
    res = run_analytics_query(
        question="Why did profit decrease in August?",
        user_id=7,
        user_name="Rahul Kumar",
        role="FINANCE_MANAGER",
        permissions=["VIEW_FINANCE", "VIEW_PROFIT", "VIEW_EXPENSES", "VIEW_SALES"]
    )
    assert res["success"] is True
    assert res["data"]["row_count"] > 0
    assert "company_financials" in res["sources"] or "expenses" in res["sources"]
    # Check that August drop is reflected in answer or data
    assert any(k in res["answer"].lower() for k in ["august", "profit", "drop", "expense"])

# ------------------------------------------------------------------------------
# 6. FastAPI REST API Endpoint Tests (/api/v1/analytics/query)
# ------------------------------------------------------------------------------
def test_fastapi_analytics_endpoint_authorized(client):
    """Verify authorized CEO can query /api/v1/analytics/query with JWT."""
    login_resp = client.post("/api/v1/auth/login", data={"username": "ceo", "password": "CeoPassword123!"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    payload = {"question": "How many employees are in each department?"}
    response = client.post("/api/v1/analytics/query", json=payload, headers=headers)
    assert response.status_code == 200, f"Endpoint failed: {response.text}"

    data = response.json()
    assert data["success"] is True
    assert data["user_role"] == "CEO"
    assert data["data"]["row_count"] == 10
    assert len(data["sources"]) >= 2

def test_fastapi_analytics_endpoint_unauthorized_blocked(client):
    """Verify unauthorized Sales Manager querying salaries gets 403 Forbidden."""
    login_resp = client.post("/api/v1/auth/login", data={"username": "sales.manager", "password": "SalesPassword123!"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    payload = {"question": "Show employee salaries"}
    response = client.post("/api/v1/analytics/query", json=payload, headers=headers)
    assert response.status_code == 403, f"Expected 403 Forbidden, got {response.status_code}"
    assert "Access Denied" in response.json()["detail"]

def test_fastapi_analytics_endpoint_unauthenticated(client):
    """Verify request without JWT token gets 401 Unauthorized."""
    payload = {"question": "Show monthly sales for the last 12 months."}
    response = client.post("/api/v1/analytics/query", json=payload)
    assert response.status_code == 401

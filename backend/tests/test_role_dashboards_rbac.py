"""
Automated Pytest Suite for Role-Specific Dashboards & Server-Side RBAC Enforcement.
Tests authentication, role authorization, and negative permission boundary rejection.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def login_and_get_token(username: str, password: str) -> str:
    """Helper to authenticate against PostgreSQL and retrieve JWT access token."""
    res = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert res.status_code == 200, f"Login failed for {username}: {res.text}"
    return res.json()["access_token"]


# =============================================================================
# 1. Unauthenticated & Invalid Token Security Tests
# =============================================================================

def test_role_dashboard_unauthenticated_rejected():
    """Unauthenticated requests to any role dashboard must return HTTP 401."""
    roles = ["ceo", "sales", "hr", "finance", "inventory", "erp"]
    for r in roles:
        res = client.get(f"/api/v1/analytics/dashboard/{r}")
        assert res.status_code == 401, f"Expected 401 for unauthenticated {r}, got {res.status_code}"


def test_role_dashboard_invalid_token_rejected():
    """Invalid or forged JWT tokens must be rejected with HTTP 401."""
    headers = {"Authorization": "Bearer invalid.fake.token"}
    res = client.get("/api/v1/analytics/dashboard/ceo", headers=headers)
    assert res.status_code == 401


# =============================================================================
# 2. CEO Authorization Tests (Full Enterprise Scope)
# =============================================================================

def test_ceo_authorized_for_all_dashboards():
    """CEO persona possesses full company-wide visibility across all role dashboards."""
    ceo_token = login_and_get_token("ceo", "CeoPassword123!")
    headers = {"Authorization": f"Bearer {ceo_token}"}

    roles = ["ceo", "sales", "hr", "finance", "inventory", "erp"]
    for r in roles:
        res = client.get(f"/api/v1/analytics/dashboard/{r}", headers=headers)
        assert res.status_code == 200, f"CEO should access {r}, got {res.status_code}"
        data = res.json()
        assert len(data.get("kpis", [])) == 4
        assert "insights" in data


# =============================================================================
# 3. Sales Manager Authorization & Negative Boundary Tests
# =============================================================================

def test_sales_manager_authorized_sales():
    """Sales Manager must successfully access /dashboard/sales with real sales & customer metrics."""
    sales_token = login_and_get_token("sales.manager", "SalesPassword123!")
    headers = {"Authorization": f"Bearer {sales_token}"}

    res = client.get("/api/v1/analytics/dashboard/sales", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "SALES_MANAGER"
    assert "top_customers" in data
    assert len(data["top_customers"]) > 0
    # Must NOT expose employee salary data
    assert data.get("department_summary") is None


def test_sales_manager_blocked_from_hr_dashboard():
    """Sales Manager attempting to access /dashboard/hr must receive HTTP 403 Forbidden."""
    sales_token = login_and_get_token("sales.manager", "SalesPassword123!")
    headers = {"Authorization": f"Bearer {sales_token}"}

    res = client.get("/api/v1/analytics/dashboard/hr", headers=headers)
    assert res.status_code == 403
    assert "Access Denied" in res.json()["detail"]


def test_sales_manager_blocked_from_finance_dashboard():
    """Sales Manager attempting to access /dashboard/finance must receive HTTP 403 Forbidden."""
    sales_token = login_and_get_token("sales.manager", "SalesPassword123!")
    headers = {"Authorization": f"Bearer {sales_token}"}

    res = client.get("/api/v1/analytics/dashboard/finance", headers=headers)
    assert res.status_code == 403
    assert "VIEW_FINANCE" in res.json()["detail"]


# =============================================================================
# 4. HR Manager Authorization & Negative Boundary Tests
# =============================================================================

def test_hr_manager_authorized_hr():
    """HR Manager must successfully access /dashboard/hr with departmental salary & headcount metrics."""
    hr_token = login_and_get_token("hr.manager", "HrPassword123!")
    headers = {"Authorization": f"Bearer {hr_token}"}

    res = client.get("/api/v1/analytics/dashboard/hr", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "HR_MANAGER"
    assert "department_summary" in data
    assert len(data["department_summary"]) == 10
    # Department summary contains verified payroll & average salary
    assert data["department_summary"][0]["avg_salary"] > 0


def test_hr_manager_blocked_from_sales_dashboard():
    """HR Manager attempting to access /dashboard/sales must receive HTTP 403 Forbidden."""
    hr_token = login_and_get_token("hr.manager", "HrPassword123!")
    headers = {"Authorization": f"Bearer {hr_token}"}

    res = client.get("/api/v1/analytics/dashboard/sales", headers=headers)
    assert res.status_code == 403
    assert "VIEW_SALES" in res.json()["detail"]


# =============================================================================
# 5. Finance Manager Authorization & Root-Cause Highlight Tests
# =============================================================================

def test_finance_manager_authorized_finance():
    """Finance Manager must successfully access /dashboard/finance with P&L trends and root cause."""
    fin_token = login_and_get_token("finance.manager", "FinancePassword123!")
    headers = {"Authorization": f"Bearer {fin_token}"}

    res = client.get("/api/v1/analytics/dashboard/finance", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "FINANCE_MANAGER"
    assert "financial_trend" in data
    assert len(data["financial_trend"]) > 0
    # Must contain the August 2026 profit contraction root-cause highlight
    assert data.get("root_cause_highlight") is not None
    rc = data["root_cause_highlight"]
    assert rc["change_pct"] == -50.0
    assert "freight" in rc["primary_driver"].lower()


def test_finance_manager_blocked_from_hr_dashboard():
    """Finance Manager attempting to access /dashboard/hr must receive HTTP 403 Forbidden."""
    fin_token = login_and_get_token("finance.manager", "FinancePassword123!")
    headers = {"Authorization": f"Bearer {fin_token}"}

    res = client.get("/api/v1/analytics/dashboard/hr", headers=headers)
    assert res.status_code == 403


# =============================================================================
# 6. Inventory & ERP Manager Authorization Tests
# =============================================================================

def test_inventory_manager_authorized_inventory():
    """Inventory Manager must successfully access /dashboard/inventory with stock & reorder alerts."""
    inv_token = login_and_get_token("inventory.manager", "InventoryPassword123!")
    headers = {"Authorization": f"Bearer {inv_token}"}

    res = client.get("/api/v1/analytics/dashboard/inventory", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "INVENTORY_MANAGER"
    assert "low_stock_items" in data
    assert len(data["low_stock_items"]) > 0


def test_inventory_manager_blocked_from_salary_dashboard():
    """Inventory Manager attempting to access /dashboard/hr must receive HTTP 403 Forbidden."""
    inv_token = login_and_get_token("inventory.manager", "InventoryPassword123!")
    headers = {"Authorization": f"Bearer {inv_token}"}

    res = client.get("/api/v1/analytics/dashboard/hr", headers=headers)
    assert res.status_code == 403


def test_erp_manager_authorized_erp():
    """ERP Manager must successfully access /dashboard/erp with procurement PO spend."""
    erp_token = login_and_get_token("erp.manager", "ErpPassword123!")
    headers = {"Authorization": f"Bearer {erp_token}"}

    res = client.get("/api/v1/analytics/dashboard/erp", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "ERP_MANAGER"
    assert "top_suppliers" in data

"""
Tests for PostgreSQL Authentication, JWT, and Role-Based Access Control (RBAC).
"""
import pytest
from app.models.auth_models import User, Role, Permission
from app.core.security import verify_password

def test_rbac_roles_and_permissions_count(postgres_db):
    """Verify 7 application roles and 11 granular permissions exist."""
    role_count = postgres_db.query(Role).count()
    perm_count = postgres_db.query(Permission).count()
    user_count = postgres_db.query(User).count()

    assert role_count == 7, f"Expected 7 roles, found {role_count}"
    assert perm_count == 11, f"Expected 11 permissions, found {perm_count}"
    assert user_count >= 7, f"Expected at least 7 application users, found {user_count}"

def test_application_user_employee_mappings(postgres_db):
    """Verify that manager accounts in PostgreSQL map to employee IDs in MySQL."""
    expected_mappings = {
        "ceo": "E006",
        "sales.manager": "E001",
        "hr.manager": "E002",
        "finance.manager": "E003",
        "inventory.manager": "E005",
        "erp.manager": "E007",
    }
    for username, expected_emp_id in expected_mappings.items():
        user = postgres_db.query(User).filter(User.username == username).first()
        assert user is not None, f"User '{username}' not found in PostgreSQL"
        assert user.employee_id == expected_emp_id, (
            f"User '{username}' mapped to '{user.employee_id}', expected '{expected_emp_id}'"
        )

def test_admin_account_has_no_workforce_employee(postgres_db):
    """Verify that technical system admin is decoupled from workforce records."""
    admin = postgres_db.query(User).filter(User.username == "admin").first()
    assert admin is not None
    assert admin.employee_id is None, "Technical Admin should not have a workforce employee_id"
    assert admin.role.role_name == "ADMIN"

def test_auth_login_success(client):
    """Verify login with correct credentials returns valid JWT."""
    response = client.post("/api/v1/auth/login", data={"username": "sales.manager", "password": "SalesPassword123!"})
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "SALES_MANAGER"


def test_auth_login_invalid_password(client):
    """Verify login with wrong password returns 401 Unauthorized."""
    response = client.post("/api/v1/auth/login", data={"username": "sales.manager", "password": "WrongPassword!"})
    assert response.status_code == 401

def test_auth_me_endpoint(client):
    """Verify /auth/me returns authenticated user's profile and permissions."""
    login_resp = client.post("/api/v1/auth/login", data={"username": "hr.manager", "password": "HrPassword123!"})
    token = login_resp.json()["access_token"]

    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    data = me_resp.json()
    assert data["username"] == "hr.manager"
    assert data["role"] == "HR_MANAGER"
    assert "VIEW_HR" in data["permissions"]
    assert "VIEW_EMPLOYEE_SALARY" in data["permissions"]

def test_rbac_admin_guard_enforcement(client):
    """
    Verify backend RBAC guard:
    - Admin (MANAGE_USERS) -> GET /api/v1/admin/users returns 200 OK
    - Sales Manager (VIEW_SALES, VIEW_CRM) -> GET /api/v1/admin/users returns 403 Forbidden
    """
    # 1. Admin login and access
    admin_login = client.post("/api/v1/auth/login", data={"username": "admin", "password": "AdminPassword123!"})
    admin_token = admin_login.json()["access_token"]
    admin_access = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_access.status_code == 200, f"Admin should have access: {admin_access.text}"

    # 2. Sales Manager login and blocked access
    sales_login = client.post("/api/v1/auth/login", data={"username": "sales.manager", "password": "SalesPassword123!"})
    sales_token = sales_login.json()["access_token"]
    sales_access = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {sales_token}"})
    assert sales_access.status_code == 403, "Sales Manager should be rejected with 403 Forbidden"

"""
Automated Pytest Suite for CEO User & Role Management and RBAC Protection.
Verifies:
- Only CEO can access employee directory & provisioning status.
- Only CEO can provision login accounts for existing MySQL employees.
- Non-existent employees, duplicate accounts, and duplicate usernames are rejected.
- Managers (SALES_MANAGER, HR_MANAGER, FINANCE_MANAGER, etc.) receive HTTP 403 Forbidden.
- Newly provisioned user can log in and reach their role-specific dashboard.
- Newly provisioned user is blocked from unauthorized dashboards.
- CEO can reassign application roles and disable/enable accounts.
- Users cannot modify their own role or disable their own account.
- Disabled accounts are blocked at login.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.postgres_session import PostgresSessionLocal
from app.models.auth_models import User

client = TestClient(app)

@pytest.fixture(scope="module")
def ceo_token():
    resp = client.post("/api/v1/auth/login", data={"username": "ceo", "password": "CeoPassword123!"})
    assert resp.status_code == 200, f"CEO login failed: {resp.text}"
    return resp.json()["access_token"]

@pytest.fixture(scope="module")
def sales_manager_token():
    resp = client.post("/api/v1/auth/login", data={"username": "sales.manager", "password": "SalesPassword123!"})
    assert resp.status_code == 200, f"Sales Manager login failed: {resp.text}"
    return resp.json()["access_token"]

@pytest.fixture(scope="module")
def hr_manager_token():
    resp = client.post("/api/v1/auth/login", data={"username": "hr.manager", "password": "HrPassword123!"})
    assert resp.status_code == 200, f"HR Manager login failed: {resp.text}"
    return resp.json()["access_token"]

@pytest.fixture(scope="module")
def finance_manager_token():
    resp = client.post("/api/v1/auth/login", data={"username": "finance.manager", "password": "FinancePassword123!"})
    assert resp.status_code == 200, f"Finance Manager login failed: {resp.text}"
    return resp.json()["access_token"]


# Cleanup helper to ensure clean test state
def cleanup_user(username: str):
    db = PostgresSessionLocal()
    u = db.query(User).filter(User.username == username).first()
    if u:
        db.delete(u)
        db.commit()
    db.close()


def test_ceo_can_view_directory(ceo_token):
    """CEO can view correlated MySQL employees and application accounts."""
    resp = client.get("/api/v1/admin/directory", headers={"Authorization": f"Bearer {ceo_token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 500
    
    # E001 (Arun Kumar) should have account
    e001 = next((e for e in data if e["employee_id"] == "E001"), None)
    assert e001 is not None
    assert e001["has_account"] is True
    assert e001["role_name"] == "SALES_MANAGER"

    # E008 (Rohan Mehta) initially has no account
    e008 = next((e for e in data if e["employee_id"] == "E008"), None)
    assert e008 is not None


def test_managers_cannot_view_directory(sales_manager_token, hr_manager_token, finance_manager_token):
    """Non-CEO managers must receive 403 Forbidden when accessing directory."""
    for token in [sales_manager_token, hr_manager_token, finance_manager_token]:
        resp = client.get("/api/v1/admin/directory", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403
        assert "Access Denied" in resp.json()["detail"]


def test_unauthenticated_directory_blocked():
    """Unauthenticated requests must receive 401 Unauthorized."""
    resp = client.get("/api/v1/admin/directory")
    assert resp.status_code == 401


def test_ceo_can_provision_account_flow(ceo_token):
    """Test full provisioning lifecycle: creation, login, dashboard access, role update, disable, reactivate."""
    test_uname = "rohan.mehta.prov"
    cleanup_user(test_uname)

    try:
        # 1. CEO provisions account for E008
        payload = {
            "employee_id": "E008",
            "username": test_uname,
            "password": "RohanPassword123!",
            "role_name": "SALES_MANAGER"
        }
        res_prov = client.post("/api/v1/admin/provision", json=payload, headers={"Authorization": f"Bearer {ceo_token}"})
        assert res_prov.status_code == 201, f"Provisioning failed: {res_prov.text}"
        user_info = res_prov.json()
        assert user_info["username"] == test_uname
        assert user_info["role_name"] == "SALES_MANAGER"
        assert user_info["employee_id"] == "E008"
        target_uid = user_info["user_id"]

        # 2. Duplicate provisioning for same employee must fail (HTTP 400)
        res_dup_emp = client.post("/api/v1/admin/provision", json=payload, headers={"Authorization": f"Bearer {ceo_token}"})
        assert res_dup_emp.status_code == 400
        assert "already has an application account" in res_dup_emp.json()["detail"]

        # 3. Duplicate username must fail (HTTP 400)
        res_dup_user = client.post("/api/v1/admin/provision", json={
            "employee_id": "E009",
            "username": test_uname,
            "password": "Password123!",
            "role_name": "SALES_MANAGER"
        }, headers={"Authorization": f"Bearer {ceo_token}"})
        assert res_dup_user.status_code == 400
        assert "already taken" in res_dup_user.json()["detail"]

        # 4. Provisioning for non-existent employee must fail (HTTP 404)
        res_fake_emp = client.post("/api/v1/admin/provision", json={
            "employee_id": "E9999",
            "username": "fake.user",
            "password": "Password123!",
            "role_name": "SALES_MANAGER"
        }, headers={"Authorization": f"Bearer {ceo_token}"})
        assert res_fake_emp.status_code == 404

        # 5. Newly provisioned user logs in
        login_res = client.post("/api/v1/auth/login", data={"username": test_uname, "password": "RohanPassword123!"})
        assert login_res.status_code == 200
        rohan_token = login_res.json()["access_token"]
        assert login_res.json()["user"]["role"] == "SALES_MANAGER"

        # 6. Newly provisioned user can access /dashboard/sales
        dash_res = client.get("/api/v1/analytics/dashboard/sales", headers={"Authorization": f"Bearer {rohan_token}"})
        assert dash_res.status_code == 200

        # 7. Newly provisioned user blocked from /dashboard/hr (403)
        hr_block = client.get("/api/v1/analytics/dashboard/hr", headers={"Authorization": f"Bearer {rohan_token}"})
        assert hr_block.status_code == 403

        # 8. Newly provisioned user cannot access /admin/directory (403)
        admin_block = client.get("/api/v1/admin/directory", headers={"Authorization": f"Bearer {rohan_token}"})
        assert admin_block.status_code == 403

        # 9. CEO changes user's role to ERP_MANAGER
        role_res = client.patch(f"/api/v1/admin/users/{target_uid}/role", json={"role_name": "ERP_MANAGER"}, headers={"Authorization": f"Bearer {ceo_token}"})
        assert role_res.status_code == 200
        assert role_res.json()["role_name"] == "ERP_MANAGER"

        # 10. User logs in again to refresh role
        login_res2 = client.post("/api/v1/auth/login", data={"username": test_uname, "password": "RohanPassword123!"})
        assert login_res2.status_code == 200
        erp_token = login_res2.json()["access_token"]
        assert login_res2.json()["user"]["role"] == "ERP_MANAGER"

        # 11. Can now access ERP dashboard, but blocked from Finance
        erp_dash = client.get("/api/v1/analytics/dashboard/erp", headers={"Authorization": f"Bearer {erp_token}"})
        assert erp_dash.status_code == 200

        fin_block = client.get("/api/v1/analytics/dashboard/finance", headers={"Authorization": f"Bearer {erp_token}"})
        assert fin_block.status_code == 403

        # 12. CEO disables the account
        dis_res = client.patch(f"/api/v1/admin/users/{target_uid}/status", json={"is_active": False}, headers={"Authorization": f"Bearer {ceo_token}"})
        assert dis_res.status_code == 200
        assert dis_res.json()["is_active"] is False

        # 13. Disabled user cannot log in (403)
        dis_login = client.post("/api/v1/auth/login", data={"username": test_uname, "password": "RohanPassword123!"})
        assert dis_login.status_code == 403

        # 14. CEO reactivates the account
        react_res = client.patch(f"/api/v1/admin/users/{target_uid}/status", json={"is_active": True}, headers={"Authorization": f"Bearer {ceo_token}"})
        assert react_res.status_code == 200
        assert react_res.json()["is_active"] is True

        # 15. User can log in again
        relogin_res = client.post("/api/v1/auth/login", data={"username": test_uname, "password": "RohanPassword123!"})
        assert relogin_res.status_code == 200

    finally:
        cleanup_user(test_uname)


def test_self_role_modification_blocked(ceo_token):
    """CEO cannot modify their own role (HTTP 400)."""
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {ceo_token}"})
    ceo_uid = me_resp.json()["user_id"]
    resp = client.patch(f"/api/v1/admin/users/{ceo_uid}/role", json={"role_name": "SALES_MANAGER"}, headers={"Authorization": f"Bearer {ceo_token}"})
    assert resp.status_code == 400
    assert "Security Violation" in resp.json()["detail"]


def test_self_account_disable_blocked(ceo_token):
    """CEO cannot disable their own account (HTTP 400)."""
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {ceo_token}"})
    ceo_uid = me_resp.json()["user_id"]
    resp = client.patch(f"/api/v1/admin/users/{ceo_uid}/status", json={"is_active": False}, headers={"Authorization": f"Bearer {ceo_token}"})
    assert resp.status_code == 400
    assert "Security Violation" in resp.json()["detail"]


def test_managers_cannot_provision(sales_manager_token):
    """Sales Manager attempting to provision another user gets 403 Forbidden."""
    resp = client.post("/api/v1/admin/provision", json={
        "employee_id": "E010",
        "username": "suresh.sales",
        "password": "Password123!",
        "role_name": "SALES_MANAGER"
    }, headers={"Authorization": f"Bearer {sales_manager_token}"})
    assert resp.status_code == 403
    assert "Access Denied" in resp.json()["detail"]

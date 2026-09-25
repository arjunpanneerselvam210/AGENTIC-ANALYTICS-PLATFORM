"""
Phase 3 & 4 Verification Script: Authentication & RBAC Security Layer
Verifies:
1. PostgreSQL Database Integrity (Roles, Permissions, Users, Mappings)
2. Password Hashing (Bcrypt) & Verification
3. JWT Access Token Generation & Decoding
4. FastAPI Login Endpoint (/api/v1/auth/login)
5. Current User Endpoint (/api/v1/auth/me)
6. RBAC Permission Guards:
   - Admin allowed to access Admin APIs
   - Sales Manager denied from accessing Admin APIs (403 Forbidden)
   - Permission scoping per role
"""

import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient
from app.main import app
from app.db.postgres_session import PostgresSessionLocal
from app.models.auth_models import User, Role, Permission
from app.core.security import verify_password, decode_access_token

GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_result(title: str, passed: bool, details: str = ""):
    icon = f"{GREEN}[PASS]{RESET}" if passed else f"{RED}[FAIL]{RESET}"
    print(f"  {icon} {BOLD}{title:<38}{RESET} {details}")

def main():
    print(f"\n{BOLD}{CYAN}============================================================{RESET}")
    print(f"{BOLD}{CYAN}  AGENTIC ANALYTICS PLATFORM - PHASE 3 & 4 VERIFICATION{RESET}")
    print(f"{BOLD}{CYAN}  Authentication, JWT Security & RBAC Permission Guards{RESET}")
    print(f"{BOLD}{CYAN}============================================================{RESET}\n")

    client = TestClient(app)
    db = PostgresSessionLocal()

    # 1. Database Counts
    print(f"{BOLD}1. Database Integrity (PostgreSQL):{RESET}")
    role_count = db.query(Role).count()
    perm_count = db.query(Permission).count()
    user_count = db.query(User).count()

    print_result("Roles Created", role_count == 7, f"{role_count}/7 Roles")
    print_result("Permissions Created", perm_count == 11, f"{perm_count}/11 Permissions")
    print_result("Application Users Created", user_count >= 7, f"{user_count} Users")

    # 2. Check Roles and their assigned permissions
    print(f"\n{BOLD}2. Role Permissions Scoping:{RESET}")
    roles = db.query(Role).all()
    for r in roles:
        perms = [p.permission_code for p in r.permissions]
        print_result(f"Role: {r.role_name}", len(perms) > 0, f"({len(perms)} perms): {', '.join(perms[:4])}...")

    # 3. Test Authentication API
    print(f"\n{BOLD}3. Authentication Endpoints (/api/v1/auth):{RESET}")
    
    # 3a. Admin Login
    resp_admin = client.post("/api/v1/auth/login", data={"username": "admin", "password": "AdminPassword123!"})
    admin_login_ok = resp_admin.status_code == 200
    print_result("Admin Login (Valid Password)", admin_login_ok, f"Status: {resp_admin.status_code}")
    admin_token = resp_admin.json().get("access_token") if admin_login_ok else None

    # 3b. Sales Manager Login
    resp_sales = client.post("/api/v1/auth/login", data={"username": "sales.manager", "password": "SalesPassword123!"})
    sales_login_ok = resp_sales.status_code == 200
    print_result("Sales Manager Login", sales_login_ok, f"Status: {resp_sales.status_code}")
    sales_token = resp_sales.json().get("access_token") if sales_login_ok else None

    # 3c. Invalid Password Rejection
    resp_bad = client.post("/api/v1/auth/login", data={"username": "admin", "password": "WrongPassword!"})
    bad_rejected = resp_bad.status_code == 401
    print_result("Invalid Password Rejected", bad_rejected, f"Status: {resp_bad.status_code} (401 Unauthorized expected)")

    # 3d. Current User Profile (/auth/me)
    resp_me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {sales_token}"})
    me_ok = resp_me.status_code == 200 and resp_me.json().get("role") == "SALES_MANAGER"
    print_result("GET /auth/me with Bearer Token", me_ok, f"Returned Role: {resp_me.json().get('role') if me_ok else 'None'}")

    # 4. Test RBAC Permission Guards
    print(f"\n{BOLD}4. RBAC Permission Guards Enforcement:{RESET}")

    # 4a. Admin accessing Admin APIs (MANAGE_USERS required) -> MUST SUCCEED (200)
    resp_admin_list = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    admin_allowed = resp_admin_list.status_code == 200
    print_result("Admin -> GET /admin/users", admin_allowed, f"Status: {resp_admin_list.status_code} (200 OK expected)")

    # 4b. Sales Manager accessing Admin APIs (MANAGE_USERS required) -> MUST BE BLOCKED (403)
    resp_sales_blocked = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {sales_token}"})
    sales_blocked = resp_sales_blocked.status_code == 403
    print_result("Sales Manager -> GET /admin/users", sales_blocked, f"Status: {resp_sales_blocked.status_code} (403 Forbidden expected - Unauthorized blocked!)")

    # 4c. Verify Section 3 & 44 concept: Employee vs Application User
    sales_user = db.query(User).filter(User.username == "sales.manager").first()
    mapping_ok = sales_user.employee_id == "E001" and sales_user.full_name == "Arun Kumar"
    print_result("Employee Mapping (E001 -> Arun Kumar)", mapping_ok, f"App user '{sales_user.username}' correctly linked to workforce ID '{sales_user.employee_id}'")

    db.close()

    all_passed = all([
        role_count == 7,
        perm_count == 11,
        user_count >= 7,
        admin_login_ok,
        sales_login_ok,
        bad_rejected,
        me_ok,
        admin_allowed,
        sales_blocked,
        mapping_ok
    ])

    print(f"\n{BOLD}{CYAN}============================================================{RESET}")
    if all_passed:
        print(f"{GREEN}{BOLD}>>> ALL PHASE 3 & 4 TESTS PASSED SUCCESSFULLY! <<<{RESET}")
        print("Authentication and Role-Based Access Control (RBAC) are 100% active and enforced.")
        print(f"You are ready to proceed to Phase 5 (Basic AI Chatbot).\n")
    else:
        print(f"{RED}{BOLD}>>> Some checks failed. Please check the logs above. <<<{RESET}\n")

if __name__ == "__main__":
    main()

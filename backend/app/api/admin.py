"""
Administrative User & Role Management Router for FreshMart.
Strictly restricted to CEO (and system ADMIN).

Enforces:
- Only CEO can view employee directory and application provisioning status.
- Only CEO can provision new application accounts for existing MySQL employees.
- Only CEO can assign and change application roles.
- Only CEO can activate or disable application accounts.
- Managers (SALES_MANAGER, HR_MANAGER, FINANCE_MANAGER, INVENTORY_MANAGER, ERP_MANAGER)
  are strictly blocked with HTTP 403 Forbidden.
- A user cannot modify their own role or disable their own account.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.postgres_session import get_postgres_db
from app.models.auth_models import User, Role
from app.core.security import get_current_user, get_password_hash
from app.schemas.auth_schemas import (
    UserResponse,
    UserCreate,
    RoleResponse,
    UserStatusUpdate,
    UserRoleUpdate,
    EmployeeDirectoryItem,
    ProvisionAccountRequest
)
from app.schemas.common_schemas import HTTPError
from mcp_server.database import MCPDatabaseManager
import pymysql
import logging
from app.core.config import settings

logger = logging.getLogger("admin")

ROLE_TO_JOB_TITLE = {
    "CEO": "Chief Executive Officer",
    "SALES_MANAGER": "Sales Manager",
    "FINANCE_MANAGER": "Finance Manager",
    "HR_MANAGER": "HR Manager",
    "INVENTORY_MANAGER": "Inventory & Warehouse Manager",
    "ERP_MANAGER": "ERP Operations Manager",
    "ADMIN": "System Administrator",
}

router = APIRouter(prefix="/admin")

# ------------------------------------------------------------------------------
# CEO Authorization Dependency
# ------------------------------------------------------------------------------

def require_ceo(current_user: User = Depends(get_current_user)) -> User:
    """
    Enforces that only the CEO (or system ADMIN) can manage application users and roles.
    All manager roles (SALES_MANAGER, HR_MANAGER, FINANCE_MANAGER, INVENTORY_MANAGER, ERP_MANAGER)
    are strictly rejected with HTTP 403 Forbidden.
    """
    if current_user.role.role_name not in ["CEO", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Only CEO is authorized to manage user accounts and assign roles."
        )
    return current_user


# ------------------------------------------------------------------------------
# Employee Directory & Provisioning Status (CEO Only)
# ------------------------------------------------------------------------------

@router.get(
    "/directory",
    response_model=List[EmployeeDirectoryItem],
    tags=["User & Role Management"],
    summary="List Workforce Employees with Application Provisioning Status",
    description=(
        "Retrieves all existing FreshMart employees from the MySQL business database correlated with "
        "their PostgreSQL application login account status.\n\n"
        "**Authorization:** Restricted strictly to `CEO` (and `ADMIN`)."
    ),
    operation_id="listEmployeesProvisioningDirectory",
    responses={
        200: {"model": List[EmployeeDirectoryItem], "description": "Employee directory successfully retrieved."},
        401: {"model": HTTPError, "description": "Unauthorized: Missing, invalid, or expired JWT token."},
        403: {"model": HTTPError, "description": "Forbidden: Non-CEO manager roles are strictly prohibited."}
    }
)
def get_employees_directory(
    db: Session = Depends(get_postgres_db),
    _: User = Depends(require_ceo)
):
    """Correlate MySQL workforce employees with PostgreSQL application accounts."""
    # 1. Fetch all employees from MySQL via MCP database manager
    mcp = MCPDatabaseManager()
    sql = """
        SELECT 
            e.employee_id,
            e.first_name,
            e.last_name,
            e.email,
            d.dept_name AS department,
            e.job_title,
            e.status AS employee_status
        FROM employees e
        JOIN departments d ON e.department_id = d.dept_id
        ORDER BY e.employee_id ASC;
    """
    res = mcp.execute_read_only_query(sql, limit=1000)
    mysql_rows = res.get("rows", [])

    # 2. Fetch all PostgreSQL users
    pg_users = db.query(User).all()
    user_by_emp_id = {u.employee_id: u for u in pg_users if u.employee_id}
    user_by_email = {u.email.lower(): u for u in pg_users if u.email}

    # 3. Correlate and format directory items
    items = []
    for emp in mysql_rows:
        emp_id = emp["employee_id"]
        pg_user = user_by_emp_id.get(emp_id) or user_by_email.get(emp["email"].lower())

        has_account = pg_user is not None
        user_id = pg_user.user_id if pg_user else None
        username = pg_user.username if pg_user else None
        role_id = pg_user.role_id if pg_user else None
        role_name = pg_user.role.role_name if pg_user and pg_user.role else None
        is_active = pg_user.is_active if pg_user else None

        items.append(EmployeeDirectoryItem(
            employee_id=emp_id,
            first_name=emp["first_name"],
            last_name=emp["last_name"],
            full_name=f"{emp['first_name']} {emp['last_name']}",
            email=emp["email"],
            department=emp["department"],
            job_title=emp["job_title"],
            employee_status=emp["employee_status"],
            has_account=has_account,
            user_id=user_id,
            username=username,
            role_id=role_id,
            role_name=role_name,
            is_active=is_active
        ))

    return items


# ------------------------------------------------------------------------------
# Provision Application Account for Existing Employee (CEO Only)
# ------------------------------------------------------------------------------

@router.post(
    "/provision",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["User & Role Management"],
    summary="Provision Application Login for Existing MySQL Employee",
    description=(
        "Provisions a new PostgreSQL application login account for an employee that already exists in MySQL.\n"
        "Validates that:\n"
        "- The employee exists in MySQL.\n"
        "- The employee does not already possess an application account.\n"
        "- The username is unique in PostgreSQL.\n"
        "- The requested role exists.\n"
        "- Password is cryptographically hashed with bcrypt.\n\n"
        "**Authorization:** Restricted strictly to `CEO` (and `ADMIN`)."
    ),
    operation_id="provisionEmployeeLoginAccount",
    responses={
        201: {"model": UserResponse, "description": "Application account provisioned successfully."},
        400: {"model": HTTPError, "description": "Bad Request: Employee already has an account or username is taken."},
        401: {"model": HTTPError, "description": "Unauthorized: Missing, invalid, or expired JWT token."},
        403: {"model": HTTPError, "description": "Forbidden: Non-CEO manager roles are strictly prohibited."},
        404: {"model": HTTPError, "description": "Not Found: Employee or Role does not exist."}
    }
)
def provision_account(
    req: ProvisionAccountRequest,
    db: Session = Depends(get_postgres_db),
    _: User = Depends(require_ceo)
):
    """CEO provisions a new application account for an existing employee."""
    # 1. Verify employee exists in MySQL
    mcp = MCPDatabaseManager()
    sanitized_emp_id = req.employee_id.strip().replace("'", "").replace(";", "")
    emp_res = mcp.execute_read_only_query(
        f"SELECT employee_id, first_name, last_name, email, status FROM employees WHERE employee_id = '{sanitized_emp_id}';",
        limit=1
    )
    emp_rows = emp_res.get("rows", [])
    if not emp_rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{req.employee_id}' was not found in MySQL workforce records."
        )
    emp_data = emp_rows[0]

    # 2. Verify employee does not already have an account
    existing_emp = db.query(User).filter(User.employee_id == req.employee_id).first()
    if existing_emp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee '{req.employee_id}' ({existing_emp.full_name}) already has an application account ('{existing_emp.username}')."
        )

    # 3. Verify username is unique
    existing_user = db.query(User).filter(User.username == req.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{req.username}' is already taken in the application database."
        )

    # 4. Verify role exists
    role = db.query(Role).filter(Role.role_name == req.role_name.strip()).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{req.role_name}' does not exist in the system roles catalog."
        )

    # 5. Hash password with bcrypt and insert into PostgreSQL
    pwd_hash = get_password_hash(req.password)
    new_user = User(
        username=req.username.strip(),
        email=emp_data["email"],
        password_hash=pwd_hash,
        full_name=f"{emp_data['first_name']} {emp_data['last_name']}",
        role_id=role.role_id,
        employee_id=emp_data["employee_id"],
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        user_id=new_user.user_id,
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        role_id=new_user.role_id,
        role_name=new_user.role.role_name,
        employee_id=new_user.employee_id,
        is_active=new_user.is_active,
        permissions=new_user.permission_codes,
        created_at=new_user.created_at
    )


# ------------------------------------------------------------------------------
# User Account Listing & Standard Creation (CEO Only)
# ------------------------------------------------------------------------------

@router.get(
    "/users",
    response_model=List[UserResponse],
    tags=["User & Role Management"],
    summary="List All Registered Application Users",
    description="Retrieves a complete list of all FreshMart application user accounts.\n\n**Authorization:** Restricted strictly to `CEO` (and `ADMIN`).",
    operation_id="listAllApplicationUsers"
)
def list_users(
    db: Session = Depends(get_postgres_db),
    _: User = Depends(require_ceo)
):
    """List all application users."""
    users = db.query(User).all()
    result = []
    for u in users:
        result.append(UserResponse(
            user_id=u.user_id,
            username=u.username,
            email=u.email,
            full_name=u.full_name,
            role_id=u.role_id,
            role_name=u.role.role_name,
            employee_id=u.employee_id,
            is_active=u.is_active,
            permissions=u.permission_codes,
            created_at=u.created_at
        ))
    return result


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["User & Role Management"],
    summary="Provision New Application User Account Directly",
    operation_id="createApplicationUser"
)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_postgres_db),
    _: User = Depends(require_ceo)
):
    """Create a new application user (Requires CEO)."""
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user_in.username}' already exists."
        )
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{user_in.email}' already exists."
        )
    role = db.query(Role).filter(Role.role_id == user_in.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role ID {user_in.role_id} not found."
        )

    new_user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role_id=user_in.role_id,
        employee_id=user_in.employee_id,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        user_id=new_user.user_id,
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        role_id=new_user.role_id,
        role_name=new_user.role.role_name,
        employee_id=new_user.employee_id,
        is_active=new_user.is_active,
        permissions=new_user.permission_codes,
        created_at=new_user.created_at
    )


# ------------------------------------------------------------------------------
# Activate / Disable User Account (CEO Only)
# ------------------------------------------------------------------------------

@router.patch(
    "/users/{user_id}/status",
    response_model=UserResponse,
    tags=["User & Role Management"],
    summary="Activate or Disable User Account",
    description=(
        "Enables or disables an application user account. Deactivated accounts are immediately blocked "
        "from logging in and their active JWT sessions are rejected at the authentication barrier.\n\n"
        "**Authorization:** Restricted strictly to `CEO` (and `ADMIN`). A user cannot disable themselves."
    ),
    operation_id="updateUserAccountStatus"
)
def toggle_user_status(
    user_id: int,
    status_update: UserStatusUpdate,
    db: Session = Depends(get_postgres_db),
    current_user: User = Depends(require_ceo)
):
    """Enable or disable user account (Requires CEO). Prevents self-disabling."""
    if current_user.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security Violation: You cannot disable your own application account."
        )

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    user.is_active = status_update.is_active
    db.commit()
    db.refresh(user)

    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role_id=user.role_id,
        role_name=user.role.role_name,
        employee_id=user.employee_id,
        is_active=user.is_active,
        permissions=user.permission_codes,
        created_at=user.created_at
    )


# ------------------------------------------------------------------------------
# Change User Role (CEO Only)
# ------------------------------------------------------------------------------

@router.patch(
    "/users/{user_id}/role",
    response_model=UserResponse,
    tags=["User & Role Management"],
    summary="Change User Application Role & Privileges",
    description=(
        "Reassigns a user's application role, dynamically changing their granted RBAC permission codes.\n\n"
        "**Authorization:** Restricted strictly to `CEO` (and `ADMIN`). A user cannot modify their own role."
    ),
    operation_id="updateUserApplicationRole"
)
def change_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    db: Session = Depends(get_postgres_db),
    current_user: User = Depends(require_ceo)
):
    """Change user role (Requires CEO). Prevents self-role promotion/demotion."""
    if current_user.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security Violation: You cannot modify your own application role."
        )

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    # Resolve target role either by role_id or role_name
    role = None
    if role_update.role_id:
        role = db.query(Role).filter(Role.role_id == role_update.role_id).first()
    elif role_update.role_name:
        role = db.query(Role).filter(Role.role_name == role_update.role_name.strip()).first()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found with specified role_id or role_name."
        )

    user.role_id = role.role_id
    db.commit()
    db.refresh(user)

    # Synchronize MySQL workforce job_title if user is linked to an employee
    if user.employee_id:
        try:
            new_title = ROLE_TO_JOB_TITLE.get(role.role_name, role.role_name.replace("_", " ").title())
            mysql_conn = pymysql.connect(
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                database=settings.MYSQL_DB,
                autocommit=True
            )
            with mysql_conn.cursor() as cur:
                cur.execute(
                    "UPDATE employees SET job_title = %s WHERE employee_id = %s;",
                    (new_title, user.employee_id)
                )
            mysql_conn.close()
            logger.info(f"Synchronized MySQL job_title for employee {user.employee_id} to '{new_title}'")
        except Exception as e:
            logger.warning(f"Failed to synchronize MySQL job_title for {user.employee_id}: {e}")

    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role_id=user.role_id,
        role_name=user.role.role_name,
        employee_id=user.employee_id,
        is_active=user.is_active,
        permissions=user.permission_codes,
        created_at=user.created_at
    )


# ------------------------------------------------------------------------------
# Role Catalog (CEO Only)
# ------------------------------------------------------------------------------

@router.get(
    "/roles",
    response_model=List[RoleResponse],
    tags=["User & Role Management"],
    summary="List Application Roles & Granted Permission Codes",
    operation_id="listApplicationRolesAndPermissions"
)
def list_roles(
    db: Session = Depends(get_postgres_db),
    _: User = Depends(require_ceo)
):
    """List all roles and their assigned permissions (Requires CEO)."""
    roles = db.query(Role).all()
    return [
        RoleResponse(
            role_id=r.role_id,
            role_name=r.role_name,
            description=r.description,
            permissions=[p.permission_code for p in r.permissions]
        )
        for r in roles
    ]

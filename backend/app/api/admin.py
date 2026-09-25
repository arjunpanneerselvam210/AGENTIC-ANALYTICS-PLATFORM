"""
Administrative User & Role Management Router for FreshMart.
Enforces strict RBAC permissions:
- MANAGE_USERS for account creation, listing, and activation toggling.
- MANAGE_ROLES for role reassignment and inspecting role permission matrices.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.postgres_session import get_postgres_db
from app.models.auth_models import User, Role
from app.core.security import require_permission, get_password_hash
from app.schemas.auth_schemas import (
    UserResponse,
    UserCreate,
    RoleResponse,
    UserStatusUpdate,
    UserRoleUpdate
)
from app.schemas.common_schemas import HTTPError

router = APIRouter(prefix="/admin")

# ------------------------------------------------------------------------------
# User Management Endpoints (Requires MANAGE_USERS permission)
# ------------------------------------------------------------------------------

@router.get(
    "/users",
    response_model=List[UserResponse],
    tags=["User Management"],
    summary="List All Registered Application Users",
    description=(
        "Retrieves a complete list of all FreshMart application user accounts, including their "
        "assigned role, granted permission codes, workforce employee linkage, and active status.\n\n"
        "**Authorization:** Requires `MANAGE_USERS` permission (granted to `ADMIN`)."
    ),
    operation_id="listAllApplicationUsers",
    responses={
        200: {
            "model": List[UserResponse],
            "description": "List of all user accounts successfully retrieved."
        },
        401: {
            "model": HTTPError,
            "description": "Unauthorized: Missing, invalid, or expired JWT access token."
        },
        403: {
            "model": HTTPError,
            "description": "Forbidden: User lacks the required 'MANAGE_USERS' permission."
        }
    }
)
def list_users(
    db: Session = Depends(get_postgres_db),
    _: User = Depends(require_permission("MANAGE_USERS"))
):
    """List all application users (Requires MANAGE_USERS permission)."""
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
    tags=["User Management"],
    summary="Provision New Application User Account",
    description=(
        "Provisions a new FreshMart user account with secure bcrypt password hashing and associates "
        "it with an existing application role.\n\n"
        "**Authorization:** Requires `MANAGE_USERS` permission (granted to `ADMIN`)."
    ),
    operation_id="createApplicationUser",
    responses={
        201: {
            "model": UserResponse,
            "description": "User account created successfully."
        },
        400: {
            "model": HTTPError,
            "description": "Bad Request: Username or email already exists in system."
        },
        401: {
            "model": HTTPError,
            "description": "Unauthorized: Missing, invalid, or expired JWT access token."
        },
        403: {
            "model": HTTPError,
            "description": "Forbidden: User lacks the required 'MANAGE_USERS' permission."
        },
        404: {
            "model": HTTPError,
            "description": "Not Found: The specified role_id does not exist."
        },
        422: {
            "description": "Validation Error: Invalid payload attributes."
        }
    }
)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_postgres_db),
    _: User = Depends(require_permission("MANAGE_USERS"))
):
    """Create a new application user (Requires MANAGE_USERS permission)."""
    # Check duplicate username
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user_in.username}' already exists."
        )
    # Check duplicate email
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{user_in.email}' already exists."
        )
    # Check role exists
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

@router.patch(
    "/users/{user_id}/status",
    response_model=UserResponse,
    tags=["User Management"],
    summary="Activate or Deactivate User Account",
    description=(
        "Enables or disables an application user account. Deactivated accounts are immediately blocked "
        "from logging in and their active JWT sessions are rejected at the authentication barrier.\n\n"
        "**Authorization:** Requires `MANAGE_USERS` permission (granted to `ADMIN`)."
    ),
    operation_id="updateUserAccountStatus",
    responses={
        200: {
            "model": UserResponse,
            "description": "User account status updated successfully."
        },
        401: {
            "model": HTTPError,
            "description": "Unauthorized: Missing, invalid, or expired JWT access token."
        },
        403: {
            "model": HTTPError,
            "description": "Forbidden: User lacks the required 'MANAGE_USERS' permission."
        },
        404: {
            "model": HTTPError,
            "description": "Not Found: User with specified user_id not found."
        },
        422: {
            "description": "Validation Error: Invalid user_id or payload."
        }
    }
)
def toggle_user_status(
    user_id: int,
    status_update: UserStatusUpdate,
    db: Session = Depends(get_postgres_db),
    _: User = Depends(require_permission("MANAGE_USERS"))
):
    """Enable or disable user account (Requires MANAGE_USERS permission)."""
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

@router.patch(
    "/users/{user_id}/role",
    response_model=UserResponse,
    tags=["User Management"],
    summary="Change User Application Role & Privileges",
    description=(
        "Reassigns a user's application role, dynamically changing their granted RBAC permission codes "
        "and data domain access across the platform.\n\n"
        "**Authorization:** Requires `MANAGE_ROLES` permission (granted to `ADMIN`)."
    ),
    operation_id="updateUserApplicationRole",
    responses={
        200: {
            "model": UserResponse,
            "description": "User role updated successfully."
        },
        401: {
            "model": HTTPError,
            "description": "Unauthorized: Missing, invalid, or expired JWT access token."
        },
        403: {
            "model": HTTPError,
            "description": "Forbidden: User lacks the required 'MANAGE_ROLES' permission."
        },
        404: {
            "model": HTTPError,
            "description": "Not Found: User or Role ID not found."
        },
        422: {
            "description": "Validation Error: Invalid user_id or role_id."
        }
    }
)
def change_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    db: Session = Depends(get_postgres_db),
    _: User = Depends(require_permission("MANAGE_ROLES"))
):
    """Change user role (Requires MANAGE_ROLES permission)."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    role = db.query(Role).filter(Role.role_id == role_update.role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found.")

    user.role_id = role_update.role_id
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
# Role Management Endpoints (Requires MANAGE_ROLES permission)
# ------------------------------------------------------------------------------

@router.get(
    "/roles",
    response_model=List[RoleResponse],
    tags=["Role Management"],
    summary="List Application Roles & Granted Permission Codes",
    description=(
        "Returns all 7 FreshMart application roles (ADMIN, CEO, HR_MANAGER, ERP_MANAGER, "
        "SALES_MANAGER, INVENTORY_MANAGER, FINANCE_MANAGER) along with their granular permission codes.\n\n"
        "**Authorization:** Requires `MANAGE_ROLES` permission (granted to `ADMIN`)."
    ),
    operation_id="listApplicationRolesAndPermissions",
    responses={
        200: {
            "model": List[RoleResponse],
            "description": "Roles and assigned permission codes successfully retrieved."
        },
        401: {
            "model": HTTPError,
            "description": "Unauthorized: Missing, invalid, or expired JWT access token."
        },
        403: {
            "model": HTTPError,
            "description": "Forbidden: User lacks the required 'MANAGE_ROLES' permission."
        }
    }
)
def list_roles(
    db: Session = Depends(get_postgres_db),
    _: User = Depends(require_permission("MANAGE_ROLES"))
):
    """List all roles and their assigned permissions (Requires MANAGE_ROLES permission)."""
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

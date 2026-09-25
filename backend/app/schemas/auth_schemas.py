"""
Authentication and RBAC schemas for FreshMart API.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

class LoginRequest(BaseModel):
    """User login request payload."""
    username: str = Field(
        ...,
        description="Application username (e.g. ceo, sales.manager, admin)",
        example="ceo"
    )
    password: str = Field(
        ...,
        description="Application account password",
        example="CeoPassword123!"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "username": "ceo",
                    "password": "CeoPassword123!"
                },
                {
                    "username": "sales.manager",
                    "password": "SalesPassword123!"
                },
                {
                    "username": "hr.manager",
                    "password": "HrPassword123!"
                },
                {
                    "username": "admin",
                    "password": "AdminPassword123!"
                }
            ]
        }
    )

class UserProfile(BaseModel):
    """Current authenticated user profile and granted permissions."""
    user_id: int = Field(..., description="Unique integer user identifier", example=2)
    username: str = Field(..., description="Unique application username", example="ceo")
    email: str = Field(..., description="Corporate email address", example="ceo@freshmart.local")
    full_name: str = Field(..., description="User's full name", example="Vikram Malhotra")
    role: str = Field(..., description="Assigned application role name", example="CEO")
    employee_id: Optional[str] = Field(None, description="Linked MySQL workforce employee ID", example="E006")
    permissions: List[str] = Field(
        ...,
        description="List of granular RBAC permission codes granted to this user",
        example=["VIEW_HR", "VIEW_EMPLOYEE_SALARY", "VIEW_CRM", "VIEW_SALES", "VIEW_INVENTORY", "VIEW_PURCHASES", "VIEW_FINANCE", "VIEW_PROFIT", "VIEW_EXPENSES"]
    )
    is_active: bool = Field(True, description="Account active status flag", example=True)

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    """JWT token response returned upon successful authentication."""
    access_token: str = Field(..., description="Signed JWT Bearer access token containing claims and permissions")
    token_type: str = Field("bearer", description="Token protocol type", example="bearer")
    user: UserProfile = Field(..., description="Authenticated user profile and permissions")

class UserCreate(BaseModel):
    """Payload to provision a new application user account."""
    username: str = Field(..., min_length=3, max_length=60, description="Unique username for the new account", example="anita.finance")
    email: str = Field(..., description="Unique email address", example="anita.f@freshmart.local")
    password: str = Field(..., min_length=6, description="Initial plain text password (hashed securely with bcrypt)", example="SecurePass2026!")
    full_name: str = Field(..., max_length=120, description="Full display name of the user", example="Anita Sharma")
    role_id: int = Field(..., description="Role ID to assign to this user (1: ADMIN, 2: CEO, 3: HR_MANAGER, 4: ERP_MANAGER, 5: SALES_MANAGER, 6: INVENTORY_MANAGER, 7: FINANCE_MANAGER)", example=7)
    employee_id: Optional[str] = Field(None, description="Optional MySQL employee ID to associate", example="E010")

class UserResponse(BaseModel):
    """Detailed user account representation."""
    user_id: int = Field(..., description="Unique user identifier", example=1)
    username: str = Field(..., description="Unique username", example="admin")
    email: str = Field(..., description="Email address", example="admin@freshmart.local")
    full_name: str = Field(..., description="Display name", example="Technical Administrator")
    role_id: int = Field(..., description="Foreign key reference to assigned role", example=1)
    role_name: str = Field(..., description="Name of assigned role", example="ADMIN")
    employee_id: Optional[str] = Field(None, description="Linked MySQL workforce ID", example=None)
    is_active: bool = Field(..., description="Whether user account is active", example=True)
    permissions: List[str] = Field(..., description="List of granular permission codes granted via role", example=["MANAGE_USERS", "MANAGE_ROLES"])
    created_at: datetime = Field(..., description="Account creation UTC timestamp")

    model_config = ConfigDict(from_attributes=True)

class RolePermissionResponse(BaseModel):
    """Granular permission code definition."""
    permission_id: int = Field(..., description="Unique permission identifier", example=1)
    permission_code: str = Field(..., description="Granular permission code string", example="VIEW_SALES")
    category: str = Field(..., description="Functional business category (e.g. Sales, HRMS, CRM, Finance)", example="Sales")
    description: Optional[str] = Field(None, description="Human-readable description of the privilege", example="View sales orders, order items, and regional revenue")

    model_config = ConfigDict(from_attributes=True)

class RoleResponse(BaseModel):
    """Application role representation with assigned permissions."""
    role_id: int = Field(..., description="Unique role identifier", example=5)
    role_name: str = Field(..., description="Unique role name", example="SALES_MANAGER")
    description: Optional[str] = Field(None, description="Role purpose description", example="Sales Manager. Customers, CRM, orders, and sales trends.")
    permissions: List[str] = Field(..., description="List of permission codes assigned to this role", example=["VIEW_CRM", "VIEW_SALES", "VIEW_INVENTORY"])

    model_config = ConfigDict(from_attributes=True)

class UserStatusUpdate(BaseModel):
    """Payload to activate or deactivate a user account."""
    is_active: bool = Field(..., description="Set true to enable account, false to deactivate account", example=False)

class UserRoleUpdate(BaseModel):
    """Payload to reassign a user's application role."""
    role_id: int = Field(..., description="ID of the new role to assign", example=5)

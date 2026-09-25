"""
Authentication Router for FreshMart Agentic Analytics.
Handles user login, JWT issuance, and authenticated identity/permission introspection.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.postgres_session import get_postgres_db
from app.models.auth_models import User
from app.core.security import verify_password, create_access_token, get_current_user
from app.schemas.auth_schemas import TokenResponse, UserProfile, LoginRequest
from app.schemas.common_schemas import HTTPError

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate User & Generate JWT Access Token",
    description=(
        "Authenticates a FreshMart user with username and password, returning a signed JWT Bearer access token "
        "along with the user profile, role, and granted RBAC permission codes.\n\n"
        "**Supported Content-Types:**\n"
        "- `application/json`: Standard REST API clients\n"
        "- `application/x-www-form-urlencoded`: Interactive Swagger UI Authorize dialog and HTML forms\n\n"
        "**Available Demo Accounts (Password: `<Role>Password123!` or `AdminPassword123!`):**\n"
        "- `ceo`: Full enterprise analytics access\n"
        "- `sales.manager`: Sales, CRM, and inventory analytics\n"
        "- `finance.manager`: Financial P&L, expenses, and profit analytics\n"
        "- `hr.manager`: HRMS directory and employee salary analytics\n"
        "- `inventory.manager`: Products, warehouse stock, and purchasing\n"
        "- `erp.manager`: Integrated procurement, stock, sales, and HR\n"
        "- `admin`: System administration (user and role management)"
    ),
    operation_id="loginUser",
    responses={
        200: {
            "model": TokenResponse,
            "description": "User successfully authenticated. JWT access token and user profile returned."
        },
        400: {
            "model": HTTPError,
            "description": "Bad Request: Missing username or password, or malformed request payload."
        },
        401: {
            "model": HTTPError,
            "description": "Unauthorized: Incorrect username or password."
        },
        403: {
            "model": HTTPError,
            "description": "Forbidden: User account is inactive or disabled by system administrator."
        },
        422: {
            "description": "Validation Error: Request payload could not be processed."
        }
    },
    openapi_extra={
        "requestBody": {
            "required": True,
            "description": "FreshMart application credentials submitted as JSON or Form URL-encoded data.",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/LoginRequest"
                    },
                    "examples": {
                        "ceo_login": {
                            "summary": "CEO Account (Full Access)",
                            "description": "Login as CEO with full enterprise-wide visibility.",
                            "value": {
                                "username": "ceo",
                                "password": "CeoPassword123!"
                            }
                        },
                        "sales_manager_login": {
                            "summary": "Sales Manager Account",
                            "description": "Login as Sales Manager with sales, CRM, and inventory permissions.",
                            "value": {
                                "username": "sales.manager",
                                "password": "SalesPassword123!"
                            }
                        },
                        "finance_manager_login": {
                            "summary": "Finance Manager Account",
                            "description": "Login as Finance Manager with P&L, profit, and expense access.",
                            "value": {
                                "username": "finance.manager",
                                "password": "FinancePassword123!"
                            }
                        },
                        "hr_manager_login": {
                            "summary": "HR Manager Account",
                            "description": "Login as HR Manager with employee salary inspection rights.",
                            "value": {
                                "username": "hr.manager",
                                "password": "HrPassword123!"
                            }
                        },
                        "admin_login": {
                            "summary": "System Administrator",
                            "description": "Login as Technical Administrator for user and role management.",
                            "value": {
                                "username": "admin",
                                "password": "AdminPassword123!"
                            }
                        }
                    }
                },
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "username": {
                                "type": "string",
                                "description": "Application username (e.g., ceo, sales.manager, admin)",
                                "example": "ceo"
                            },
                            "password": {
                                "type": "string",
                                "format": "password",
                                "description": "Application password",
                                "example": "CeoPassword123!"
                            },
                            "grant_type": {
                                "type": "string",
                                "default": "password"
                            }
                        },
                        "required": ["username", "password"]
                    }
                }
            }
        }
    }
)
async def login(
    request: Request,
    db: Session = Depends(get_postgres_db)
):
    """
    Authenticate user and return JWT access token.
    Supports both JSON body and standard OAuth2 form submission for Swagger UI.
    """
    username = None
    password = None

    content_type = request.headers.get("content-type", "").lower()
    if "application/json" in content_type:
        try:
            body = await request.json()
            if isinstance(body, dict):
                username = body.get("username")
                password = body.get("password")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Malformed JSON body"
            )
    else:
        try:
            form = await request.form()
            username = form.get("username")
            password = form.get("password")
        except Exception:
            pass

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required."
        )

    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated. Contact Admin."
        )

    permissions = user.permission_codes
    token_payload = {
        "sub": user.username,
        "user_id": user.user_id,
        "role": user.role.role_name,
        "permissions": permissions,
        "employee_id": user.employee_id
    }
    access_token = create_access_token(data=token_payload)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserProfile(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role.role_name,
            employee_id=user.employee_id,
            permissions=permissions,
            is_active=user.is_active
        )
    )

@router.get(
    "/me",
    response_model=UserProfile,
    summary="Get Current Authenticated User Profile",
    description=(
        "Returns profile information, role metadata, and granted RBAC permission codes "
        "for the currently authenticated user identified by the verified JWT access token."
    ),
    operation_id="getCurrentUserProfile",
    responses={
        200: {
            "model": UserProfile,
            "description": "User profile and granted permissions successfully retrieved."
        },
        401: {
            "model": HTTPError,
            "description": "Unauthorized: Missing, invalid, or expired JWT access token."
        },
        403: {
            "model": HTTPError,
            "description": "Forbidden: User account is inactive or disabled."
        }
    }
)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns profile information and granted permissions for the authenticated user.
    """
    return UserProfile(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.role_name,
        employee_id=current_user.employee_id,
        permissions=current_user.permission_codes,
        is_active=current_user.is_active
    )

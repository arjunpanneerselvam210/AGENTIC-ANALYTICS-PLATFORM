from datetime import datetime, timedelta, timezone
from typing import Optional, List, Callable
import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.postgres_session import get_postgres_db
from app.models.auth_models import User

# OAuth2 password flow scheme for Swagger UI interactive login
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=False,
    description="OAuth2 Password Flow: Authenticate using username and password"
)

# HTTP Bearer scheme for direct JWT token entry in Swagger UI Authorize dialog
http_bearer = HTTPBearer(
    auto_error=False,
    scheme_name="bearerAuth",
    description="FreshMart JWT Bearer Token. Enter token format: <token> or Bearer <token>"
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Generates a secure bcrypt password hash."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a signed JWT access token containing user claims:
    - sub (username)
    - user_id
    - role
    - permissions (list of permission codes)
    """
    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)
    if expires_delta:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """Decodes and validates a JWT token signature and expiration."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
    request: Request,
    bearer_creds: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    oauth2_token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_postgres_db)
) -> User:
    """
    FastAPI dependency that extracts and validates the authenticated User
    from the Bearer JWT token. Authoritative backend identity verification.
    Supports HTTPBearer, OAuth2PasswordBearer, and direct Authorization header.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials: Missing or invalid Bearer token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = None
    if bearer_creds and bearer_creds.credentials:
        token = bearer_creds.credentials
    elif oauth2_token:
        token = oauth2_token
    else:
        auth_header = request.headers.get("Authorization", "")
        scheme, param = get_authorization_scheme_param(auth_header)
        if scheme.lower() == "bearer" and param:
            token = param

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled. Contact system administrator."
        )
    return user

def require_permission(required_permission: str) -> Callable:
    """
    RBAC Permission Guard Dependency Factory.
    Ensures the authenticated user possesses the specific permission code.
    Rejects unauthorized access at the backend layer BEFORE reaching AI or DB.
    """
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        user_perms = current_user.permission_codes
        if required_permission not in user_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied: You do not have permission '{required_permission}'."
            )
        return current_user
    return permission_checker

def require_role(required_role: str) -> Callable:
    """
    RBAC Role Guard Dependency Factory.
    Ensures the user has the required application role (e.g. 'ADMIN').
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.role_name != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied: Role '{required_role}' required."
            )
        return current_user
    return role_checker

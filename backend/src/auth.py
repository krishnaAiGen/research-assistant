import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

# Security scheme
security = HTTPBearer()

class TokenData(BaseModel):
    user_id: str
    role: str
    permissions: List[str]

class UserRole:
    ADMIN = "admin"
    ANALYTICS = "analytics"
    USER = "user"

class Permission:
    UPLOAD = "upload"
    ANALYTICS = "analytics"
    POPULAR = "popular"

# Role-based permissions mapping
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [Permission.UPLOAD, Permission.ANALYTICS, Permission.POPULAR],
    UserRole.ANALYTICS: [Permission.ANALYTICS, Permission.POPULAR],
    UserRole.USER: []  # Basic user permissions (search, document access, etc.)
}

def create_access_token(user_id: str, role: str) -> str:
    """Create a JWT access token"""
    permissions = ROLE_PERMISSIONS.get(role, [])
    
    payload = {
        "user_id": user_id,
        "role": role,
        "permissions": permissions,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> TokenData:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        user_id = payload.get("user_id")
        role = payload.get("role")
        permissions = payload.get("permissions", [])
        
        if not user_id or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        return TokenData(
            user_id=user_id,
            role=role,
            permissions=permissions
        )
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """Get current user from JWT token"""
    token = credentials.credentials
    return verify_token(token)

def require_permission(required_permission: str):
    """Decorator to require specific permission"""
    def permission_checker(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        if required_permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {required_permission}"
            )
        return current_user
    
    return permission_checker

def require_role(required_role: str):
    """Decorator to require specific role"""
    def role_checker(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient role. Required: {required_role}, Current: {current_user.role}"
            )
        return current_user
    
    return role_checker

# Convenience functions for specific permissions
def require_upload_permission():
    """Require upload permission (admin only)"""
    return require_permission(Permission.UPLOAD)

def require_analytics_permission():
    """Require analytics permission (admin or analytics role)"""
    return require_permission(Permission.ANALYTICS)

def require_popular_permission():
    """Require popular permission (admin or analytics role)"""
    return require_permission(Permission.POPULAR) 
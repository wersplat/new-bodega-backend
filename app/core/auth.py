"""
Authentication utilities and JWT token management using Supabase
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt import PyJWTError as JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from typing import List, Optional
from pydantic import BaseModel

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

from app.core.config import settings
from app.core.supabase import supabase
from app.schemas.user import UserInDB

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.warning("JWT token missing 'sub' claim")
            return None
        return username
    except JWTError as e:
        logger.warning(f"JWT token verification failed: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error verifying JWT token: {str(e)}", exc_info=True)
        return None

async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme)
) -> UserInDB:
    """Get current authenticated user from Supabase"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Log authentication attempt
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"Authentication attempt from {client_host}")
    
    email = verify_token(token)
    if email is None:
        logger.warning(f"Invalid token provided from {client_host}")
        raise credentials_exception
    
    try:
        # Get user data from Supabase
        result = supabase.get_client().table("users").select("*").eq("email", email).single().execute()
        if not result.data:
            logger.warning(f"User not found in database: {email}")
            raise credentials_exception
        
        # Convert to UserInDB model
        user_data = result.data
        user = UserInDB(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data.get("full_name"),
            is_active=user_data.get("is_active", True),
            is_admin=user_data.get("is_admin", False),
            discord_id=user_data.get("discord_id"),
            created_at=user_data["created_at"],
            updated_at=user_data.get("updated_at")
        )
        
        # Log successful authentication
        logger.info(f"Successfully authenticated user: {user.email} (ID: {user.id})")
        return user
    except Exception as e:
        logger.error(f"Error during user authentication for {email}: {str(e)}", exc_info=True)
        raise credentials_exception

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Get current admin user"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


class RoleChecker:
    """
    Role-based access control for API endpoints.
    
    Usage:
        admin_role = RoleChecker(["admin"])
        moderator_role = RoleChecker(["moderator"])
        admin_or_moderator = RoleChecker(["admin", "moderator"])
        
        @router.get("/admin")
        async def admin_route(current_user: UserInDB = Depends(admin_role)):
            ...
    """
    
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
    
    async def __call__(
        self, 
        current_user: UserInDB = Depends(get_current_active_user)
    ) -> UserInDB:
        """
        Check if the current user has any of the allowed roles.
        
        Args:
            current_user: The authenticated user
            
        Returns:
            The current user if authorized
            
        Raises:
            HTTPException: 403 if user doesn't have required roles
        """
        # Super admins have access to everything
        if current_user.is_admin:
            return current_user
            
        # Check if user has any of the allowed roles
        user_roles = []
        if hasattr(current_user, 'roles') and current_user.roles:
            user_roles = [role.lower() for role in current_user.roles]
        
        # Allow if user has any of the required roles
        if not any(role.lower() in self.allowed_roles for role in user_roles):
            logger.warning(
                f"User {current_user.email} (ID: {current_user.id}) "
                f"attempted to access endpoint requiring roles: {self.allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {', '.join(self.allowed_roles)}"
            )
            
        return current_user 
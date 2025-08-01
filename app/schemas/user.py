"""
Pydantic schemas for user authentication and management
"""

from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_serializer
from typing import Optional, ClassVar, Dict, Any, Union
from datetime import datetime
from uuid import UUID, uuid4

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    discord_id: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    discord_id: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str  # UUID from Supabase Auth
    created_at: datetime
    updated_at: Optional[datetime] = None

class User(UserInDB):
    pass

class UserLogin(BaseModel):
    email: str  # Changed from username to email to match Supabase Auth
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: Optional[int] = None  # Optional token expiration in seconds
    refresh_token: Optional[str] = None  # Optional refresh token for Supabase

class TokenData(BaseModel):
    sub: str  # Will contain the user's email
    user_id: str  # User's UUID from Supabase
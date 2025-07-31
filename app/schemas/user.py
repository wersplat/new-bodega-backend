"""
Pydantic schemas for user authentication and management
"""

from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_serializer
from typing import Optional, ClassVar, Dict, Any
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    discord_id: Optional[str] = None

class UserInDB(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool = True
    is_admin: bool = False
    discord_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class User(UserInDB):
    pass

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 
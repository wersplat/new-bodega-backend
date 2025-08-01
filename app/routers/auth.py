"""
Authentication router for user login and registration using Supabase
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.core.auth import verify_password, create_access_token, get_current_active_user
from app.core.config import settings
from app.core.supabase import supabase
from app.schemas.user import UserCreate, User as UserSchema, Token, UserInDB

router = APIRouter()

@router.post("/register", response_model=UserSchema)
async def register(user: UserCreate):
    """
    Register a new user account with Supabase Auth
    """
    try:
        # Check if user already exists
        existing_user = supabase.get_client().auth.admin.list_users()
        if any(u.email == user.email for u in existing_user.users):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user in Supabase Auth
        auth_response = supabase.sign_up_with_email(
            email=user.email,
            password=user.password,
            user_metadata={
                "username": user.username,
                "full_name": user.full_name
            }
        )
        
        # Create user in users table
        user_data = {
            "id": auth_response.user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": True
        }
        
        # Insert user data into users table
        result = supabase.get_client().table("users").insert(user_data).execute()
        
        return {
            "id": auth_response.user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login user and return access token
    """
    try:
        # Authenticate with Supabase
        auth_response = supabase.sign_in_with_email(
            email=form_data.username,  # username is email in OAuth2PasswordRequestForm
            password=form_data.password
        )
        
        # Get user data from users table
        user_data = supabase.get_client().table("users") \
            .select("*") \
            .eq("email", form_data.username) \
            .single() \
            .execute()
            
        user = user_data.data
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"], "user_id": user["id"]},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_active_user)):
    """
    Get current user information
    """
    return current_user
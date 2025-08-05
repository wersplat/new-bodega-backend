"""
Authentication router for user login and registration using Supabase
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import logging

from fastapi.responses import RedirectResponse
from urllib.parse import urlencode

from app.core.auth import verify_password, create_access_token, get_current_active_user
from app.core.config import settings
from app.core.supabase import supabase, SupabaseService
from app.schemas.user import UserCreate, User as UserSchema, Token, UserInDB

router = APIRouter()

@router.post("/register", response_model=UserSchema)
async def register(user: UserCreate):
    """
    Register a new user account with Supabase Auth
    
    This endpoint uses the service role key to create the user, which bypasses RLS.
    The service role key is required because user registration is an admin operation.
    """
    import logging
    import json
    from app.core.supabase import SupabaseService
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Starting registration for user: {user.email}")
        
        # Get admin client for user registration
        try:
            admin_client = SupabaseService.get_client(admin=True)
            logger.info(f"Using admin client for registration with URL: {admin_client.supabase_url}")
        except Exception as e:
            logger.error(f"Failed to initialize admin client: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize authentication service"
            )
        
        # Check if user already exists
        try:
            logger.info("Checking for existing users...")
            existing_users = admin_client.auth.admin.list_users()
            logger.info(f"Found {len(existing_users)} existing users")
            
            if any(hasattr(u, 'email') and u.email and u.email.lower() == user.email.lower() 
                  for u in existing_users):
                error_msg = f"Email {user.email} is already registered"
                logger.warning(error_msg)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )
        except Exception as e:
            logger.error(f"Error checking for existing users: {str(e)}", exc_info=True)
            # Continue with registration if we can't check existing users
            logger.warning("Could not verify if user exists, continuing with registration...")
        
        # Create user in Supabase Auth using admin client
        logger.info("Attempting to create user in Supabase Auth...")
        try:
            # Prepare user data
            user_data = {
                "email": user.email,
                "password": user.password,
                "email_confirm": True,  # Auto-confirm the email
                "user_metadata": {
                    "username": user.username,
                    "full_name": user.full_name
                }
            }
            
            logger.info(f"Creating user with data: {json.dumps(user_data, default=str)}")
            
            # Create user with email and password
            try:
                auth_response = admin_client.auth.admin.create_user(user_data)
                logger.info(f"Auth response type: {type(auth_response)}")
                logger.info(f"Auth response dir: {dir(auth_response)}")
                
                # Try to convert response to dict for logging
                try:
                    auth_dict = auth_response.dict() if hasattr(auth_response, 'dict') else str(auth_response)
                    logger.info(f"Auth response: {json.dumps(auth_dict, default=str)}")
                except Exception as e:
                    logger.warning(f"Could not convert auth response to dict: {str(e)}")
                
                # Check if user was created successfully
                if not hasattr(auth_response, 'user') or not auth_response.user:
                    logger.error("Auth response is missing user data")
                    raise Exception("Failed to create user: Invalid response from authentication service")
                    
                user_id = auth_response.user.id if hasattr(auth_response.user, 'id') else None
                if not user_id:
                    logger.error("Auth response is missing user ID")
                    raise Exception("Failed to create user: No user ID in response")
                
                logger.info(f"Successfully created user with ID: {user_id}")
                
                # Create user in users table using the admin client to bypass RLS
                db_user_data = {
                    "id": user_id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "is_active": True
                }
                
                logger.info(f"Inserting user data into users table: {db_user_data}")
                try:
                    # First, check if the users table exists and get its structure
                    try:
                        table_info = admin_client.table("users").select("*", count='exact', limit=1).execute()
                        logger.info(f"Users table info: {table_info}")
                    except Exception as table_error:
                        logger.error(f"Error checking users table: {str(table_error)}", exc_info=True)
                    
                    # Try to insert the user data with detailed error handling
                    try:
                        result = admin_client.table("users").insert(db_user_data).execute()
                        logger.info(f"User data inserted successfully: {result}")
                        
                        # Verify the data was inserted
                        try:
                            inserted_user = admin_client.table("users").select("*").eq("id", user_id).execute()
                            logger.info(f"Verification query result: {inserted_user}")
                        except Exception as verify_error:
                            logger.error(f"Error verifying user insertion: {str(verify_error)}", exc_info=True)
                        
                        return {
                            "id": user_id,
                            "username": user.username,
                            "email": user.email,
                            "full_name": user.full_name,
                            "is_active": True
                        }
                        
                    except Exception as insert_error:
                        # Try to get more detailed error information
                        error_detail = str(insert_error)
                        error_type = type(insert_error).__name__
                        logger.error(f"Database insert failed with {error_type}: {error_detail}", exc_info=True)
                        
                        # If available, get the full error response
                        if hasattr(insert_error, 'args') and insert_error.args:
                            error_args = insert_error.args
                            logger.error(f"Error args: {error_args}")
                            
                            # Try to extract the error message from the response
                            if len(error_args) > 1 and hasattr(error_args[1], 'get'):
                                error_response = error_args[1]
                                error_message = error_response.get('message', str(error_response))
                                error_detail = f"Database error: {error_message}"
                        
                        raise Exception(error_detail) from insert_error
                    
                except Exception as db_error:
                    logger.error(f"Failed to insert user into database: {str(db_error)}", exc_info=True)
                    
                    # Try to clean up the auth user if database insert fails
                    try:
                        if user_id:
                            logger.info(f"Attempting to clean up auth user {user_id}...")
                            delete_result = admin_client.auth.admin.delete_user(user_id)
                            logger.info(f"Cleanup result: {delete_result}")
                    except Exception as cleanup_error:
                        logger.error(f"Failed to clean up auth user after database error: {str(cleanup_error)}", exc_info=True)
                    
                    # Provide more detailed error information
                    error_detail = str(db_error)
                    if "duplicate key" in error_detail.lower():
                        error_detail = "This username or email is already in use."
                    elif "null value" in error_detail.lower() and "violates not-null constraint" in error_detail.lower():
                        error_detail = "Required user information is missing."
                    
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"User account created but failed to save user data: {error_detail}"
                    )
                
            except Exception as auth_error:
                logger.error(f"Failed to create auth user: {str(auth_error)}", exc_info=True)
                raise auth_error
                
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error during user registration: {error_msg}", exc_info=True)
            
            # Provide more specific error messages
            if "already registered" in error_msg.lower() or "already in use" in error_msg.lower():
                error_detail = "This email is already registered"
            elif "password" in error_msg.lower():
                error_detail = "Password does not meet requirements. It should be at least 6 characters long."
            elif "invalid email" in error_msg.lower():
                error_detail = "Please provide a valid email address"
            elif "auth" in error_msg.lower() and "disabled" in error_msg.lower():
                error_detail = "User registration is currently disabled"
            else:
                error_detail = f"Registration failed: {error_msg}"
                
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail
            )
            
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions as-is
        raise http_exc
        
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration. Please try again later."
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

@router.get("/callback")
async def oauth_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    error_description: str = None
):
    """
    OAuth callback endpoint for handling authentication redirects
    This endpoint receives the OAuth callback from Supabase and redirects to the appropriate frontend
    """
    try:
        if error:
            # Handle OAuth errors
            error_params = urlencode({
                'error': error,
                'error_description': error_description or 'Authentication failed'
            })
            
            # Redirect to frontend with error
            frontend_url = settings.FRONTEND_URL or "http://localhost:3000"
            return RedirectResponse(url=f"{frontend_url}/auth/error?{error_params}")
        
        if not code:
            # No authorization code received
            return RedirectResponse(url=f"{settings.FRONTEND_URL or 'http://localhost:3000'}/auth/error?error=no_code")
        
        # Exchange the authorization code for a session
        try:
            client = supabase.get_client()
            session = client.auth.exchange_code_for_session(code)
            
            if session and session.access_token:
                # Successfully authenticated
                # Redirect to frontend with success
                frontend_url = settings.FRONTEND_URL or "http://localhost:3000"
                
                # You can add additional parameters like user info if needed
                success_params = urlencode({
                    'access_token': session.access_token,
                    'refresh_token': session.refresh_token,
                    'expires_at': str(session.expires_at) if session.expires_at else '',
                    'user_id': session.user.id if session.user else ''
                })
                
                return RedirectResponse(url=f"{frontend_url}/auth/callback?{success_params}")
            else:
                # No session received
                return RedirectResponse(url=f"{settings.FRONTEND_URL or 'http://localhost:3000'}/auth/error?error=no_session")
                
        except Exception as e:
            # Handle session exchange errors
            error_params = urlencode({
                'error': 'session_exchange_failed',
                'error_description': str(e)
            })
            return RedirectResponse(url=f"{settings.FRONTEND_URL or 'http://localhost:3000'}/auth/error?{error_params}")
            
    except Exception as e:
        # Handle any other errors
        error_params = urlencode({
            'error': 'callback_error',
            'error_description': str(e)
        })
        return RedirectResponse(url=f"{settings.FRONTEND_URL or 'http://localhost:3000'}/auth/error?{error_params}")

@router.get("/debug/config")
async def debug_config():
    """
    Debug endpoint to check Supabase configuration
    """
    client = supabase.get_client()
    
    # Get auth settings (if available)
    auth_settings = {}
    try:
        # This is a protected endpoint in newer versions, so it might fail
        auth_settings = client.auth.get_settings()
    except Exception as e:
        auth_settings = {"error": str(e)}
    
    # Get client configuration (without sensitive data)
    config = {
        "supabase_url": client.supabase_url,
        "supabase_key_type": "ANON_KEY" if client.supabase_key == settings.SUPABASE_ANON_KEY else "SERVICE_KEY",
        "auth_settings": auth_settings,
        "settings": {
            "SUPABASE_URL": settings.SUPABASE_URL,
            "SUPABASE_ANON_KEY": f"{settings.SUPABASE_ANON_KEY[:10]}...{settings.SUPABASE_ANON_KEY[-5:]}" if settings.SUPABASE_ANON_KEY else None,
            "SUPABASE_KEY": f"{settings.SUPABASE_KEY[:10]}...{settings.SUPABASE_KEY[-5:]}" if settings.SUPABASE_KEY else None,
            "DEBUG": settings.DEBUG
        }
    }
    
    return config

@router.get("/debug/users-table")
async def debug_users_table():
    """
    Debug endpoint to inspect the users table structure and data
    """
    try:
        admin_client = SupabaseService.get_client(admin=True)
        
        # Get table structure by selecting a single row
        table_info = admin_client.table("users").select("*").limit(1).execute()
        
        # Get row count
        row_count = admin_client.table("users").select("id", count='exact').execute()
        
        # Get table info from information_schema
        table_schema = admin_client.rpc('get_table_schema', {'table_name': 'users'}).execute()
        
        return {
            "table_info": table_info.data if hasattr(table_info, 'data') else str(table_info),
            "row_count": row_count.count if hasattr(row_count, 'count') else "Unknown",
            "table_schema": table_schema.data if hasattr(table_schema, 'data') else str(table_schema)
        }
        
    except Exception as e:
        error_detail = str(e)
        if hasattr(e, 'args') and e.args:
            error_detail = str(e.args)
        
        return {
            "error": "Failed to inspect users table",
            "details": error_detail,
            "type": type(e).__name__
        }

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_active_user)):
    """
    Get current user information
    """
    return current_user
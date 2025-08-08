"""
Supabase client initialization and utilities with type hints
"""
from typing import Optional, Dict, Any, List, TypeVar, Generic, Type, Union, Callable, Iterator, ContextManager
from contextlib import contextmanager
from fastapi import HTTPException
from pydantic import BaseModel
from supabase import create_client, Client as SupabaseClient
from app.core.config import settings
import os

# Type variables for generic operations
T = TypeVar('T', bound=BaseModel)

class TransactionError(Exception):
    """Exception raised for errors in database transactions"""
    pass

class SupabaseService:
    _client: Optional[SupabaseClient] = None
    _admin_client: Optional[SupabaseClient] = None

    @classmethod
    def get_client(cls, admin: bool = False) -> SupabaseClient:
        """Get or create the Supabase client instance
        
        Args:
            admin: If True, returns a client with service role key for admin operations.
                  If False, returns a client with anon key for public operations.
                  
        Returns:
            SupabaseClient: Configured Supabase client instance
            
        Note: The service role key bypasses Row Level Security (RLS) and should only be used
              for administrative operations on the server side. Never expose the service role
              key to client-side code.
        """
        if admin:
            if cls._admin_client is None:
                # Prefer explicit service role key; fall back to SUPABASE_KEY
                service_role_key = (
                    settings.SUPABASE_KEY
                    or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
                    or os.getenv("SERVICE_ROLE_KEY", "")
                )
                if not settings.SUPABASE_URL or not service_role_key:
                    raise ValueError("Supabase URL and service role key must be set in environment variables")
                # Safety: avoid accidentally using anon key for admin client
                if service_role_key.startswith("sb-publishable-"):
                    # Try to recover by reading common env var names
                    alt = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SERVICE_ROLE_KEY")
                    if alt and alt.startswith("sb-service-"):
                        service_role_key = alt
                cls._admin_client = create_client(settings.SUPABASE_URL, service_role_key)
            return cls._admin_client
        else:
            if cls._client is None:
                if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
                    raise ValueError("Supabase URL and anon key must be set in environment variables")
                cls._client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
            return cls._client
        
    @classmethod
    @contextmanager
    def transaction(cls) -> Iterator[SupabaseClient]:
        """Context manager for database transactions
        
        Example:
            with supabase.transaction() as db:
                # Perform operations within transaction
                db.table('users').insert(...).execute()
                db.table('profiles').update(...).execute()
                # Commit happens automatically if no exceptions
        """
        client = cls.get_client()
        try:
            # Start a transaction
            client.rpc('begin')
            yield client
            # Commit the transaction
            client.rpc('commit')
        except Exception as e:
            # Rollback on error
            client.rpc('rollback')
            raise TransactionError(f"Transaction failed: {str(e)}") from e
        
    # Generic CRUD Operations
    @classmethod
    def fetch_all(cls, table: str) -> List[Dict[str, Any]]:
        """Fetch all records from a table"""
        client = cls.get_client()
        response = client.table(table).select("*").execute()
        return response.data if hasattr(response, 'data') else []

    @classmethod
    def fetch_by_id(cls, table: str, id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """Fetch a single record by ID from the specified table using Session.get()
        
        Args:
            table: Name of the table to query
            id: ID of the record to fetch (can be string or integer)
            
        Returns:
            Dictionary containing the record data if found, None otherwise
        """
        client = cls.get_client()
        try:
            # Try to use Session.get() for primary key lookups
            response = client.table(table).select("*").eq('id', id).single().execute()
            return response.data if hasattr(response, 'data') and response.data else None
        except Exception:
            # Fall back to the standard query if single() is not supported
            response = client.table(table).select("*").eq('id', id).execute()
            return response.data[0] if hasattr(response, 'data') and response.data and len(response.data) > 0 else None

    @classmethod
    def insert(cls, table: str, data: Dict[str, Any], client: Optional[SupabaseClient] = None) -> Optional[Dict[str, Any]]:
        """Insert a new record into the specified table
        
        Args:
            table: Name of the table to insert into
            data: Dictionary of data to insert
            client: Optional client to use for the operation (for transactions)
            
        Returns:
            Dictionary containing the inserted record if successful, None otherwise
        """
        client = client or cls.get_client()
        response = client.table(table).insert(data).execute()
        return response.data[0] if response.data and len(response.data) > 0 else None

    @classmethod
    def update(cls, table: str, id: Union[str, int], data: Dict[str, Any], client: Optional[SupabaseClient] = None) -> Optional[Dict[str, Any]]:
        """Update a record in the specified table
        
        Args:
            table: Name of the table containing the record
            id: ID of the record to update (can be string or integer)
            data: Dictionary of fields to update
            client: Optional client to use for the operation (for transactions)
            
        Returns:
            Dictionary containing the updated record if successful, None otherwise
        """
        client = client or cls.get_client()
        response = client.table(table).update(data).eq('id', id).execute()
        return response.data[0] if response.data and len(response.data) > 0 else None

    @classmethod
    def delete(cls, table: str, id: Union[str, int], client: Optional[SupabaseClient] = None) -> bool:
        """Delete a record from the specified table
        
        Args:
            table: Name of the table containing the record
            id: ID of the record to delete (can be string or integer)
            client: Optional client to use for the operation (for transactions)
            
        Returns:
            bool: True if record was deleted, False otherwise
        """
        client = client or cls.get_client()
        response = client.table(table).delete().eq('id', id).execute()
        return len(response.data) > 0 if hasattr(response, 'data') and response.data else False

    # Authentication Methods
    @classmethod
    def get_user(cls, jwt: str) -> Dict[str, Any]:
        """Get user from Supabase Auth using JWT"""
        client = cls.get_client()
        return client.auth.get_user(jwt)

    @classmethod
    def sign_in_with_email(cls, email: str, password: str) -> Dict[str, Any]:
        """Sign in with email and password"""
        client = cls.get_client()
        return client.auth.sign_in_with_password({"email": email, "password": password})

    @classmethod
    def sign_up_with_email(
        cls, 
        email: str, 
        password: str, 
        user_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Sign up a new user with email and password
        
        Args:
            email: User's email address
            password: User's password
            user_metadata: Optional metadata to include with the user
            
        Returns:
            Dict containing the user data if successful
            
        Raises:
            HTTPException: If there's an error during signup
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"Attempting to sign up user with email: {email}")
            client = cls.get_client()
            
            # Ensure email is a string and not empty
            if not isinstance(email, str) or not email.strip():
                error_msg = f"Invalid email format: {email}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            # Ensure password meets minimum requirements
            if not isinstance(password, str) or len(password) < 6:
                error_msg = "Password must be at least 6 characters"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Normalize email - ensure it's in the correct format
            normalized_email = email.strip().lower()
            
            # Log the signup attempt
            logger.debug(f"Attempting to sign up with email: {normalized_email}")
            
            # Attempt to sign up the user
            result = client.auth.sign_up({
                "email": normalized_email,
                "password": password,
                "options": {
                    "data": user_metadata or {}
                }
            })
            
            if hasattr(result, 'user') and result.user:
                logger.info(f"Successfully signed up user: {result.user.id}")
                return {
                    "id": result.user.id,
                    "email": result.user.email,
                    "created_at": getattr(result.user, 'created_at', None),
                    "confirmed_at": getattr(result.user, 'confirmed_at', None)
                }
            else:
                logger.warning("Signup response missing user data")
                return {"message": "Check your email for the confirmation link"}
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error during user signup: {error_msg}", exc_info=True)
            
            # Provide a more user-friendly error message
            if "email" in error_msg.lower() and "invalid" in error_msg.lower():
                error_msg = f"The email address '{email}' is not valid. Please check the format and try again."
            
            raise HTTPException(
                status_code=400,
                detail=error_msg
            )



    # Custom Queries (Add more as needed)
    @classmethod
    def get_players_by_team(cls, team_id: str) -> List[Dict[str, Any]]:
        """Get all players in a specific team"""
        client = cls.get_client()
        response = client.table('players').select('*').eq('team_id', team_id).execute()
        return response.data if hasattr(response, 'data') else []

    @classmethod
    def get_events_by_league(cls, league: str) -> List[Dict[str, Any]]:
        """Get all events for a specific league"""
        client = cls.get_client()
        response = client.table('events').select('*').eq('league', league).execute()
        return response.data if hasattr(response, 'data') else []

# Global Supabase client instance
supabase = SupabaseService()

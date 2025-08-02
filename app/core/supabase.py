"""
Supabase client initialization and utilities with type hints
"""
from typing import Optional, Dict, Any, List, TypeVar, Generic, Type, Union, Callable, Iterator, ContextManager
from contextlib import contextmanager
from pydantic import BaseModel
from supabase import create_client, Client as SupabaseClient
from app.core.config import settings

# Type variables for generic operations
T = TypeVar('T', bound=BaseModel)

class TransactionError(Exception):
    """Exception raised for errors in database transactions"""
    pass

class SupabaseService:
    _client: Optional[SupabaseClient] = None

    @classmethod
    def get_client(cls) -> SupabaseClient:
        """Get or create the Supabase client instance"""
        if cls._client is None:
            if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                raise ValueError("Supabase URL and key must be set in environment variables")
            cls._client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
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
        """Sign up a new user with email and password"""
        client = cls.get_client()
        return client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": user_metadata or {}
            }
        })



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

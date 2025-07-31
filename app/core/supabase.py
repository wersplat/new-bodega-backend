"""
Supabase client initialization and utilities with type hints
"""
from typing import Optional, Dict, Any, List, TypeVar, Generic, Type, Union
from pydantic import BaseModel
from supabase import create_client, Client as SupabaseClient
from app.core.config import settings

# Type variables for generic operations
T = TypeVar('T', bound=BaseModel)

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

    # Generic CRUD Operations
    @classmethod
    def fetch_all(cls, table: str) -> List[Dict[str, Any]]:
        """Fetch all records from a table"""
        client = cls.get_client()
        response = client.table(table).select("*").execute()
        return response.data if hasattr(response, 'data') else []

    @classmethod
    def fetch_by_id(cls, table: str, id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """Fetch a single record by ID"""
        client = cls.get_client()
        response = client.table(table).select("*").eq('id', id).execute()
        return response.data[0] if response.data else None

    @classmethod
    def insert(cls, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new record"""
        client = cls.get_client()
        response = client.table(table).insert(data).execute()
        return response.data[0] if response.data else None

    @classmethod
    def update(cls, table: str, id: Union[str, int], data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing record"""
        client = cls.get_client()
        response = client.table(table).update(data).eq('id', id).execute()
        return response.data[0] if response.data else None

    @classmethod
    def delete(cls, table: str, id: Union[str, int]) -> bool:
        """Delete a record by ID"""
        client = cls.get_client()
        response = client.table(table).delete().eq('id', id).execute()
        return len(response.data) > 0 if response.data else False

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

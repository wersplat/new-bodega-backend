"""
Pytest configuration and fixtures for testing
"""
import os
import pytest
from typing import Generator, Any
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from supabase import create_client

from app.core.config import settings
from app.core.supabase import SupabaseService

# Create a test FastAPI app for testing
app = FastAPI()

# Test database URL - using the same as the main database for now
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", settings.DATABASE_URL)

# Create a test Supabase client that uses the service role key
class TestSupabaseService(SupabaseService):
    """Test Supabase service that can bypass RLS"""
    
    @classmethod
    def get_client(cls) -> Any:
        """Get or create a test Supabase client instance"""
        if cls._client is None:
            # Use the service role key if available, otherwise use the regular key
            service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", settings.SUPABASE_KEY)
            cls._client = create_client(settings.SUPABASE_URL, service_role_key)
        return cls._client

# Override the global supabase instance with our test version
test_supabase = TestSupabaseService()

@pytest.fixture(scope="session")
def test_db() -> Generator[Session, None, None]:
    """
    Create a test database session and set up test data.
    This runs once per test session.
    """
    engine = create_engine(TEST_DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """
    Create a test client for the FastAPI application.
    This client will be used by all tests in the module.
    """
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="module")
def test_supabase_fixture() -> TestSupabaseService:
    """
    Provide a test Supabase client instance.
    This client will use the service role key if available.
    """
    return test_supabase

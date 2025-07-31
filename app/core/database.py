"""
Database configuration and session management with Supabase
"""
from typing import Generator, Dict, Any, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings

# SQLAlchemy setup for direct database access (if needed)
engine = None
SessionLocal = None
Base = declarative_base()

# Initialize SQLAlchemy engine if DATABASE_URL is provided
if settings.DATABASE_URL:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        echo=settings.DEBUG
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get a database session.
    Note: With Supabase, you might not need this for all operations,
    but it's kept for compatibility with existing code that uses SQLAlchemy.
    """
    if not SessionLocal:
        raise RuntimeError("Database URL not configured")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import Supabase client
from app.core.supabase import supabase as sb_client

# Re-export Supabase client for easier imports
def get_supabase():
    """Get the Supabase client instance"""
    return sb_client.get_client() 
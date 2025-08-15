"""
Tournament Model

This module defines the SQLAlchemy model for tournaments in the system.
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey, Integer, Numeric, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from app.core.database import Base

class TournamentStatus(str, Enum):
    DRAFT = "draft"
    UPCOMING = "upcoming"
    REGISTRATION_OPEN = "registration_open"
    REGISTRATION_CLOSED = "registration_closed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"

class TournamentTier(str, Enum):
    T1 = "t1"
    T2 = "t2"
    T3 = "t3"
    T4 = "t4"
    OPEN = "open"
    INVITATIONAL = "invitational"
    QUALIFIER = "qualifier"
    MAJOR = "major"
    MINOR = "minor"

# Note: Tournament class has been moved to league.py to avoid table name conflicts
# and to match the Supabase database schema

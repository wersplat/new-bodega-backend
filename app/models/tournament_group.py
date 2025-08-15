"""
Tournament Group Model

This module defines the SQLAlchemy model for tournament groups in the system.
"""
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Text, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base

# Note: TournamentGroup class has been moved to team.py to avoid table name conflicts
# and to match the Supabase database schema. The team.py version includes:
# - TournamentGroup
# - TournamentGroupMember  
# - GroupMatch
# - GroupStanding

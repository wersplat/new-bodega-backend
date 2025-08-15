"""
Tournament Model

This module defines the SQLAlchemy model for tournaments in the system.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import Column, String, ForeignKey, Integer, Boolean, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base

class Console(str, Enum):
    """Enumeration of possible console platforms."""
    PS5 = "PS5"
    XBOX_SERIES_X = "Xbox Series X"
    PC = "PC"

class GameYear(str, Enum):
    """Enumeration of NBA 2K game years."""
    2K22 = "2K22"
    2K23 = "2K23"
    2K24 = "2K24"
    2K25 = "2K25"
    2K26 = "2K26"

class EventTier(str, Enum):
    """Enumeration of event tiers."""
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"
    T4 = "T4"

class Status(str, Enum):
    """Enumeration of tournament statuses."""
    UPCOMING = "upcoming"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Tournament(Base):
    """
    SQLAlchemy model representing a tournament in the system.
    
    This model maps to the 'tournaments' table in the database.
    """
    __tablename__ = "tournaments"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=True)  # Uses Status enum
    tier = Column(String, nullable=True)    # Uses EventTier enum
    console = Column(String, nullable=True)  # Uses Console enum
    game_year = Column(String, nullable=True)  # Uses GameYear enum
    
    # Tournament dates
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    
    # Organizer information
    organizer_id = Column(PGUUID(as_uuid=True), ForeignKey("leagues_info.id"), nullable=True)
    organizer_logo_url = Column(String, ForeignKey("leagues_info.lg_logo_url"), nullable=True)
    
    # Tournament details
    banner_url = Column(String, nullable=True)
    rules_url = Column(String, nullable=True)
    place = Column(String, ForeignKey("teams.id"), nullable=True)
    prize_pool = Column(Integer, nullable=True)
    max_rp = Column(Integer, nullable=True)
    decay_days = Column(Integer, nullable=True)
    
    # Championship details
    champion = Column(String, ForeignKey("teams.id"), nullable=True)
    runner_up = Column(String, ForeignKey("teams.id"), nullable=True)
    
    # Sponsor information
    sponsor = Column(String, ForeignKey("sponsor_info.sponsor_name"), nullable=True)
    sponsor_logo = Column(String, ForeignKey("sponsor_info.sponsor_logo"), nullable=True)
    
    # Relationships
    organizer = relationship("League", foreign_keys=[organizer_id])
    organizer_logo = relationship("League", foreign_keys=[organizer_logo_url])
    
    champion_team = relationship("Team", foreign_keys=[champion])
    runner_up_team = relationship("Team", foreign_keys=[runner_up])
    place_team = relationship("Team", foreign_keys=[place])
    
    sponsor_info = relationship("SponsorInfo", foreign_keys=[sponsor])
    sponsor_logo_info = relationship("SponsorInfo", foreign_keys=[sponsor_logo])
    
    def __repr__(self):
        return f"<Tournament {self.name} ({self.status})>"

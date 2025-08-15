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

class Tournament(Base):
    """
    SQLAlchemy model representing a tournament in the system.
    """
    __tablename__ = "tournaments"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    short_name = Column(String(10), nullable=True)
    description = Column(Text, nullable=True)
    
    # Tournament details
    logo_url = Column(String, nullable=True)
    banner_url = Column(String, nullable=True)
    rules_url = Column(String, nullable=True)
    
    # Tournament configuration
    status = Column(SQLAlchemyEnum(TournamentStatus), default=TournamentStatus.DRAFT, nullable=False)
    tier = Column(SQLAlchemyEnum(TournamentTier), nullable=False)
    is_team_based = Column(Boolean, default=True, nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)
    max_teams = Column(Integer, nullable=True)
    min_teams = Column(Integer, default=2, nullable=False)
    
    # Tournament schedule
    registration_start = Column(DateTime, nullable=True)
    registration_end = Column(DateTime, nullable=True)
    check_in_start = Column(DateTime, nullable=True)
    check_in_end = Column(DateTime, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    
    # Game settings
    game_title = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    region = Column(String, nullable=True)
    
    # Prize pool
    prize_pool = Column(Numeric(12, 2), default=0.0, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    # External references
    league_id = Column(String, ForeignKey("leagues_info.id"), nullable=True)
    organizer_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)
    
    # Relationships
    league = relationship("League", back_populates="tournaments")
    organizer = relationship("User", back_populates="organized_tournaments")
    tournament_groups = relationship("TournamentGroup", back_populates="tournament")
    matches = relationship("Match", back_populates="tournament")
    tournament_results = relationship("TournamentResult", back_populates="tournament")
    rp_transactions = relationship("PlayerRPTransaction", back_populates="tournament")
    pot_tracker_entries = relationship("TeamsPotTracker", back_populates="tournament")
    match_submissions = relationship("MatchSubmission", back_populates="tournament")
    upcoming_matches = relationship("UpcomingMatch", back_populates="tournament")
    
    def __repr__(self):
        return f"<Tournament(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        """Convert the tournament to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'short_name': self.short_name,
            'description': self.description,
            'logo_url': self.logo_url,
            'banner_url': self.banner_url,
            'rules_url': self.rules_url,
            'status': self.status.value if self.status else None,
            'tier': self.tier.value if self.tier else None,
            'is_team_based': self.is_team_based,
            'is_public': self.is_public,
            'max_teams': self.max_teams,
            'min_teams': self.min_teams,
            'registration_start': self.registration_start.isoformat() if self.registration_start else None,
            'registration_end': self.registration_end.isoformat() if self.registration_end else None,
            'check_in_start': self.check_in_start.isoformat() if self.check_in_start else None,
            'check_in_end': self.check_in_end.isoformat() if self.check_in_end else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'game_title': self.game_title,
            'platform': self.platform,
            'region': self.region,
            'prize_pool': float(self.prize_pool) if self.prize_pool else 0.0,
            'currency': self.currency,
            'league_id': self.league_id,
            'organizer_id': self.organizer_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

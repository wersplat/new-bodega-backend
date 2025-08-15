"""
Tournament Result Model

This module defines the SQLAlchemy model for tournament results in the system.
"""

from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, func, Boolean, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class TournamentResult(Base):
    """
    SQLAlchemy model representing tournament results in the system.
    
    This model maps to the 'event_results' table in the database.
    """
    __tablename__ = "event_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    placement = Column(Integer, nullable=False)
    rp_awarded = Column(Integer, nullable=False)
    bonus_rp = Column(Integer, default=0, nullable=False)
    total_rp = Column(Integer, nullable=False)  # This is a generated column in the database
    awarded_at = Column(DateTime, server_default=func.now(), nullable=False)
    prize_amount = Column(Numeric(10, 2), nullable=True)
    winner_banner_url = Column(String, nullable=True)
    tournament_id = Column(UUID(as_uuid=True), ForeignKey("tournaments.id"), nullable=False)
    league_id = Column(String, ForeignKey("leagues_info.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    team = relationship("Team", back_populates="event_results")
    tournament = relationship("Tournament", back_populates="event_results")
    league = relationship("LeagueInfo", back_populates="event_results")
    
    def __repr__(self):
        return f"<TournamentResult(id={self.id}, team_id={self.team_id}, placement={self.placement}, tournament_id={self.tournament_id})>"
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            'id': str(self.id),
            'team_id': self.team_id,
            'placement': self.placement,
            'rp_awarded': self.rp_awarded,
            'bonus_rp': self.bonus_rp,
            'total_rp': self.total_rp,
            'awarded_at': self.awarded_at.isoformat() if self.awarded_at else None,
            'prize_amount': float(self.prize_amount) if self.prize_amount is not None else None,
            'winner_banner_url': self.winner_banner_url,
            'tournament_id': str(self.tournament_id),
            'league_id': self.league_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

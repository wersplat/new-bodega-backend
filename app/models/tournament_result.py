"""
Tournament Result Model

This module defines the SQLAlchemy model for tournament results in the system.
"""
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Numeric, Text, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base

class TournamentResult(Base):
    """
    SQLAlchemy model representing a team's result in a tournament.
    """
    __tablename__ = "tournament_results"
    
    id = Column(String, primary_key=True, index=True)
    tournament_id = Column(String, ForeignKey("tournaments.id"), nullable=False)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    league_id = Column(String, ForeignKey("leagues_info.id"), nullable=True)
    
    # Placement and results
    placement = Column(Integer, nullable=False)
    is_winner = Column(Boolean, default=False, nullable=False)
    is_runner_up = Column(Boolean, default=False, nullable=False)
    
    # Points and awards
    rp_awarded = Column(Integer, default=0, nullable=False)  # Ranking points
    bonus_rp = Column(Integer, default=0, nullable=False)    # Any bonus points
    total_rp = Column(Integer, default=0, nullable=False)    # Total points (rp_awarded + bonus_rp)
    prize_amount = Column(Numeric(12, 2), default=0.0, nullable=False)
    prize_currency = Column(String(3), default="USD", nullable=False)
    
    # Additional details
    winner_banner_url = Column(String, nullable=True)  # URL to winner's banner
    notes = Column(Text, nullable=True)                # Any additional notes
    
    # Timestamps
    awarded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)
    
    # Relationships
    tournament = relationship("Tournament", back_populates="tournament_results")
    team = relationship("Team", back_populates="tournament_results")
    league = relationship("League", back_populates="tournament_results")
    
    def __repr__(self):
        return f"<TournamentResult(id={self.id}, placement={self.placement}, tournament_id={self.tournament_id}, team_id={self.team_id})>"
    
    def to_dict(self):
        """Convert the tournament result to a dictionary."""
        return {
            'id': self.id,
            'tournament_id': self.tournament_id,
            'team_id': self.team_id,
            'league_id': self.league_id,
            'placement': self.placement,
            'is_winner': self.is_winner,
            'is_runner_up': self.is_runner_up,
            'rp_awarded': self.rp_awarded,
            'bonus_rp': self.bonus_rp,
            'total_rp': self.total_rp,
            'prize_amount': float(self.prize_amount) if self.prize_amount else 0.0,
            'prize_currency': self.prize_currency,
            'winner_banner_url': self.winner_banner_url,
            'notes': self.notes,
            'awarded_at': self.awarded_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

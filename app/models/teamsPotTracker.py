"""
Teams Pot Tracker Model

This module defines the SQLAlchemy model for tracking team pot winnings.
"""
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Numeric
from sqlalchemy.orm import relationship

from app.core.database import Base

class TeamsPotTracker(Base):
    """
    SQLAlchemy model for tracking team pot winnings.
    """
    __tablename__ = "teams_pot_tracker"
    
    id = Column(String, primary_key=True, index=True)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    league_id = Column(String, ForeignKey("leagues_info.id"), nullable=True)
    tournament_id = Column(String, ForeignKey("tournaments.id"), nullable=True)
    amount = Column(Numeric(10, 2), default=0.0, nullable=False)
    last_updated = Column(DateTime, nullable=True)
    
    # Relationships
    team = relationship("Team", back_populates="teams_pot_tracker")
    league = relationship("League", back_populates="teams_pot_tracker")
    tournament = relationship("Tournament", back_populates="teams_pot_tracker")
    
    def __repr__(self):
        return f"<TeamsPotTracker(id={self.id}, team_id={self.team_id}, amount={self.amount})>"
    
    def to_dict(self):
        """Convert the pot tracker to a dictionary."""
        return {
            'id': self.id,
            'team_id': self.team_id,
            'league_id': self.league_id,
            'tournament_id': self.tournament_id,
            'amount': float(self.amount) if self.amount is not None else 0.0,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
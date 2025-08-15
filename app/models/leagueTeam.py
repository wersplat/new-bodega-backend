"""
League Team Model

This module defines the SQLAlchemy model for the many-to-many relationship between leagues and teams.
"""
from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base

class LeagueTeam(Base):
    """
    SQLAlchemy model representing the many-to-many relationship between leagues and teams.
    """
    __tablename__ = "league_teams"
    
    id = Column(String, primary_key=True, index=True)
    league_id = Column(String, ForeignKey("leagues_info.id"), nullable=False)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    joined_at = Column(DateTime, nullable=False)
    left_at = Column(DateTime, nullable=True)
    
    # Relationships
    league = relationship("League", back_populates="league_teams")
    team = relationship("Team", back_populates="league_teams")
    
    def __repr__(self):
        return f"<LeagueTeam(id={self.id}, league_id={self.league_id}, team_id={self.team_id})>"
    
    def to_dict(self):
        """Convert the league-team relationship to a dictionary."""
        return {
            'id': self.id,
            'league_id': self.league_id,
            'team_id': self.team_id,
            'is_active': self.is_active,
            'joined_at': self.joined_at.isoformat(),
            'left_at': self.left_at.isoformat() if self.left_at else None
        }

"""
Team Player Model

This module defines the SQLAlchemy model for the many-to-many relationship between teams and players.
"""
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, Integer
from sqlalchemy.orm import relationship

from app.core.database import Base

class TeamPlayer(Base):
    """
    SQLAlchemy model representing the many-to-many relationship between teams and players.
    """
    __tablename__ = "team_players"
    
    id = Column(String, primary_key=True, index=True)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    player_id = Column(String, ForeignKey("players.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_captain = Column(Boolean, default=False, nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    left_at = Column(DateTime, nullable=True)
    jersey_number = Column(Integer, nullable=True)
    
    # Relationships
    team = relationship("Team", back_populates="team_players")
    player = relationship("Player", back_populates="team_players")
    
    def __repr__(self):
        return f"<TeamPlayer(id={self.id}, team_id={self.team_id}, player_id={self.player_id})>"
    
    def to_dict(self):
        """Convert the team-player relationship to a dictionary."""
        return {
            'id': self.id,
            'team_id': self.team_id,
            'player_id': self.player_id,
            'is_active': self.is_active,
            'is_captain': self.is_captain,
            'joined_at': self.joined_at.isoformat(),
            'left_at': self.left_at.isoformat() if self.left_at else None,
            'jersey_number': self.jersey_number
        }

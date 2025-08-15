"""
Match MVP Model

This module defines the SQLAlchemy model for match MVPs in the system.
"""
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Text, Boolean, Numeric
from sqlalchemy.orm import relationship

from app.core.database import Base

class MatchMVP(Base):
    """
    SQLAlchemy model representing an MVP (Most Valuable Player) for a match.
    """
    __tablename__ = "match_mvps"
    
    id = Column(String, primary_key=True, index=True)
    match_id = Column(String, ForeignKey("matches.id"), nullable=False)
    player_id = Column(String, ForeignKey("players.id"), nullable=False)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    
    # MVP details
    rating = Column(Numeric(3, 1), nullable=False)  # Player rating (e.g., 8.5)
    position = Column(String(50), nullable=True)     # Player position in the match
    minutes_played = Column(Integer, nullable=True)  # Minutes played in the match
    
    # Performance metrics
    goals = Column(Integer, default=0, nullable=False)
    assists = Column(Integer, default=0, nullable=False)
    saves = Column(Integer, default=0, nullable=False)
    shots = Column(Integer, default=0, nullable=False)
    shots_on_target = Column(Integer, default=0, nullable=False)
    passes = Column(Integer, default=0, nullable=False)
    pass_accuracy = Column(Float, default=0.0, nullable=False)  # Percentage
    tackles = Column(Integer, default=0, nullable=False)
    interceptions = Column(Integer, default=0, nullable=False)
    clearances = Column(Integer, default=0, nullable=False)
    
    # Additional info
    is_man_of_the_match = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)
    
    # Relationships
    match = relationship("Match", back_populates="mvps")
    player = relationship("Player", back_populates="mvp_awards")
    team = relationship("Team", back_populates="mvp_awards")
    
    def __repr__(self):
        return f"<MatchMVP(id={self.id}, match_id={self.match_id}, player_id={self.player_id})>"
    
    def to_dict(self):
        """Convert the MVP to a dictionary."""
        return {
            'id': self.id,
            'match_id': self.match_id,
            'player_id': self.player_id,
            'team_id': self.team_id,
            'rating': float(self.rating) if self.rating is not None else None,
            'position': self.position,
            'minutes_played': self.minutes_played,
            'goals': self.goals,
            'assists': self.assists,
            'saves': self.saves,
            'shots': self.shots,
            'shots_on_target': self.shots_on_target,
            'passes': self.passes,
            'pass_accuracy': self.pass_accuracy,
            'tackles': self.tackles,
            'interceptions': self.interceptions,
            'clearances': self.clearances,
            'is_man_of_the_match': self.is_man_of_the_match,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

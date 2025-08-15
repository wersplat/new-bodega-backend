"""
Tournament Group Model

This module defines the SQLAlchemy model for tournament groups in the system.
"""
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Text, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base

class TournamentGroup(Base):
    """
    SQLAlchemy model representing a group within a tournament.
    """
    __tablename__ = "tournament_groups"
    
    id = Column(String, primary_key=True, index=True)
    tournament_id = Column(String, ForeignKey("tournaments.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Group configuration
    is_knockout = Column(Boolean, default=False, nullable=False)
    is_round_robin = Column(Boolean, default=True, nullable=False)
    num_advancing = Column(Integer, default=2, nullable=False)  # Number of teams that advance
    
    # Group stage settings
    matches_per_opponent = Column(Integer, default=1, nullable=False)  # How many times teams play each other
    points_for_win = Column(Integer, default=3, nullable=False)
    points_for_draw = Column(Integer, default=1, nullable=False)
    points_for_loss = Column(Integer, default=0, nullable=False)
    
    # Tiebreaker settings
    tiebreaker1 = Column(String, default="head_to_head", nullable=False)
    tiebreaker2 = Column(String, default="map_difference", nullable=True)
    tiebreaker3 = Column(String, default="points_scored", nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)
    
    # Relationships
    tournament = relationship("Tournament", back_populates="tournament_groups")
    group_members = relationship("TournamentGroupMember", back_populates="group")
    matches = relationship("Match", back_populates="group")
    upcoming_matches = relationship("UpcomingMatch", back_populates="tournament_group")
    
    def __repr__(self):
        return f"<TournamentGroup(id={self.id}, name='{self.name}', tournament_id={self.tournament_id})>"
    
    def to_dict(self):
        """Convert the tournament group to a dictionary."""
        return {
            'id': self.id,
            'tournament_id': self.tournament_id,
            'name': self.name,
            'description': self.description,
            'is_knockout': self.is_knockout,
            'is_round_robin': self.is_round_robin,
            'num_advancing': self.num_advancing,
            'matches_per_opponent': self.matches_per_opponent,
            'points_for_win': self.points_for_win,
            'points_for_draw': self.points_for_draw,
            'points_for_loss': self.points_for_loss,
            'tiebreaker1': self.tiebreaker1,
            'tiebreaker2': self.tiebreaker2,
            'tiebreaker3': self.tiebreaker3,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

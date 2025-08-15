"""
Tournament Group Member Model

This module defines the SQLAlchemy model for tournament group members in the system.
"""
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base

class TournamentGroupMember(Base):
    """
    SQLAlchemy model representing a member (team) within a tournament group.
    """
    __tablename__ = "tournament_group_members"
    
    id = Column(String, primary_key=True, index=True)
    group_id = Column(String, ForeignKey("tournament_groups.id"), nullable=False)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    
    # Group stage stats
    matches_played = Column(Integer, default=0, nullable=False)
    matches_won = Column(Integer, default=0, nullable=False)
    matches_drawn = Column(Integer, default=0, nullable=False)
    matches_lost = Column(Integer, default=0, nullable=False)
    points = Column(Integer, default=0, nullable=False)
    
    # For tiebreakers
    points_scored = Column(Integer, default=0, nullable=False)
    points_conceded = Column(Integer, default=0, nullable=False)
    map_difference = Column(Integer, default=0, nullable=False)
    
    # Status
    is_eliminated = Column(Boolean, default=False, nullable=False)
    seed = Column(Integer, nullable=True)  # Initial seeding within the group
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)
    
    # Relationships
    group = relationship("TournamentGroup", back_populates="group_members")
    team = relationship("Team", back_populates="tournament_group_memberships")
    
    def __repr__(self):
        return f"<TournamentGroupMember(id={self.id}, group_id={self.group_id}, team_id={self.team_id})>"
    
    def to_dict(self):
        """Convert the group member to a dictionary."""
        return {
            'id': self.id,
            'group_id': self.group_id,
            'team_id': self.team_id,
            'matches_played': self.matches_played,
            'matches_won': self.matches_won,
            'matches_drawn': self.matches_drawn,
            'matches_lost': self.matches_lost,
            'points': self.points,
            'points_scored': self.points_scored,
            'points_conceded': self.points_conceded,
            'map_difference': self.map_difference,
            'is_eliminated': self.is_eliminated,
            'seed': self.seed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

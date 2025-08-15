"""
Teams Pot Tracker Model

This module defines the SQLAlchemy model for tracking team prize money in tournaments.
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class TeamsPotTracker(Base):
    """
    SQLAlchemy model representing team prize money tracking in tournaments.
    
    This model tracks the prize money earned by teams in various tournaments.
    """
    __tablename__ = 'teams_pot_tracker'
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id', onupdate='CASCADE'), nullable=True)
    placement = Column(Integer, nullable=True)
    prize_amount = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    league_id = Column(UUID(as_uuid=True), ForeignKey('leagues_info.id', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)
    tournament_id = Column(UUID(as_uuid=True), ForeignKey('tournaments.id', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)
    
    # Relationships
    team = relationship('Team', back_populates='pot_tracker_entries')
    league = relationship('LeagueInfo', back_populates='pot_tracker_entries')
    tournament = relationship('Tournament', back_populates='pot_tracker_entries')
    
    def __repr__(self):
        return f"<TeamsPotTracker(id={self.id}, team_id={self.team_id}, placement={self.placement}, prize_amount={self.prize_amount})>"
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            'id': str(self.id),
            'team_id': str(self.team_id) if self.team_id else None,
            'placement': self.placement,
            'prize_amount': self.prize_amount,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'league_id': str(self.league_id) if self.league_id else None,
            'tournament_id': str(self.tournament_id) if self.tournament_id else None
        }
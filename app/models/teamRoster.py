"""
Team Roster Model

This module defines the SQLAlchemy model for team rosters in the system.
"""

from datetime import datetime
from sqlalchemy import Column, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class TeamRoster(Base):
    """
    SQLAlchemy model representing team rosters.
    
    This model tracks the association between teams and players, including their roles
    (captain, player-coach) and the duration of their membership.
    """
    __tablename__ = 'team_rosters'
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id', ondelete='CASCADE'), nullable=True, index=True)
    player_id = Column(UUID(as_uuid=True), ForeignKey('players.id', ondelete='CASCADE'), nullable=True, index=True)
    is_captain = Column(Boolean, default=False, nullable=True)
    is_player_coach = Column(Boolean, default=False, nullable=True)
    joined_at = Column(DateTime, server_default=func.now(), nullable=True)
    left_at = Column(DateTime, nullable=True)
    league_id = Column(UUID(as_uuid=True), ForeignKey('leagues_info.id', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)
    tournament_id = Column(UUID(as_uuid=True), ForeignKey('tournaments.id', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)
    
    # Relationships
    team = relationship('Team', back_populates='roster_entries')
    player = relationship('Player', back_populates='team_roster_entries')
    league = relationship('LeagueInfo', back_populates='team_roster_entries')
    tournament = relationship('Tournament', back_populates='team_roster_entries')
    
    # Indexes
    __table_args__ = (
        Index('idx_team_rosters_team_id', 'team_id'),
        Index('idx_team_rosters_player_id', 'player_id'),
    )
    
    def __repr__(self):
        return f"<TeamRoster(id={self.id}, team_id={self.team_id}, player_id={self.player_id})>"
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            'id': str(self.id),
            'team_id': str(self.team_id) if self.team_id else None,
            'player_id': str(self.player_id) if self.player_id else None,
            'is_captain': self.is_captain,
            'is_player_coach': self.is_player_coach,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'left_at': self.left_at.isoformat() if self.left_at else None,
            'league_id': str(self.league_id) if self.league_id else None,
            'tournament_id': str(self.tournament_id) if self.tournament_id else None
        }
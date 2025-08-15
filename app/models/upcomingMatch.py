"""
Upcoming Match Model

This module defines the SQLAlchemy model for upcoming matches in the system.
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class UpcomingMatch(Base):
    """
    SQLAlchemy model representing upcoming matches.
    
    This model tracks scheduled matches that are yet to be played, including
    their participants, schedule, and related metadata.
    """
    __tablename__ = 'upcoming_matches'
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    team_a_id = Column(UUID(as_uuid=True), ForeignKey('teams.id'), nullable=True, index=True)
    team_b_id = Column(UUID(as_uuid=True), ForeignKey('teams.id'), nullable=True, index=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    stream_url = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String, server_default='scheduled', nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey('tournament_groups.id'), nullable=True, index=True)
    round = Column(Integer, nullable=True)
    match_number = Column(Integer, nullable=True)
    league_id = Column(UUID(as_uuid=True), ForeignKey('leagues_info.id', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)
    tournament_id = Column(UUID(as_uuid=True), ForeignKey('tournaments.id', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)
    
    # Relationships
    team_a = relationship('Team', foreign_keys=[team_a_id], back_populates='upcoming_matches_as_team_a')
    team_b = relationship('Team', foreign_keys=[team_b_id], back_populates='upcoming_matches_as_team_b')
    group = relationship('TournamentGroup', back_populates='upcoming_matches')
    league = relationship('LeagueInfo', back_populates='upcoming_matches')
    tournament = relationship('Tournament', back_populates='upcoming_matches')
    
    # Indexes
    __table_args__ = (
        Index('idx_upcoming_matches_scheduled_at', 'scheduled_at'),
    )
    
    def __repr__(self):
        return f"<UpcomingMatch(id={self.id}, team_a_id={self.team_a_id}, team_b_id={self.team_b_id}, scheduled_at={self.scheduled_at})>"
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            'id': str(self.id),
            'team_a_id': str(self.team_a_id) if self.team_a_id else None,
            'team_b_id': str(self.team_b_id) if self.team_b_id else None,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'stream_url': self.stream_url,
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'group_id': str(self.group_id) if self.group_id else None,
            'round': self.round,
            'match_number': self.match_number,
            'league_id': str(self.league_id) if self.league_id else None,
            'tournament_id': str(self.tournament_id) if self.tournament_id else None
        }
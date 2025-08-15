"""
Ranking Points Model

This module defines the SQLAlchemy model for tracking team ranking points in the system.
"""

from datetime import date
from sqlalchemy import Column, String, Integer, Date, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class RankingPoints(Base):
    """
    SQLAlchemy model representing ranking points awarded to teams.
    
    This model tracks points awarded to teams from various sources (matches, tournaments, etc.)
    and when those points expire.
    """
    __tablename__ = 'ranking_points'
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id'), nullable=True, index=True)
    source = Column(String, nullable=True)  # e.g., 'match', 'tournament', 'bonus', etc.
    points = Column(Integer, nullable=True)
    awarded_at = Column(Date, server_default=func.CURRENT_DATE, nullable=True)
    expires_at = Column(Date, nullable=True, index=True)
    league_id = Column(UUID(as_uuid=True), ForeignKey('leagues_info.id', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    tournament_id = Column(UUID(as_uuid=True), ForeignKey('tournaments.id', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    
    # Relationships
    team = relationship('Team', back_populates='ranking_points')
    league = relationship('LeagueInfo', back_populates='ranking_points')
    tournament = relationship('Tournament', back_populates='ranking_points')
    
    # Create index on expires_at for faster expiration queries
    __table_args__ = (
        Index('idx_rp_expire', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<RankingPoints(id={self.id}, team_id={self.team_id}, points={self.points}, source='{self.source}')>"
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            'id': str(self.id),
            'team_id': str(self.team_id) if self.team_id else None,
            'source': self.source,
            'points': self.points,
            'awarded_at': self.awarded_at.isoformat() if self.awarded_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'league_id': str(self.league_id) if self.league_id else None,
            'tournament_id': str(self.tournament_id) if self.tournament_id else None
        }
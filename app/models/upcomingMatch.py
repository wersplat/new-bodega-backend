"""
Upcoming Match Model

This module defines the SQLAlchemy model for upcoming matches.
"""
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, Text, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base

class UpcomingMatch(Base):
    """
    SQLAlchemy model representing an upcoming match.
    """
    __tablename__ = "upcoming_matches"
    
    id = Column(String, primary_key=True, index=True)
    team_a_id = Column(String, ForeignKey("teams.id"), nullable=False)
    team_b_id = Column(String, ForeignKey("teams.id"), nullable=False)
    tournament_id = Column(String, ForeignKey("tournaments.id"), nullable=True)
    league_id = Column(String, ForeignKey("leagues_info.id"), nullable=True)
    tournament_group_id = Column(String, ForeignKey("tournament_groups.id"), nullable=True)
    scheduled_time = Column(DateTime, nullable=False)
    round = Column(String, nullable=True)
    match_number = Column(Integer, nullable=True)
    status = Column(String, default="scheduled")  # scheduled, in_progress, completed, canceled
    stream_url = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    team_a = relationship("Team", foreign_keys=[team_a_id])
    team_b = relationship("Team", foreign_keys=[team_b_id])
    tournament = relationship("Tournament", back_populates="upcoming_matches")
    league = relationship("League", back_populates="upcoming_matches")
    tournament_group = relationship("TournamentGroup", back_populates="upcoming_matches")
    
    def __repr__(self):
        return f"<UpcomingMatch(id={self.id}, {self.team_a_id} vs {self.team_b_id}, scheduled={self.scheduled_time})>"
    
    def to_dict(self):
        """Convert the upcoming match to a dictionary."""
        return {
            'id': self.id,
            'team_a_id': self.team_a_id,
            'team_b_id': self.team_b_id,
            'tournament_id': self.tournament_id,
            'league_id': self.league_id,
            'tournament_group_id': self.tournament_group_id,
            'scheduled_time': self.scheduled_time.isoformat(),
            'round': self.round,
            'match_number': self.match_number,
            'status': self.status,
            'stream_url': self.stream_url,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
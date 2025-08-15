"""
Match Model

This module defines the SQLAlchemy model for matches in the system.
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Text, Boolean, Numeric, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from app.core.database import Base

class MatchStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"
    WALKOVER = "walkover"
    DEFAULTED = "defaulted"

class Match(Base):
    """
    SQLAlchemy model representing a match between two teams.
    """
    __tablename__ = "matches"
    
    id = Column(String, primary_key=True, index=True)
    tournament_id = Column(String, ForeignKey("tournaments.id"), nullable=True)
    league_id = Column(String, ForeignKey("leagues_info.id"), nullable=True)
    group_id = Column(String, ForeignKey("tournament_groups.id"), nullable=True)
    
    # Teams
    team_a_id = Column(String, ForeignKey("teams.id"), nullable=False)
    team_b_id = Column(String, ForeignKey("teams.id"), nullable=False)
    
    # Match details
    name = Column(String, nullable=True)  # Custom match name if needed
    round = Column(String, nullable=True)  # e.g., "Quarterfinals", "Group A"
    match_number = Column(Integer, nullable=True)  # Match number in the tournament
    best_of = Column(Integer, default=1, nullable=False)  # Best of X games
    
    # Status and results
    status = Column(SQLAlchemyEnum(MatchStatus), default=MatchStatus.SCHEDULED, nullable=False)
    is_forfeit = Column(Boolean, default=False, nullable=False)
    is_walkover = Column(Boolean, default=False, nullable=False)
    
    # Scores
    team_a_score = Column(Integer, default=0, nullable=False)
    team_b_score = Column(Integer, default=0, nullable=False)
    
    # Match metadata
    scheduled_time = Column(DateTime, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # Duration in seconds
    
    # Stream and VOD
    stream_url = Column(String, nullable=True)
    vod_url = Column(String, nullable=True)
    
    # Additional info
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)
    
    # Relationships
    tournament = relationship("Tournament", back_populates="matches")
    league = relationship("League", back_populates="matches")
    group = relationship("TournamentGroup", back_populates="matches")
    
    team_a = relationship("Team", foreign_keys=[team_a_id], back_populates="matches_as_team_a")
    team_b = relationship("Team", foreign_keys=[team_b_id], back_populates="matches_as_team_b")
    
    # Match stats and related data
    stats = relationship("MatchStats", back_populates="match", uselist=False)
    mvps = relationship("MatchMVP", back_populates="match")
    submissions = relationship("MatchSubmission", back_populates="match")
    
    @property
    def winner_id(self):
        """Determine the winner team ID based on scores."""
        if self.status != MatchStatus.COMPLETED:
            return None
        if self.team_a_score > self.team_b_score:
            return self.team_a_id
        elif self.team_b_score > self.team_a_score:
            return self.team_b_id
        return None  # It's a draw
    
    @property
    def loser_id(self):
        """Determine the loser team ID based on scores."""
        if self.status != MatchStatus.COMPLETED:
            return None
        if self.team_a_score < self.team_b_score:
            return self.team_a_id
        elif self.team_b_score < self.team_a_score:
            return self.team_b_id
        return None  # It's a draw
    
    @property
    def is_draw(self):
        """Check if the match ended in a draw."""
        return (
            self.status == MatchStatus.COMPLETED and 
            self.team_a_score == self.team_b_score
        )
    
    def __repr__(self):
        return f"<Match(id={self.id}, {self.team_a_id} vs {self.team_b_id}, status='{self.status}')>"
    
    def to_dict(self):
        """Convert the match to a dictionary."""
        return {
            'id': self.id,
            'tournament_id': self.tournament_id,
            'league_id': self.league_id,
            'group_id': self.group_id,
            'team_a_id': self.team_a_id,
            'team_b_id': self.team_b_id,
            'name': self.name,
            'round': self.round,
            'match_number': self.match_number,
            'best_of': self.best_of,
            'status': self.status.value if self.status else None,
            'is_forfeit': self.is_forfeit,
            'is_walkover': self.is_walkover,
            'team_a_score': self.team_a_score,
            'team_b_score': self.team_b_score,
            'winner_id': self.winner_id,
            'loser_id': self.loser_id,
            'is_draw': self.is_draw,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'stream_url': self.stream_url,
            'vod_url': self.vod_url,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

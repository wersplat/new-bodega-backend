"""
Match Submission Model

This module defines the SQLAlchemy model for match submissions in the system.
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, CheckConstraint, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ReviewStatus(str, Enum):
    """Enumeration of possible review statuses for match submissions."""
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'


class MatchSubmission(Base):
    """
    SQLAlchemy model representing match submissions.
    
    This model tracks match results submitted by teams, including their review status
    and related metadata.
    """
    __tablename__ = 'match_submissions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    match_id = Column(UUID(as_uuid=True), ForeignKey('matches.id', onupdate='CASCADE'), nullable=True)
    team_a_id = Column(UUID(as_uuid=True), ForeignKey('teams.id'), nullable=True)
    team_a_name = Column(String, ForeignKey('teams.name'), nullable=True)
    team_b_id = Column(UUID(as_uuid=True), ForeignKey('teams.id'), nullable=True)
    team_b_name = Column(String, ForeignKey('teams.name'), nullable=True)
    review_status = Column(String, nullable=True)  # Uses ReviewStatus enum
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    review_notes = Column(Text, nullable=True)
    status = Column(String, nullable=True)
    payload = Column(JSONB, nullable=True)
    tournament_id = Column(UUID(as_uuid=True), ForeignKey('tournaments.id', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)
    league_id = Column(UUID(as_uuid=True), ForeignKey('leagues_info.id', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)
    
    # Relationships
    match = relationship('Match', back_populates='submissions')
    team_a = relationship('Team', foreign_keys=[team_a_id], back_populates='submissions_as_team_a')
    team_b = relationship('Team', foreign_keys=[team_b_id], back_populates='submissions_as_team_b')
    tournament = relationship('Tournament', back_populates='match_submissions')
    league = relationship('LeagueInfo', back_populates='match_submissions')
    
    __table_args__ = (
        CheckConstraint(
            "review_status IN ('pending', 'approved', 'rejected')",
            name='match_submissions_review_status_check'
        ),
    )
    
    def __repr__(self):
        return f"<MatchSubmission(id={self.id}, match_id={self.match_id}, status='{self.review_status}')>"
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            'id': str(self.id),
            'match_id': str(self.match_id) if self.match_id else None,
            'team_a_id': str(self.team_a_id) if self.team_a_id else None,
            'team_a_name': self.team_a_name,
            'team_b_id': str(self.team_b_id) if self.team_b_id else None,
            'team_b_name': self.team_b_name,
            'review_status': self.review_status,
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'review_notes': self.review_notes,
            'status': self.status,
            'payload': self.payload,
            'tournament_id': str(self.tournament_id) if self.tournament_id else None,
            'league_id': str(self.league_id) if self.league_id else None
        }
"""
Match Submission Model

This module defines the SQLAlchemy model for match submissions.
"""
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Text, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base

class MatchSubmission(Base):
    """
    SQLAlchemy model representing a match submission.
    """
    __tablename__ = "match_submissions"
    
    id = Column(String, primary_key=True, index=True)
    match_id = Column(String, ForeignKey("matches.id"), nullable=False)
    submitting_team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    opponent_team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    tournament_id = Column(String, ForeignKey("tournaments.id"), nullable=True)
    league_id = Column(String, ForeignKey("leagues_info.id"), nullable=True)
    
    # Match details
    team_score = Column(Integer, nullable=False)
    opponent_score = Column(Integer, nullable=False)
    
    # Status and metadata
    status = Column(String, default="pending")  # pending, approved, rejected
    submitted_by = Column(String, nullable=False)  # User ID
    reviewed_by = Column(String, nullable=True)    # Admin user ID
    review_notes = Column(Text, nullable=True)
    
    # Timestamps
    submitted_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    
    # Relationships
    match = relationship("Match")
    submitting_team = relationship("Team", foreign_keys=[submitting_team_id])
    opponent_team = relationship("Team", foreign_keys=[opponent_team_id])
    tournament = relationship("Tournament", back_populates="match_submissions")
    league = relationship("League", back_populates="match_submissions")
    
    def __repr__(self):
        return f"<MatchSubmission(id={self.id}, match_id={self.match_id}, status={self.status})>"
    
    def to_dict(self):
        """Convert the match submission to a dictionary."""
        return {
            'id': self.id,
            'match_id': self.match_id,
            'submitting_team_id': self.submitting_team_id,
            'opponent_team_id': self.opponent_team_id,
            'tournament_id': self.tournament_id,
            'league_id': self.league_id,
            'team_score': self.team_score,
            'opponent_score': self.opponent_score,
            'status': self.status,
            'submitted_by': self.submitted_by,
            'reviewed_by': self.reviewed_by,
            'review_notes': self.review_notes,
            'submitted_at': self.submitted_at.isoformat(),
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None
        }
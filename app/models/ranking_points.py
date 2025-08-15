"""
Ranking Points Model

This module defines the SQLAlchemy model for tracking team ranking points.
"""
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Float
from sqlalchemy.orm import relationship

from app.core.database import Base

class RankingPoints(Base):
    """
    SQLAlchemy model representing ranking points for teams.
    """
    __tablename__ = "ranking_points"
    
    id = Column(String, primary_key=True, index=True)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    league_id = Column(String, ForeignKey("leagues_info.id"), nullable=True)
    tournament_id = Column(String, ForeignKey("tournaments.id"), nullable=True)
    points = Column(Float, default=0.0, nullable=False)
    rank = Column(Integer, nullable=True)
    last_updated = Column(DateTime, nullable=True)
    
    # Relationships
    team = relationship("Team", back_populates="ranking_points")
    league = relationship("LeagueInfo", back_populates="ranking_points")
    tournament = relationship("Tournament", back_populates="ranking_points")
    
    def __repr__(self):
        return f"<RankingPoints(id={self.id}, team_id={self.team_id}, points={self.points})>"
    
    def to_dict(self):
        """Convert the ranking points to a dictionary."""
        return {
            'id': self.id,
            'team_id': self.team_id,
            'league_id': self.league_id,
            'tournament_id': self.tournament_id,
            'points': self.points,
            'rank': self.rank,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
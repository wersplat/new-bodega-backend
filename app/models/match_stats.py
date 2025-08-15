"""
Match Stats Model

This module defines the SQLAlchemy model for match statistics in the system.
"""
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Integer, Float, DateTime, Text, Boolean, Numeric
from sqlalchemy.orm import relationship

from app.core.database import Base

class MatchStats(Base):
    """
    SQLAlchemy model representing detailed statistics for a match.
    """
    __tablename__ = "match_stats"
    
    id = Column(String, primary_key=True, index=True)
    match_id = Column(String, ForeignKey("matches.id"), nullable=False, unique=True)
    
    # Team A stats
    team_a_score = Column(Integer, default=0, nullable=False)
    team_a_possession = Column(Float, default=0.0, nullable=False)  # Percentage
    team_a_shots = Column(Integer, default=0, nullable=False)
    team_a_shots_on_target = Column(Integer, default=0, nullable=False)
    team_a_fouls = Column(Integer, default=0, nullable=False)
    team_a_yellow_cards = Column(Integer, default=0, nullable=False)
    team_a_red_cards = Column(Integer, default=0, nullable=False)
    team_a_corners = Column(Integer, default=0, nullable=False)
    team_a_offsides = Column(Integer, default=0, nullable=False)
    team_a_passes = Column(Integer, default=0, nullable=False)
    team_a_pass_accuracy = Column(Float, default=0.0, nullable=False)  # Percentage
    team_a_tackles = Column(Integer, default=0, nullable=False)
    team_a_saves = Column(Integer, default=0, nullable=False)
    
    # Team B stats
    team_b_score = Column(Integer, default=0, nullable=False)
    team_b_possession = Column(Float, default=0.0, nullable=False)  # Percentage
    team_b_shots = Column(Integer, default=0, nullable=False)
    team_b_shots_on_target = Column(Integer, default=0, nullable=False)
    team_b_fouls = Column(Integer, default=0, nullable=False)
    team_b_yellow_cards = Column(Integer, default=0, nullable=False)
    team_b_red_cards = Column(Integer, default=0, nullable=False)
    team_b_corners = Column(Integer, default=0, nullable=False)
    team_b_offsides = Column(Integer, default=0, nullable=False)
    team_b_passes = Column(Integer, default=0, nullable=False)
    team_b_pass_accuracy = Column(Float, default=0.0, nullable=False)  # Percentage
    team_b_tackles = Column(Integer, default=0, nullable=False)
    team_b_saves = Column(Integer, default=0, nullable=False)
    
    # Additional match details
    attendance = Column(Integer, nullable=True)  # Number of spectators
    stadium = Column(String, nullable=True)      # Stadium name
    weather = Column(String, nullable=True)      # Weather conditions
    
    # Metadata
    is_official = Column(Boolean, default=True, nullable=False)  # Whether stats are official
    source = Column(String, nullable=True)  # Source of the stats (e.g., 'manual', 'api', 'scout')
    notes = Column(Text, nullable=True)     # Any additional notes
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)
    
    # Relationships
    match = relationship("Match", back_populates="stats")
    
    def __repr__(self):
        return f"<MatchStats(id={self.id}, match_id={self.match_id}, score={self.team_a_score}-{self.team_b_score})>"
    
    def to_dict(self):
        """Convert the match stats to a dictionary."""
        return {
            'id': self.id,
            'match_id': self.match_id,
            
            # Team A stats
            'team_a_score': self.team_a_score,
            'team_a_possession': self.team_a_possession,
            'team_a_shots': self.team_a_shots,
            'team_a_shots_on_target': self.team_a_shots_on_target,
            'team_a_fouls': self.team_a_fouls,
            'team_a_yellow_cards': self.team_a_yellow_cards,
            'team_a_red_cards': self.team_a_red_cards,
            'team_a_corners': self.team_a_corners,
            'team_a_offsides': self.team_a_offsides,
            'team_a_passes': self.team_a_passes,
            'team_a_pass_accuracy': self.team_a_pass_accuracy,
            'team_a_tackles': self.team_a_tackles,
            'team_a_saves': self.team_a_saves,
            
            # Team B stats
            'team_b_score': self.team_b_score,
            'team_b_possession': self.team_b_possession,
            'team_b_shots': self.team_b_shots,
            'team_b_shots_on_target': self.team_b_shots_on_target,
            'team_b_fouls': self.team_b_fouls,
            'team_b_yellow_cards': self.team_b_yellow_cards,
            'team_b_red_cards': self.team_b_red_cards,
            'team_b_corners': self.team_b_corners,
            'team_b_offsides': self.team_b_offsides,
            'team_b_passes': self.team_b_passes,
            'team_b_pass_accuracy': self.team_b_pass_accuracy,
            'team_b_tackles': self.team_b_tackles,
            'team_b_saves': self.team_b_saves,
            
            # Additional details
            'attendance': self.attendance,
            'stadium': self.stadium,
            'weather': self.weather,
            'is_official': self.is_official,
            'source': self.source,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

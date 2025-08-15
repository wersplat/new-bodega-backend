"""
Player model for NBA 2K player profiles and rankings
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class PlayerPosition(enum.Enum):
    POINT_GUARD = "Point Guard"
    SHOOTING_GUARD = "Shooting Guard"
    LOCK = "Lock"
    POWER_FORWARD = "Power Forward"
    CENTER = "Center"

class SalaryTier(enum.Enum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"

class Player(Base):
    """
    SQLAlchemy model representing a player in the system.
    Matches the Supabase database schema.
    """
    __tablename__ = "players"
    
    id = Column(String, primary_key=True, index=True)
    
    # Player information
    gamertag = Column(String, nullable=False, unique=True)
    alternate_gamertag = Column(String, nullable=True)
    
    # Player details
    position = Column(Enum(PlayerPosition, name="player_position"), nullable=True)
    current_team_id = Column(String, ForeignKey("teams.id"), nullable=True)
    
    # Performance and ranking
    performance_score = Column(Float, nullable=True)
    player_rp = Column(Integer, nullable=True)
    player_rank_score = Column(Float, nullable=True)
    salary_tier = Column(Enum(SalaryTier, name="salary_tier"), nullable=True)
    monthly_value = Column(Integer, nullable=True)
    is_rookie = Column(Boolean, nullable=True)
    
    # Social media and contact
    discord_id = Column(String, nullable=True)
    twitter_id = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=True)
    
    # Relationships
    current_team = relationship("Team", foreign_keys=[current_team_id])
    player_stats = relationship("PlayerStats", back_populates="player")
    team_rosters = relationship("TeamRoster", back_populates="player")
    player_rp_transactions = relationship("PlayerRPTransaction", back_populates="player")
    awards_race = relationship("AwardsRace", back_populates="player")
    match_mvp = relationship("MatchMVP", back_populates="player")
    
    def __repr__(self):
        return f"<Player(id={self.id}, gamertag='{self.gamertag}')>"
    
    def to_dict(self):
        """Convert the player to a dictionary."""
        return {
            'id': self.id,
            'gamertag': self.gamertag,
            'alternate_gamertag': self.alternate_gamertag,
            'position': self.position.value if self.position else None,
            'current_team_id': self.current_team_id,
            'performance_score': self.performance_score,
            'player_rp': self.player_rp,
            'player_rank_score': self.player_rank_score,
            'salary_tier': self.salary_tier.value if self.salary_tier else None,
            'monthly_value': self.monthly_value,
            'is_rookie': self.is_rookie,
            'discord_id': self.discord_id,
            'twitter_id': self.twitter_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PlayerStats(Base):
    """
    SQLAlchemy model representing player statistics for matches.
    Matches the Supabase database schema.
    """
    __tablename__ = "player_stats"
    
    id = Column(String, primary_key=True, index=True)
    player_id = Column(String, ForeignKey("players.id"), nullable=False)
    match_id = Column(String, ForeignKey("matches.id"), nullable=False)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    
    # Basic stats
    points = Column(Integer, nullable=True)
    assists = Column(Integer, nullable=True)
    rebounds = Column(Integer, nullable=True)
    steals = Column(Integer, nullable=True)
    blocks = Column(Integer, nullable=True)
    turnovers = Column(Integer, nullable=True)
    fouls = Column(Integer, nullable=True)
    plus_minus = Column(Integer, nullable=True)
    
    # Shooting stats
    fgm = Column(Integer, default=0)  # Field Goals Made
    fga = Column(Integer, nullable=True)  # Field Goals Attempted
    three_points_made = Column(Integer, default=0)
    three_points_attempted = Column(Integer, default=0)
    ftm = Column(Integer, default=0)  # Free Throws Made
    fta = Column(Integer, default=0)  # Free Throws Attempted
    
    # Computed stats
    ps = Column(Float, nullable=True)  # Performance score (computed)
    player_name = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    player = relationship("Player", back_populates="player_stats")
    match = relationship("Match")
    team = relationship("Team")
    
    def __repr__(self):
        return f"<PlayerStats(id={self.id}, player_id='{self.player_id}', points={self.points})>"

class MatchMVP(Base):
    """
    SQLAlchemy model representing MVP players for matches.
    Matches the Supabase database schema.
    """
    __tablename__ = "match_mvp"
    
    match_id = Column(String, ForeignKey("matches.id"), primary_key=True)
    player_id = Column(String, ForeignKey("players.id"), nullable=False)
    
    # Relationships
    match = relationship("Match")
    player = relationship("Player", back_populates="match_mvp")
    
    def __repr__(self):
        return f"<MatchMVP(match_id='{self.match_id}', player_id='{self.player_id}')>" 
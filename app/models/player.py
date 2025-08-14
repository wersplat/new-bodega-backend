"""
Player model for NBA 2K player profiles and rankings
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
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
    __tablename__ = "players"
    
    id = Column(String, primary_key=True, index=True)
    gamertag = Column(String, unique=True, nullable=False)
    position = Column(Enum(PlayerPosition, name="player_position"))
    current_team_id = Column(String, ForeignKey("teams.id"))
    performance_score = Column(Float, default=0.0)
    player_rp = Column(Integer, default=0)
    player_rank_score = Column(Float, default=0.0)
    salary_tier = Column(Enum(SalaryTier, name="salary_tier"))
    monthly_value = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    is_rookie = Column(Boolean)
    discord_id = Column(String, unique=True)
    twitter_id = Column(String, unique=True)
    alternate_gamertag = Column(String)
    
    # Relationships
    current_team = relationship("Team", foreign_keys=[current_team_id])
    player_stats = relationship("PlayerStats", back_populates="player")
    draft_pool = relationship("DraftPool", back_populates="player")
    team_rosters = relationship("TeamRoster", back_populates="player")
    player_rp_transactions = relationship("PlayerRPTransaction", back_populates="player")
    awards_race = relationship("AwardsRace", back_populates="player")
    match_mvp = relationship("MatchMVP", back_populates="player")
    
    def __repr__(self):
        return f"<Player(id={self.id}, gamertag='{self.gamertag}', rp={self.player_rp})>"

class PlayerStats(Base):
    __tablename__ = "player_stats"
    
    id = Column(String, primary_key=True, index=True)
    player_id = Column(String, ForeignKey("players.id"), nullable=False)
    match_id = Column(String, ForeignKey("matches.id"), nullable=False)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    points = Column(Integer)
    assists = Column(Integer)
    rebounds = Column(Integer)
    steals = Column(Integer)
    blocks = Column(Integer)
    turnovers = Column(Integer)
    fouls = Column(Integer)
    ps = Column(Float)  # Performance score (computed)
    created_at = Column(DateTime, server_default=func.now())
    fgm = Column(Integer, default=0)  # Field Goals Made
    fga = Column(Integer)  # Field Goals Attempted
    three_points_made = Column(Integer, default=0)
    three_points_attempted = Column(Integer, default=0)
    ftm = Column(Integer, default=0)  # Free Throws Made
    fta = Column(Integer, default=0)  # Free Throws Attempted
    plus_minus = Column(Integer)
    player_name = Column(String)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="player_stats")
    match = relationship("Match")
    team = relationship("Team")
    
    def __repr__(self):
        return f"<PlayerStats(id={self.id}, player_id='{self.player_id}', points={self.points})>"

class MatchMVP(Base):
    __tablename__ = "match_mvp"
    
    match_id = Column(String, ForeignKey("matches.id"), primary_key=True)
    player_id = Column(String, ForeignKey("players.id"), nullable=False)
    
    # Relationships
    match = relationship("Match")
    player = relationship("Player", back_populates="match_mvp")
    
    def __repr__(self):
        return f"<MatchMVP(match_id='{self.match_id}', player_id='{self.player_id}')>" 
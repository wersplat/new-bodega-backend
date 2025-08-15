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
    """
    SQLAlchemy model representing a player in the system.
    """
    __tablename__ = "players"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # Link to auth user if applicable
    
    # Player information
    display_name = Column(String, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True, index=True)
    phone_number = Column(String, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    country = Column(String, nullable=True)
    state = Column(String, nullable=True)
    city = Column(String, nullable=True)
    
    # Player details
    bio = Column(Text, nullable=True)
    profile_image_url = Column(String, nullable=True)
    banner_image_url = Column(String, nullable=True)
    
    # Social media links
    twitter_handle = Column(String, nullable=True)
    twitch_username = Column(String, nullable=True)
    youtube_channel = Column(String, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    
    # Player information
    gamertag = Column(String, unique=True, nullable=False)
    position = Column(Enum(PlayerPosition, name="player_position"))
    current_team_id = Column(String, ForeignKey("teams.id"))
    performance_score = Column(Float, default=0.0)
    player_rp = Column(Integer, default=0)
    player_rank_score = Column(Float, default=0.0)
    salary_tier = Column(Enum(SalaryTier, name="salary_tier"))
    monthly_value = Column(Integer, default=0)
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
    team_players = relationship("TeamPlayer", back_populates="player")
    rp_transactions = relationship("PlayerRPTransaction", back_populates="player")
    
    def __repr__(self):
        return f"<Player(id={self.id}, display_name='{self.display_name}')>"
    
    def to_dict(self):
        """Convert the player to a dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'display_name': self.display_name,
            'full_name': self.full_name,
            'email': self.email,
            'phone_number': self.phone_number,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'country': self.country,
            'state': self.state,
            'city': self.city,
            'bio': self.bio,
            'profile_image_url': self.profile_image_url,
            'banner_image_url': self.banner_image_url,
            'twitter_handle': self.twitter_handle,
            'twitch_username': self.twitch_username,
            'youtube_channel': self.youtube_channel,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'gamertag': self.gamertag,
            'position': self.position,
            'current_team_id': self.current_team_id,
            'performance_score': self.performance_score,
            'player_rp': self.player_rp,
            'player_rank_score': self.player_rank_score,
            'salary_tier': self.salary_tier,
            'monthly_value': self.monthly_value,
            'is_rookie': self.is_rookie,
            'discord_id': self.discord_id,
            'twitter_id': self.twitter_id,
            'alternate_gamertag': self.alternate_gamertag
        }

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
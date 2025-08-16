"""
Pydantic schemas for player profiles and rankings
"""

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from typing import Optional, List, ClassVar, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID

class PlayerPosition(str, Enum):
    POINT_GUARD = "Point Guard"
    SHOOTING_GUARD = "Shooting Guard"
    LOCK = "Lock"
    POWER_FORWARD = "Power Forward"
    CENTER = "Center"

class SalaryTier(str, Enum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"

class LeaderboardTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    PINK_DIAMOND = "pink_diamond"
    GALAXY_OPAL = "galaxy_opal"

class PlayerBase(BaseModel):
    gamertag: str = Field(..., min_length=1, max_length=100)
    alternate_gamertag: Optional[str] = Field(None, max_length=100)
    position: Optional[PlayerPosition] = None
    current_team_id: Optional[str] = Field(None, description="Team ID as string")
    performance_score: Optional[float] = Field(default=None, ge=0.0)
    player_rp: Optional[int] = Field(default=0, ge=0)  # Aligned with schema
    player_rank_score: Optional[float] = Field(default=0.0, ge=0.0)
    salary_tier: Optional[SalaryTier] = None
    monthly_value: Optional[int] = Field(default=None, ge=0)
    is_rookie: Optional[bool] = Field(default=False)
    discord_id: Optional[str] = None
    twitter_id: Optional[str] = None

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(BaseModel):
    gamertag: Optional[str] = None
    alternate_gamertag: Optional[str] = None
    position: Optional[PlayerPosition] = None
    current_team_id: Optional[str] = None
    performance_score: Optional[float] = Field(None, ge=0.0)
    player_rp: Optional[int] = Field(None, ge=0)
    player_rank_score: Optional[float] = Field(None, ge=0.0)
    salary_tier: Optional[SalaryTier] = None
    monthly_value: Optional[int] = Field(None, ge=0)
    is_rookie: Optional[bool] = None
    discord_id: Optional[str] = None
    twitter_id: Optional[str] = None

class PlayerInDB(PlayerBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    created_at: Optional[datetime] = None

class Player(PlayerInDB):
    pass

class PlayerProfile(Player):
    """Extended player profile with team info"""
    team_name: Optional[str] = None
    team_logo_url: Optional[str] = None

class PlayerWithStats(Player):
    """Player with detailed statistics"""
    avg_points: Optional[float] = None
    avg_assists: Optional[float] = None
    avg_rebounds: Optional[float] = None
    avg_steals: Optional[float] = None
    avg_blocks: Optional[float] = None
    games_played: Optional[int] = None

class PlayerWithTeam(Player):
    """Player with team information"""
    team: Optional[Dict[str, Any]] = None

class RPHistory(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    player_id: str
    amount: int
    type: str
    description: str
    created_at: datetime
    league_id: Optional[str] = None
    match_id: Optional[str] = None
    tournament_id: Optional[str] = None

class PlayerWithHistory(Player):
    """Player with RP history"""
    rp_history: List[RPHistory] = []

class PlayerListResponse(BaseModel):
    """Paginated list of players"""
    items: List[Player]
    total: int
    page: int
    size: int
    has_more: bool 
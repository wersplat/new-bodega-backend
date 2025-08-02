"""
Pydantic schemas for player profiles and rankings
"""

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from typing import Optional, List, ClassVar, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID

class PlayerTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    PINK_DIAMOND = "pink_diamond"
    GALAXY_OPAL = "galaxy_opal"

class PlayerBase(BaseModel):
    gamertag: str = Field(..., min_length=1, max_length=100)
    platform: str = Field(..., min_length=1, max_length=50)
    team_name: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)

class PlayerCreate(PlayerBase):
    user_id: int = Field(..., gt=0, description="User ID must be a positive integer")

class PlayerUpdate(BaseModel):
    gamertag: Optional[str] = None
    platform: Optional[str] = None
    team_name: Optional[str] = None
    region: Optional[str] = None
    bio: Optional[str] = None

class PlayerInDB(PlayerBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    gamertag: str
    position: Optional[str] = None
    region_id: Optional[int] = None
    current_team_id: Optional[int] = None
    performance_score: Optional[float] = Field(default=None, ge=0.0)
    player_rp: float = Field(ge=0.0)  # Renamed from current_rp to match Supabase
    player_rank_score: float = Field(ge=0.0)  # Using this as peak_rp equivalent
    salary_tier: Optional[int] = None
    monthly_value: Optional[float] = None
    is_rookie: bool = False
    discord_id: Optional[str] = None
    twitter_id: Optional[str] = None
    alternate_gamertag: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class Player(PlayerInDB):
    pass

class PlayerProfile(Player):
    """Extended player profile with user info"""
    username: str
    full_name: Optional[str] = None
    discord_id: Optional[str] = None
    twitter_id: Optional[str] = None
    alternate_gamertag: Optional[str] = None
    position: Optional[str] = None
    region_id: Optional[int] = None
    current_team_id: Optional[int] = None
    performance_score: Optional[float] = None
    salary_tier: Optional[int] = None
    monthly_value: Optional[float] = None
    is_rookie: bool = False

class RPHistory(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    player_id: int
    old_rp: float = Field(ge=0.0)
    new_rp: float = Field(ge=0.0)
    change_reason: Optional[str] = None
    event_id: Optional[int] = None
    created_at: datetime

class PlayerWithHistory(Player):
    """Player with RP history"""
    rp_history: List[RPHistory] = [] 
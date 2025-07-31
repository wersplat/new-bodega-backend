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
    gamertag: str
    platform: str
    team_name: Optional[str] = None
    region: Optional[str] = None
    bio: Optional[str] = None

class PlayerCreate(PlayerBase):
    user_id: int

class PlayerUpdate(BaseModel):
    gamertag: Optional[str] = None
    platform: Optional[str] = None
    team_name: Optional[str] = None
    region: Optional[str] = None
    bio: Optional[str] = None

class PlayerInDB(PlayerBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    current_rp: float = Field(ge=0.0)
    peak_rp: float = Field(ge=0.0)
    tier: PlayerTier
    is_verified: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

class Player(PlayerInDB):
    pass

class PlayerProfile(Player):
    """Extended player profile with user info"""
    username: str
    full_name: Optional[str] = None
    discord_id: Optional[str] = None

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
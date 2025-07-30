"""
Pydantic schemas for player profiles and rankings
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

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
    id: int
    user_id: int
    current_rp: float
    peak_rp: float
    tier: PlayerTier
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Player(PlayerInDB):
    pass

class PlayerProfile(Player):
    """Extended player profile with user info"""
    username: str
    full_name: Optional[str] = None
    discord_id: Optional[str] = None

class RPHistory(BaseModel):
    id: int
    player_id: int
    old_rp: float
    new_rp: float
    change_reason: Optional[str] = None
    event_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class PlayerWithHistory(Player):
    """Player with RP history"""
    rp_history: List[RPHistory] = [] 
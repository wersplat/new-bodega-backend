"""
Pydantic schemas for player badges
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class PlayerBadgeBase(BaseModel):
    badge_type: str = Field(..., description="Type of badge")
    player_wallet: str = Field(..., description="Player's wallet address")
    match_id: int = Field(..., ge=1, description="Match ID where badge was earned")
    ipfs_uri: Optional[str] = None
    token_id: Optional[int] = Field(None, ge=0)
    tx_hash: Optional[str] = None
    league_id: Optional[str] = None
    tournament_id: Optional[str] = None

class PlayerBadgeCreate(PlayerBadgeBase):
    pass

class PlayerBadgeUpdate(BaseModel):
    badge_type: Optional[str] = None
    ipfs_uri: Optional[str] = None
    token_id: Optional[int] = Field(None, ge=0)
    tx_hash: Optional[str] = None
    league_id: Optional[str] = None
    tournament_id: Optional[str] = None

class PlayerBadge(PlayerBadgeBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    created_at: datetime

class PlayerBadgeWithDetails(PlayerBadge):
    """Badge with player and match details"""
    player: Optional[Dict[str, Any]] = None
    match: Optional[Dict[str, Any]] = None
    tournament: Optional[Dict[str, Any]] = None
    league: Optional[Dict[str, Any]] = None 
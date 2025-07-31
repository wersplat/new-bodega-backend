"""
Pydantic schemas for badges and achievements
"""

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from typing import Optional, List, ClassVar, Dict, Any
from datetime import datetime
from uuid import UUID

class BadgeBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    rarity: str = "common"

class BadgeCreate(BadgeBase):
    pass

class BadgeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    rarity: Optional[str] = None
    is_active: Optional[bool] = None

class BadgeInDB(BadgeBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    created_at: datetime

class Badge(BadgeInDB):
    pass

class PlayerBadgeBase(BaseModel):
    player_id: int
    badge_id: int
    is_equipped: bool = False

class PlayerBadgeCreate(PlayerBadgeBase):
    awarded_by: Optional[int] = None

class PlayerBadgeInDB(PlayerBadgeBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    awarded_by: Optional[int] = None
    awarded_at: datetime

class PlayerBadge(PlayerBadgeInDB):
    pass

class PlayerBadgeWithDetails(PlayerBadge):
    """Player badge with badge details"""
    badge: Badge 
"""
Pydantic schemas for awards and achievements
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID

class AwardTypes(str, Enum):
    OFFENSIVE_MVP = "Offensive MVP"
    DEFENSIVE_MVP = "Defensive MVP"
    ROOKIE_OF_TOURNAMENT = "Rookie of Tournament"

class AwardsRaceBase(BaseModel):
    award_type: Optional[AwardTypes] = None
    award_winner: Optional[bool] = None
    rank: Optional[int] = Field(None, ge=1)
    rp_bonus: Optional[int] = Field(None, ge=0)
    team_id: str
    player_id: Optional[str] = None
    league_id: Optional[str] = None
    tournament_id: Optional[str] = None

class AwardsRaceCreate(AwardsRaceBase):
    pass

class AwardsRaceUpdate(BaseModel):
    award_type: Optional[AwardTypes] = None
    award_winner: Optional[bool] = None
    rank: Optional[int] = Field(None, ge=1)
    rp_bonus: Optional[int] = Field(None, ge=0)
    player_id: Optional[str] = None
    league_id: Optional[str] = None
    tournament_id: Optional[str] = None

class AwardsRace(AwardsRaceBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    created_at: datetime

class AwardsRaceWithDetails(AwardsRace):
    """Awards race with player and team details"""
    player: Optional[Dict[str, Any]] = None
    team: Optional[Dict[str, Any]] = None
    tournament: Optional[Dict[str, Any]] = None
    league: Optional[Dict[str, Any]] = None

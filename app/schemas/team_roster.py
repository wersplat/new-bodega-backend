"""
Pydantic schemas for team rosters
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class TeamRosterBase(BaseModel):
    team_id: str
    player_id: Optional[str] = None
    is_captain: Optional[bool] = Field(default=False)
    is_player_coach: Optional[bool] = Field(default=False)
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None
    league_id: Optional[str] = None
    tournament_id: Optional[str] = None

class TeamRosterCreate(TeamRosterBase):
    pass

class TeamRosterUpdate(BaseModel):
    is_captain: Optional[bool] = None
    is_player_coach: Optional[bool] = None
    left_at: Optional[datetime] = None
    league_id: Optional[str] = None
    tournament_id: Optional[str] = None

class TeamRoster(TeamRosterBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str

class TeamRosterWithDetails(TeamRoster):
    """Team roster with player and team details"""
    player: Optional[Dict[str, Any]] = None
    team: Optional[Dict[str, Any]] = None
    league: Optional[Dict[str, Any]] = None
    tournament: Optional[Dict[str, Any]] = None

"""
Pydantic schemas for team roster data
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID

from .player import PlayerPosition, SalaryTier

class TeamRosterBase(BaseModel):
    player_id: Optional[str] = Field(None, description="Player ID as string")
    team_id: Optional[str] = Field(None, description="Team ID as string")
    is_captain: Optional[bool] = Field(None, description="Whether the player is team captain")
    is_player_coach: Optional[bool] = Field(None, description="Whether the player is also a coach")
    joined_at: Optional[datetime] = Field(None, description="When the player joined the team")

class TeamRosterCreate(TeamRosterBase):
    pass

class TeamRosterUpdate(BaseModel):
    is_captain: Optional[bool] = None
    is_player_coach: Optional[bool] = None

class TeamRoster(TeamRosterBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str

class TeamRosterWithDetails(TeamRoster):
    """Team roster with player and team details"""
    player: Optional[Dict[str, Any]] = None
    team: Optional[Dict[str, Any]] = None

# Schema for team_roster_current view
class TeamRosterCurrent(BaseModel):
    """Schema for team_roster_current view"""
    model_config = ConfigDict(from_attributes=True)
    
    gamertag: Optional[str] = Field(None, description="Player gamertag")
    is_captain: Optional[bool] = Field(None, description="Whether the player is team captain")
    is_player_coach: Optional[bool] = Field(None, description="Whether the player is also a coach")
    joined_at: Optional[datetime] = Field(None, description="When the player joined the team")
    monthly_value: Optional[int] = Field(None, description="Player's monthly salary value")
    player_id: Optional[str] = Field(None, description="Player ID as string")
    position: Optional[PlayerPosition] = Field(None, description="Player position")
    salary_tier: Optional[SalaryTier] = Field(None, description="Player salary tier")
    team_id: Optional[str] = Field(None, description="Team ID as string")
    team_name: Optional[str] = Field(None, description="Team name")

class TeamRosterCurrentList(BaseModel):
    """Paginated list of team roster current entries"""
    items: List[TeamRosterCurrent] = Field(..., description="List of team roster entries")
    total: int = Field(..., description="Total number of entries")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    has_more: bool = Field(..., description="Whether there are more items available")

class TeamRosterCurrentByTeam(BaseModel):
    """Team roster current entries grouped by team"""
    team_id: str = Field(..., description="Team ID")
    team_name: str = Field(..., description="Team name")
    players: List[TeamRosterCurrent] = Field(..., description="List of players on the team")
    total_players: int = Field(..., description="Total number of players")
    captains: List[TeamRosterCurrent] = Field(..., description="List of team captains")
    coaches: List[TeamRosterCurrent] = Field(..., description="List of player coaches")

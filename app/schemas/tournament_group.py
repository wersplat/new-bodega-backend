"""
Pydantic schemas for tournament groups
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class TournamentGroupBase(BaseModel):
    name: str = Field(..., description="Group name")
    description: Optional[str] = None
    max_teams: Optional[int] = Field(None, ge=1)
    advancement_count: Optional[int] = Field(None, ge=1)
    sort_order: Optional[int] = Field(None, ge=0)
    status: Optional[str] = None
    league_season_id: Optional[str] = None
    tournament_id: Optional[str] = None

class TournamentGroupCreate(TournamentGroupBase):
    pass

class TournamentGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    max_teams: Optional[int] = Field(None, ge=1)
    advancement_count: Optional[int] = Field(None, ge=1)
    sort_order: Optional[int] = Field(None, ge=0)
    status: Optional[str] = None
    league_season_id: Optional[str] = None
    tournament_id: Optional[str] = None

class TournamentGroup(TournamentGroupBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TournamentGroupWithTeams(TournamentGroup):
    """Tournament group with team members"""
    teams: List[Dict[str, Any]] = []

class TournamentGroupMemberBase(BaseModel):
    group_id: str
    team_id: str
    seed: Optional[int] = Field(None, ge=1)

class TournamentGroupMemberCreate(TournamentGroupMemberBase):
    pass

class TournamentGroupMember(TournamentGroupMemberBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    created_at: Optional[datetime] = None

class TournamentGroupMemberWithDetails(TournamentGroupMember):
    """Group member with team details"""
    team: Optional[Dict[str, Any]] = None
    group: Optional[Dict[str, Any]] = None

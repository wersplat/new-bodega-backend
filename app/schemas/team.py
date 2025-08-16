"""
Pydantic schemas for teams
"""

from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class TeamBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    logo_url: Optional[str] = None
    current_rp: Optional[int] = Field(default=0, ge=0)
    elo_rating: Optional[float] = Field(default=1500.0)
    global_rank: Optional[int] = Field(default=None, ge=1)
    leaderboard_tier: Optional[str] = None
    player_rank_score: Optional[float] = Field(default=0.0, ge=0.0)
    money_won: Optional[int] = Field(default=0, ge=0)

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    logo_url: Optional[str] = None
    current_rp: Optional[int] = Field(None, ge=0)
    elo_rating: Optional[float] = Field(None)
    global_rank: Optional[int] = Field(None, ge=1)
    leaderboard_tier: Optional[str] = None
    player_rank_score: Optional[float] = Field(None, ge=0.0)
    money_won: Optional[int] = Field(None, ge=0)

class TeamInDB(TeamBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    created_at: Optional[datetime] = None

class Team(TeamInDB):
    pass

class TeamWithPlayers(Team):
    """Team with roster information"""
    players: List[Dict[str, Any]] = []

class TeamWithStats(Team):
    """Team with match statistics"""
    total_matches: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    win_rate: Optional[float] = None

class TeamListResponse(BaseModel):
    """Paginated list of teams"""
    items: List[Team]
    total: int
    page: int
    size: int
    has_more: bool

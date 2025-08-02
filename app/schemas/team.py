"""
Pydantic schemas for teams
"""

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_serializer
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID

# Leaderboard tier is calculated by update_team_rankings function
# and is a string value like 'T1', 'T2', etc.

class TeamBase(BaseModel):
    """Base team schema with required fields"""
    name: str = Field(..., min_length=1, max_length=100)
    logo_url: Optional[HttpUrl] = None
    region_id: Optional[UUID] = None

class TeamCreate(TeamBase):
    """Schema for creating a new team"""
    pass

class TeamUpdate(BaseModel):
    """Schema for updating a team"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    logo_url: Optional[HttpUrl] = None
    region_id: Optional[UUID] = None
    current_rp: Optional[float] = Field(None, ge=0.0)
    elo_rating: Optional[float] = Field(None, ge=0.0)
    global_rank: Optional[int] = Field(None, ge=1)
    leaderboard_tier: Optional[str] = None
    money_won: Optional[float] = Field(None, ge=0.0)

class TeamInDB(TeamBase):
    """Team schema as stored in the database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    current_rp: float = Field(default=0.0, ge=0.0)
    elo_rating: float = Field(default=1000.0, ge=0.0)
    global_rank: Optional[int] = Field(None, ge=1)
    leaderboard_tier: str = "T1"
    created_at: datetime
    player_rank_score: float = Field(default=0.0, ge=0.0)
    money_won: float = Field(default=0.0, ge=0.0)
    
    @field_serializer('logo_url')
    def serialize_logo_url(self, logo_url: Optional[HttpUrl], _info) -> Optional[str]:
        return str(logo_url) if logo_url else None

class Team(TeamInDB):
    """Public-facing team schema"""
    pass

class TeamWithPlayers(Team):
    """Team schema with player information"""
    players: List[Dict[str, Any]] = []

class TeamWithStats(Team):
    """Team schema with additional statistics"""
    total_wins: int = 0
    total_losses: int = 0
    win_percentage: float = 0.0
    current_streak: int = 0
    
    @property
    def total_games(self) -> int:
        return self.total_wins + self.total_losses

class TeamStanding(Team):
    """Team standings with ranking information"""
    rank: int
    previous_rank: Optional[int] = None
    rp_change: Optional[float] = None
    event_wins: int = 0
    event_top3: int = 0
    event_top5: int = 0

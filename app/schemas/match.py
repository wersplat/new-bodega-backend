"""
Pydantic schemas for matches and game results
"""

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_serializer, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID

class MatchStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"

class MatchStage(str, Enum):
    GROUP = "group"
    ROUND_OF_32 = "round_of_32"
    ROUND_OF_16 = "round_of_16"
    QUARTERFINALS = "quarterfinals"
    SEMIFINALS = "semifinals"
    FINALS = "finals"
    THIRD_PLACE = "third_place"
    EXHIBITION = "exhibition"

class MatchBase(BaseModel):
    """Base match schema with required fields"""
    event_id: UUID
    team_a_id: UUID
    team_b_id: UUID
    stage: MatchStage = MatchStage.GROUP
    game_number: int = Field(1, ge=1)
    scheduled_at: Optional[datetime] = None

class MatchCreate(MatchBase):
    """Schema for creating a new match"""
    team_a_name: str
    team_b_name: str
    
    @model_validator(mode='after')
    def validate_teams_different(self) -> 'MatchCreate':
        if self.team_a_id == self.team_b_id:
            raise ValueError("team_a_id and team_b_id must be different")
        return self

class MatchUpdate(BaseModel):
    """Schema for updating a match"""
    status: Optional[MatchStatus] = None
    score_a: Optional[int] = Field(None, ge=0)
    score_b: Optional[int] = Field(None, ge=0)
    winner_id: Optional[UUID] = None
    played_at: Optional[datetime] = None
    boxscore_url: Optional[HttpUrl] = None
    stage: Optional[MatchStage] = None
    game_number: Optional[int] = Field(None, ge=1)

class MatchInDB(MatchBase):
    """Match schema as stored in the database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    status: MatchStatus = MatchStatus.SCHEDULED
    score_a: Optional[int] = Field(None, ge=0)
    score_b: Optional[int] = Field(None, ge=0)
    winner_id: Optional[UUID] = None
    played_at: Optional[datetime] = None
    boxscore_url: Optional[HttpUrl] = None
    team_a_name: str
    team_b_name: str
    winner_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_serializer('boxscore_url')
    def serialize_boxscore_url(self, url: Optional[HttpUrl], _info) -> Optional[str]:
        return str(url) if url else None

class Match(MatchInDB):
    """Public-facing match schema"""
    pass

class MatchWithTeams(Match):
    """Match schema with team information"""
    team_a: Optional[Dict[str, Any]] = None
    team_b: Optional[Dict[str, Any]] = None
    winner: Optional[Dict[str, Any]] = None

class MatchWithDetails(MatchWithTeams):
    """Match schema with team and player details"""
    team_a_players: List[Dict[str, Any]] = []
    team_b_players: List[Dict[str, Any]] = []
    event: Optional[Dict[str, Any]] = None

class MatchResult(BaseModel):
    """Schema for submitting match results"""
    score_a: int = Field(..., ge=0)
    score_b: int = Field(..., ge=0)
    winner_id: UUID
    boxscore_url: Optional[HttpUrl] = None
    
    @field_serializer('boxscore_url')
    def serialize_boxscore_url(self, url: Optional[HttpUrl], _info) -> Optional[str]:
        return str(url) if url else None

class PlayerMatchStats(BaseModel):
    """Schema for player statistics in a match"""
    player_id: UUID
    team_id: UUID
    points: int = Field(0, ge=0)
    assists: int = Field(0, ge=0)
    rebounds: int = Field(0, ge=0)
    steals: int = Field(0, ge=0)
    blocks: int = Field(0, ge=0)
    turnovers: int = Field(0, ge=0)
    fouls: int = Field(0, ge=0)
    fgm: int = Field(0, ge=0)  # Field goals made
    fga: int = Field(0, ge=0)  # Field goals attempted
    three_points_made: int = Field(0, ge=0)
    three_points_attempted: int = Field(0, ge=0)
    ftm: int = Field(0, ge=0)  # Free throws made
    fta: int = Field(0, ge=0)  # Free throws attempted
    plus_minus: int = 0
    minutes_played: int = Field(0, ge=0, le=48)  # Max 48 minutes in a game

class MatchStats(BaseModel):
    """Schema for match statistics submission"""
    match_id: UUID
    stats: List[PlayerMatchStats]

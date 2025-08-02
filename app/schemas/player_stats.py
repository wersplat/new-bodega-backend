"""
Pydantic schemas for player statistics
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, computed_field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class PlayerStatsBase(BaseModel):
    """Base schema for player statistics"""
    player_id: UUID
    match_id: UUID
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
    minutes_played: int = Field(0, ge=0, le=48)  # 48 minutes in a game
    ps: Optional[float] = Field(None, ge=0.0)  # Performance score (optional)

    @model_validator(mode='after')
    def validate_stats(self) -> 'PlayerStatsBase':
        if self.fga < self.fgm:
            raise ValueError('Field goals attempted must be >= field goals made')
        if self.three_points_attempted < self.three_points_made:
            raise ValueError('3-point attempts must be >= 3-pointers made')
        if self.fta < self.ftm:
            raise ValueError('Free throw attempts must be >= free throws made')
        return self

class PlayerStatsCreate(PlayerStatsBase):
    """Schema for creating new player statistics"""
    player_name: Optional[str] = None  # For easier reference

class PlayerStatsUpdate(BaseModel):
    """Schema for updating player statistics"""
    points: Optional[int] = Field(None, ge=0)
    assists: Optional[int] = Field(None, ge=0)
    rebounds: Optional[int] = Field(None, ge=0)
    steals: Optional[int] = Field(None, ge=0)
    blocks: Optional[int] = Field(None, ge=0)
    turnovers: Optional[int] = Field(None, ge=0)
    fouls: Optional[int] = Field(None, ge=0)
    fgm: Optional[int] = Field(None, ge=0)
    fga: Optional[int] = Field(None, ge=0)
    three_points_made: Optional[int] = Field(None, ge=0)
    three_points_attempted: Optional[int] = Field(None, ge=0)
    ftm: Optional[int] = Field(None, ge=0)
    fta: Optional[int] = Field(None, ge=0)
    plus_minus: Optional[int] = None
    minutes_played: Optional[int] = Field(None, ge=0, le=48)
    ps: Optional[float] = Field(None, ge=0.0)

class PlayerStatsInDB(PlayerStatsBase):
    """Player statistics as stored in the database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    player_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class PlayerGameAverages(BaseModel):
    """Schema for player's average statistics per game"""
    games_played: int = 0
    points: float = 0.0
    assists: float = 0.0
    rebounds: float = 0.0
    steals: float = 0.0
    blocks: float = 0.0
    turnovers: float = 0.0
    field_goal_pct: float = 0.0
    three_point_pct: float = 0.0
    free_throw_pct: float = 0.0
    minutes_per_game: float = 0.0
    plus_minus: float = 0.0
    double_doubles: int = 0
    triple_doubles: int = 0

class PlayerSeasonStats(BaseModel):
    """Schema for player's season statistics with computed averages"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Player and team info
    player_id: UUID
    player_name: str
    team_id: UUID
    team_name: str
    
    # Season totals
    games_played: int = 0
    games_started: int = 0
    minutes_played: int = 0
    total_points: int = 0
    total_rebounds: int = 0
    total_assists: int = 0
    total_steals: int = 0
    total_blocks: int = 0
    total_turnovers: int = 0
    total_fgm: int = 0
    total_fga: int = 0
    total_3pm: int = 0
    total_3pa: int = 0
    total_ftm: int = 0
    total_fta: int = 0
    total_plus_minus: int = 0
    double_doubles: int = 0
    triple_doubles: int = 0
    
    # Computed properties for per-game averages
    @computed_field
    def points_per_game(self) -> float:
        return self.total_points / self.games_played if self.games_played > 0 else 0.0
    
    @computed_field
    def assists_per_game(self) -> float:
        return self.total_assists / self.games_played if self.games_played > 0 else 0.0
    
    @computed_field
    def rebounds_per_game(self) -> float:
        return self.total_rebounds / self.games_played if self.games_played > 0 else 0.0
    
    @computed_field
    def steals_per_game(self) -> float:
        return self.total_steals / self.games_played if self.games_played > 0 else 0.0
    
    @computed_field
    def blocks_per_game(self) -> float:
        return self.total_blocks / self.games_played if self.games_played > 0 else 0.0
    
    @computed_field
    def turnovers_per_game(self) -> float:
        return self.total_turnovers / self.games_played if self.games_played > 0 else 0.0
    
    @computed_field
    def minutes_per_game(self) -> float:
        return self.minutes_played / self.games_played if self.games_played > 0 else 0.0
    
    @computed_field
    def plus_minus_per_game(self) -> float:
        return self.total_plus_minus / self.games_played if self.games_played > 0 else 0.0
    
    # Shooting percentages
    @computed_field
    def field_goal_pct(self) -> float:
        return (self.total_fgm / self.total_fga * 100) if self.total_fga > 0 else 0.0
    
    @computed_field
    def three_point_pct(self) -> float:
        return (self.total_3pm / self.total_3pa * 100) if self.total_3pa > 0 else 0.0
    
    @computed_field
    def free_throw_pct(self) -> float:
        return (self.total_ftm / self.total_fta * 100) if self.total_fta > 0 else 0.0
    
    # Game averages as a nested model
    @computed_field
    def averages(self) -> PlayerGameAverages:
        return PlayerGameAverages(
            games_played=self.games_played,
            points=self.points_per_game,
            assists=self.assists_per_game,
            rebounds=self.rebounds_per_game,
            steals=self.steals_per_game,
            blocks=self.blocks_per_game,
            turnovers=self.turnovers_per_game,
            field_goal_pct=self.field_goal_pct,
            three_point_pct=self.three_point_pct,
            free_throw_pct=self.free_throw_pct,
            minutes_per_game=self.minutes_per_game,
            plus_minus=self.plus_minus_per_game,
            double_doubles=self.double_doubles,
            triple_doubles=self.triple_doubles
        )

class PlayerGameLog(BaseModel):
    """Schema for a player's game log entry"""
    match_id: UUID
    match_date: datetime
    opponent_team_id: UUID
    opponent_team_name: str
    is_home: bool
    minutes_played: int
    points: int
    rebounds: int
    assists: int
    steals: int
    blocks: int
    turnovers: int
    fgm: int
    fga: int
    three_points_made: int
    three_points_attempted: int
    ftm: int
    fta: int
    plus_minus: int
    result: str  # 'W' or 'L'
    score: str  # e.g., "110-105"
    
    @property
    def field_goal_pct(self) -> float:
        return (self.fgm / self.fga * 100) if self.fga > 0 else 0.0
    
    @property
    def three_point_pct(self) -> float:
        return (self.three_points_made / self.three_points_attempted * 100) if self.three_points_attempted > 0 else 0.0
    
    @property
    def free_throw_pct(self) -> float:
        return (self.ftm / self.fta * 100) if self.fta > 0 else 0.0

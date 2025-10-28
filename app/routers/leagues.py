"""
Leagues Router

This module provides API endpoints for managing leagues in the system.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.supabase import supabase
from app.core.rate_limiter import limiter
from app.core.config import settings
from app.models.league import League, LeagueSeason, LeagueEnum, Console, GameYear
from app.core.auth import get_current_active_user
from app.schemas.user import User

router = APIRouter(
    prefix="/leagues",
    tags=["Leagues"],
    responses={404: {"description": "Not found"}},
)

# Configure logging
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class LeagueBase(BaseModel):
    league: str
    lg_discord: Optional[str] = None
    lg_logo_url: Optional[str] = None
    lg_url: Optional[str] = None
    sponsor_info: Optional[str] = None
    twitch_url: Optional[str] = None
    twitter_id: Optional[str] = None

    class Config:
        from_attributes = True
        use_enum_values = True

class LeagueCreate(LeagueBase):
    pass

class LeagueUpdate(BaseModel):
    league: Optional[str] = None
    lg_discord: Optional[str] = None
    lg_logo_url: Optional[str] = None
    lg_url: Optional[str] = None
    sponsor_info: Optional[str] = None
    twitch_url: Optional[str] = None
    twitter_id: Optional[str] = None

class LeagueResponse(LeagueBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True

# Season models
class SeasonBase(BaseModel):
    league_id: str
    league_name: str
    season_number: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current: bool = False

class SeasonCreate(SeasonBase):
    pass

class SeasonUpdate(BaseModel):
    season_number: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current: Optional[bool] = None

class SeasonResponse(SeasonBase):
    id: str

    class Config:
        from_attributes = True

# League Endpoints
@router.post("/", response_model=LeagueResponse, status_code=status.HTTP_201_CREATED)
async def create_league(
    league: LeagueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new league (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_league = League(
        **league.dict(),
        id=str(uuid4()),
        created_at=datetime.utcnow()
    )
    
    db.add(db_league)
    db.commit()
    db.refresh(db_league)
    
    return db_league

@router.get("/", response_model=List[LeagueResponse])
async def list_leagues(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all leagues.
    """
    return db.query(League).offset(skip).limit(limit).all()

@router.get("/{league_id}", response_model=LeagueResponse)
async def get_league(
    league_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a league by ID.
    """
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found"
        )
    return league

@router.put("/{league_id}", response_model=LeagueResponse)
async def update_league(
    league_id: str,
    league_update: LeagueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a league (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_league = db.query(League).filter(League.id == league_id).first()
    if not db_league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found"
        )
    
    update_data = league_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_league, field, value)
    
    db.commit()
    db.refresh(db_league)
    
    return db_league

@router.delete("/{league_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_league(
    league_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a league (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_league = db.query(League).filter(League.id == league_id).first()
    if not db_league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found"
        )
    
    db.delete(db_league)
    db.commit()
    
    return None

# Season Endpoints
@router.post("/seasons/", response_model=SeasonResponse, status_code=status.HTTP_201_CREATED)
async def create_season(
    season: SeasonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new league season (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Validate league exists
    league = db.query(League).filter(League.id == season.league_id).first()
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found"
        )
    
    db_season = LeagueSeason(
        **season.dict(),
        id=str(uuid4())
    )
    
    db.add(db_season)
    db.commit()
    db.refresh(db_season)
    
    return db_season

@router.get("/{league_id}/seasons", response_model=List[SeasonResponse])
async def list_season_id(
    league_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all seasons for a league.
    """
    return db.query(LeagueSeason)\
        .filter(LeagueSeason.league_id == league_id)\
        .offset(skip)\
        .limit(limit)\
        .all()

@router.get("/seasons/{season_id}", response_model=SeasonResponse)
async def get_season(
    season_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a season by ID.
    """
    season = db.query(LeagueSeason).filter(LeagueSeason.id == season_id).first()
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Season not found"
        )
    return season

@router.put("/seasons/{season_id}", response_model=SeasonResponse)
async def update_season(
    season_id: str,
    season_update: SeasonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a league season (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_season = db.query(LeagueSeason).filter(LeagueSeason.id == season_id).first()
    if not db_season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Season not found"
        )
    
    update_data = season_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_season, field, value)
    
    db.commit()
    db.refresh(db_season)
    
    return db_season

@router.delete("/seasons/{season_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_season(
    season_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a league season (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_season = db.query(LeagueSeason).filter(LeagueSeason.id == season_id).first()
    if not db_season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Season not found"
        )
    
    db.delete(db_season)
    db.commit()
    
    return None

# Enhanced League Endpoints (Using Supabase Views)

@router.get("/{league_id}/calendar")
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_league_calendar(
    request: Request,
    league_id: str
) -> Dict[str, Any]:
    """
    Get league calendar with upcoming matches and season info.
    
    This endpoint uses the league_calendar view for comprehensive data.
    """
    try:
        result = supabase.get_client().table("league_calendar") \
            .select("*") \
            .eq("league_id", league_id) \
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="League calendar not found"
            )
        
        return result.data[0] if result.data else {}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching league calendar for {league_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch league calendar"
        )

@router.get("/{league_id}/standings")
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_league_standings(
    request: Request,
    league_id: str,
    season_id: Optional[str] = Query(None, description="Filter by season")
) -> List[Dict[str, Any]]:
    """
    Get league division standings.
    
    Returns standings for all divisions in the league.
    """
    try:
        query = supabase.get_client().table("league_division_standings").select("*")
        
        # Note: league_division_standings view doesn't have league_id directly,
        # we need to filter by season_id which is linked to league
        if season_id:
            query = query.eq("season_id", season_id)
        
        query = query.order("overall_rank")
        result = query.execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching league standings for {league_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch league standings"
        )

@router.get("/{league_id}/results")
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_league_results(
    request: Request,
    league_id: str
) -> List[Dict[str, Any]]:
    """
    Get league results and team statistics.
    
    Returns comprehensive team statistics for the league.
    """
    try:
        result = supabase.get_client().table("league_results") \
            .select("*") \
            .eq("league_id", league_id) \
            .execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching league results for {league_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch league results"
        )

@router.get("/{league_id}/performance")
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_league_performance(
    request: Request,
    league_id: str,
    season_id: Optional[str] = Query(None, description="Filter by season")
) -> Dict[str, Any]:
    """
    Get league season performance analytics.
    
    Returns comprehensive performance metrics for a league season.
    """
    try:
        query = supabase.get_client().table("league_season_performance_mart").select("*").eq("league_id", league_id)
        
        if season_id:
            query = query.eq("season_id", season_id)
        
        result = query.execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="League performance data not found"
            )
        
        return result.data[0] if result.data else {}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching league performance for {league_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch league performance"
        )

@router.get("/{league_id}/rp-values")
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_league_rp_values(
    request: Request,
    league_id: str,
    game_year: Optional[str] = Query(None, description="Filter by game year")
) -> List[Dict[str, Any]]:
    """
    Get RP values and decay settings for a league.
    
    Returns RP configuration including max RP, bonuses, and decay rates.
    """
    try:
        query = supabase.get_client().table("league_rp_values").select("*").eq("league_id", league_id)
        
        if game_year:
            query = query.eq("game_year", game_year)
        
        result = query.execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching league RP values for {league_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch league RP values"
        )

@router.get("/{league_id}/divisions")
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_league_divisions(
    request: Request,
    league_id: str,
    season_id: Optional[str] = Query(None, description="Filter by season")
) -> List[Dict[str, Any]]:
    """
    Get divisions for a league.
    """
    try:
        query = supabase.get_client().table("lg_divisions").select("*").eq("league_id", league_id)
        
        if season_id:
            query = query.eq("season_id", season_id)
        
        query = query.order("display_order")
        result = query.execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching league divisions for {league_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch league divisions"
        )

@router.get("/{league_id}/conferences")
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_league_conferences(
    request: Request,
    league_id: str,
    season_id: Optional[str] = Query(None, description="Filter by season")
) -> List[Dict[str, Any]]:
    """
    Get conferences for a league.
    """
    try:
        query = supabase.get_client().table("lg_conf").select("*").eq("league", league_id)
        
        if season_id:
            query = query.eq("season", season_id)
        
        result = query.execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching league conferences for {league_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch league conferences"
        )

@router.get("/seasons/{season_id}/open")
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_season_open_tournament(
    request: Request,
    season_id: str
) -> Dict[str, Any]:
    """
    Get open tournament details for a league season.
    """
    try:
        result = supabase.get_client().table("league_open") \
            .select("*") \
            .eq("season_id", season_id) \
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Open tournament not found for this season"
            )
        
        return result.data[0] if result.data else {}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching season open tournament for {season_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch open tournament"
        )

@router.get("/seasons/{season_id}/playoff")
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_season_playoff_tournament(
    request: Request,
    season_id: str
) -> Dict[str, Any]:
    """
    Get playoff tournament details for a league season.
    """
    try:
        result = supabase.get_client().table("league_playoff") \
            .select("*") \
            .eq("season_id", season_id) \
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Playoff tournament not found for this season"
            )
        
        return result.data[0] if result.data else {}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching season playoff tournament for {season_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch playoff tournament"
        )

@router.get("/seasons/{season_id}/player-stats")
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_season_player_stats(
    request: Request,
    season_id: str,
    stage: Optional[str] = Query(None, description="Filter by stage (open, playoff, regular_season)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get player statistics for a league season.
    
    Can filter by stage (open, playoff, regular_season).
    """
    try:
        # Determine which view to query based on stage
        if stage == "open":
            table_name = "league_open_player_stats"
        elif stage == "playoff":
            table_name = "league_playoff_player_stats"
        elif stage == "regular_season":
            table_name = "league_regular_season_player_stats"
        else:
            # Default to all player stats
            table_name = "player_stats_by_league_season"
        
        result = supabase.get_client().table(table_name) \
            .select("*") \
            .eq("season_id", season_id) \
            .order("avg_points", desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching season player stats for {season_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch season player stats"
        )

@router.get("/seasons/{season_id}/teams")
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_season_teams(
    request: Request,
    season_id: str
) -> List[Dict[str, Any]]:
    """
    Get all teams participating in a league season.
    """
    try:
        result = supabase.get_client().table("league_season_team_rosters") \
            .select("team_id, team_name") \
            .eq("season_id", season_id) \
            .execute()
        
        # Get unique teams
        teams_dict = {}
        for row in (result.data if hasattr(result, 'data') else []):
            team_id = row.get("team_id")
            if team_id and team_id not in teams_dict:
                teams_dict[team_id] = {
                    "team_id": team_id,
                    "team_name": row.get("team_name")
                }
        
        return list(teams_dict.values())
    except Exception as e:
        logger.error(f"Error fetching season teams for {season_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch season teams"
        )

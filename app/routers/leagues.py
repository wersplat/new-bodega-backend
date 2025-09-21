"""
Leagues Router

This module provides API endpoints for managing leagues in the system.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.league import League, LeagueSeason, LeagueEnum, Console, GameYear
from app.core.auth import get_current_active_user
from app.schemas.user import User

router = APIRouter(
    prefix="/leagues",
    tags=["Leagues"],
    responses={404: {"description": "Not found"}},
)

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

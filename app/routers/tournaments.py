"""
Tournaments Router

This module provides API endpoints for managing tournaments in the system.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.league import Tournament, Console, GameYear, TournamentTier as EventTier, TournamentStatus as Status
from app.core.auth import get_current_active_user, User

router = APIRouter(
    prefix="/tournaments",
    tags=["Tournaments"],
    responses={404: {"description": "Not found"}},
)

# Pydantic models for request/response
class TournamentBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: Status
    tier: EventTier
    console: Console
    game_year: GameYear
    start_date: datetime
    end_date: datetime
    organizer_id: Optional[UUID] = None
    organizer_logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    rules_url: Optional[str] = None
    place: Optional[UUID] = None
    prize_pool: Optional[int] = None
    max_rp: Optional[int] = None
    decay_days: Optional[int] = None
    champion: Optional[UUID] = None
    runner_up: Optional[UUID] = None
    sponsor: Optional[str] = None
    sponsor_logo: Optional[str] = None

    class Config:
        orm_mode = True
        use_enum_values = True

class TournamentCreate(TournamentBase):
    pass

class TournamentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Status] = None
    tier: Optional[EventTier] = None
    console: Optional[Console] = None
    game_year: Optional[GameYear] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    organizer_id: Optional[UUID] = None
    organizer_logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    rules_url: Optional[str] = None
    place: Optional[UUID] = None
    prize_pool: Optional[int] = None
    max_rp: Optional[int] = None
    decay_days: Optional[int] = None
    champion: Optional[UUID] = None
    runner_up: Optional[UUID] = None
    sponsor: Optional[str] = None
    sponsor_logo: Optional[str] = None

class TournamentResponse(TournamentBase):
    id: UUID
    created_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        use_enum_values = True

# Endpoints
@router.post("/", response_model=TournamentResponse, status_code=status.HTTP_201_CREATED)
async def create_tournament(
    tournament: TournamentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new tournament (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_tournament = Tournament(
        **tournament.dict(),
        id=uuid4(),
        created_at=datetime.utcnow()
    )
    
    db.add(db_tournament)
    db.commit()
    db.refresh(db_tournament)
    
    return db_tournament

@router.get("/", response_model=List[TournamentResponse])
async def list_tournaments(
    skip: int = 0,
    limit: int = 100,
    status: Optional[Status] = None,
    tier: Optional[EventTier] = None,
    console: Optional[Console] = None,
    game_year: Optional[GameYear] = None,
    db: Session = Depends(get_db)
):
    """
    List all tournaments with optional filtering.
    """
    query = db.query(Tournament)
    
    if status:
        query = query.filter(Tournament.status == status)
    if tier:
        query = query.filter(Tournament.tier == tier)
    if console:
        query = query.filter(Tournament.console == console)
    if game_year:
        query = query.filter(Tournament.game_year == game_year)
    
    return query.offset(skip).limit(limit).all()

@router.get("/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(
    tournament_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a tournament by ID.
    """
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    return tournament

@router.put("/{tournament_id}", response_model=TournamentResponse)
async def update_tournament(
    tournament_id: UUID,
    tournament_update: TournamentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a tournament (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not db_tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    update_data = tournament_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tournament, field, value)
    
    db.commit()
    db.refresh(db_tournament)
    
    return db_tournament

@router.delete("/{tournament_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tournament(
    tournament_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a tournament (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not db_tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    db.delete(db_tournament)
    db.commit()
    
    return None

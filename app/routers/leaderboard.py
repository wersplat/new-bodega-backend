"""
Leaderboard router for global and event rankings
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import desc

from app.core.database import get_db
from app.models.player import Player, PlayerTier
from app.models.event import Event, EventResult
from app.schemas.player import PlayerProfile

router = APIRouter()

@router.get("/global", response_model=List[PlayerProfile])
async def get_global_leaderboard(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    tier: Optional[PlayerTier] = None,
    db: Session = Depends(get_db)
):
    """
    Get global leaderboard by RP
    """
    query = db.query(Player)
    
    if tier:
        query = query.filter(Player.tier == tier)
    
    players = query.order_by(desc(Player.current_rp)).offset(offset).limit(limit).all()
    return players

@router.get("/global/top", response_model=List[PlayerProfile])
async def get_top_players(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get top players globally
    """
    players = db.query(Player).order_by(desc(Player.current_rp)).limit(limit).all()
    return players

@router.get("/tier/{tier}", response_model=List[PlayerProfile])
async def get_tier_leaderboard(
    tier: PlayerTier,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get leaderboard for specific tier
    """
    players = db.query(Player).filter(
        Player.tier == tier
    ).order_by(desc(Player.current_rp)).offset(offset).limit(limit).all()
    return players

@router.get("/event/{event_id}", response_model=List[PlayerProfile])
async def get_event_leaderboard(
    event_id: int,
    db: Session = Depends(get_db)
):
    """
    Get leaderboard for specific event
    """
    # Check if event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Get event results ordered by position
    results = db.query(EventResult).filter(
        EventResult.event_id == event_id
    ).order_by(EventResult.position).all()
    
    # Get player profiles for results
    player_ids = [result.player_id for result in results]
    players = db.query(Player).filter(Player.id.in_(player_ids)).all()
    
    # Create a map for quick lookup
    player_map = {player.id: player for player in players}
    
    # Return players in result order
    leaderboard = []
    for result in results:
        if result.player_id in player_map:
            leaderboard.append(player_map[result.player_id])
    
    return leaderboard

@router.get("/peak", response_model=List[PlayerProfile])
async def get_peak_rp_leaderboard(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get leaderboard by peak RP
    """
    players = db.query(Player).order_by(desc(Player.peak_rp)).offset(offset).limit(limit).all()
    return players

@router.get("/platform/{platform}", response_model=List[PlayerProfile])
async def get_platform_leaderboard(
    platform: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get leaderboard for specific platform
    """
    players = db.query(Player).filter(
        Player.platform.ilike(f"%{platform}%")
    ).order_by(desc(Player.current_rp)).offset(offset).limit(limit).all()
    return players

@router.get("/region/{region}", response_model=List[PlayerProfile])
async def get_region_leaderboard(
    region: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get leaderboard for specific region
    """
    players = db.query(Player).filter(
        Player.region.ilike(f"%{region}%")
    ).order_by(desc(Player.current_rp)).offset(offset).limit(limit).all()
    return players 
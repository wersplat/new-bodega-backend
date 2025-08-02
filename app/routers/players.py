"""
Players router for player profile management and lookups
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.auth import get_current_active_user, get_current_user
from app.models.user import User
from app.models.player import Player, RPHistory
from app.schemas.player import PlayerCreate, Player as PlayerSchema, PlayerProfile, PlayerUpdate, PlayerWithHistory

router = APIRouter()

@router.post("/", response_model=PlayerSchema)
async def create_player(
    player: PlayerCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Register a new player profile
    """
    # Check if user already has a player profile
    existing_player = db.query(Player).filter(Player.user_id == current_user.id).first()
    if existing_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a player profile"
        )
    
    # Check if gamertag is already taken
    existing_gamertag = db.query(Player).filter(Player.gamertag == player.gamertag).first()
    if existing_gamertag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gamertag already taken"
        )
    
    # Create player profile
    db_player = Player(
        user_id=current_user.id,
        gamertag=player.gamertag,
        team_name=player.team_name,
        region=player.region,
    )
    
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    
    return db_player

@router.get("/{player_id}", response_model=PlayerProfile)
async def get_player(player_id: int, db: Session = Depends(get_db)):
    """
    Get player profile by ID
    """
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    return player

@router.get("/me/profile", response_model=PlayerProfile)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's player profile
    """
    player = db.query(Player).filter(Player.user_id == current_user.id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player profile not found"
        )
    
    return player

@router.put("/me/profile", response_model=PlayerSchema)
async def update_my_profile(
    player_update: PlayerUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's player profile
    """
    player = db.query(Player).filter(Player.user_id == current_user.id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player profile not found"
        )
    
    # Update fields
    update_data = player_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(player, field, value)
    
    db.commit()
    db.refresh(player)
    
    return player

@router.get("/{player_id}/history", response_model=PlayerWithHistory)
async def get_player_history(player_id: int, db: Session = Depends(get_db)):
    """
    Get player profile with RP history
    """
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    return player

@router.get("/search/{gamertag}", response_model=PlayerProfile)
async def search_player_by_gamertag(gamertag: str, db: Session = Depends(get_db)):
    """
    Search for player by gamertag
    """
    player = db.query(Player).filter(Player.gamertag.ilike(f"%{gamertag}%")).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    return player 
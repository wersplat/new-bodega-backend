"""
LEGACY ROUTER - DO NOT USE DIRECTLY

This is a legacy router that has been replaced by players_supabase.py.
It is kept for reference purposes only and its endpoints are disabled.
"""

import os
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.auth import get_current_active_user, get_current_user
from app.models.user import User
from app.models.player import Player, RPHistory
from app.schemas.player import PlayerCreate, Player as PlayerSchema, PlayerProfile, PlayerUpdate, PlayerWithHistory

# Create router with disabled tag to clearly identify it in API docs
router = APIRouter(tags=["LEGACY - DISABLED"])

# Only register endpoints if explicitly enabled (which should not be done in production)
if os.environ.get("ENABLE_LEGACY_ENDPOINTS", "").lower() == "true":
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
        
        # Create new player
        new_player = Player(
            user_id=current_user.id,
            gamertag=player.gamertag,
            platform=player.platform,
            region=player.region
        )
        db.add(new_player)
        db.commit()
        db.refresh(new_player)
        return new_player
else:
    # Add a warning endpoint to indicate this router is disabled
    @router.get("/", include_in_schema=False)
    def legacy_disabled():
        """This endpoint is disabled as it has been replaced by the Supabase version."""
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This legacy endpoint has been disabled. Please use the new API endpoints."
        )

"""
Player Badges Router

This module provides API endpoints for managing player badges.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from pydantic import BaseModel, ConfigDict, Field

from app.core.supabase import supabase
from app.core.auth_supabase import require_admin_api_token
from app.core.rate_limiter import limiter
from app.core.config import settings
from app.schemas.badge import (
    PlayerBadge, PlayerBadgeCreate, PlayerBadgeUpdate, 
    PlayerBadgeWithDetails
)

# Initialize router
router = APIRouter(
    prefix="/v1/player-badges",
    tags=["Player Badges"],
    responses={404: {"description": "Not found"}},
)

# Configure logging
logger = logging.getLogger(__name__)

@router.post(
    "/",
    response_model=PlayerBadge,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_api_token)]
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def create_player_badge(
    request: Request,
    player_badge: PlayerBadgeCreate
) -> Dict[str, Any]:
    """Create a new player badge."""
    try:
        result = supabase.insert("player_badges", player_badge.model_dump())
        return result
    except Exception as e:
        logger.error(f"Error creating player badge: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create player badge"
        )

@router.get(
    "/",
    response_model=List[PlayerBadgeWithDetails]
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_player_badges(
    request: Request,
    player_wallet: Optional[str] = Query(None, description="Filter by player wallet"),
    match_id: Optional[int] = Query(None, description="Filter by match ID"),
    tournament_id: Optional[str] = Query(None, description="Filter by tournament ID"),
    league_id: Optional[str] = Query(None, description="Filter by league ID"),
    badge_type: Optional[str] = Query(None, description="Filter by badge type"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """Get player badges with filtering options."""
    try:
        query = supabase.get_client().table("player_badges").select("*")
        
        if player_wallet:
            query = query.eq("player_wallet", player_wallet)
        if match_id:
            query = query.eq("match_id", match_id)
        if tournament_id:
            query = query.eq("tournament_id", tournament_id)
        if league_id:
            query = query.eq("league_id", league_id)
        if badge_type:
            query = query.eq("badge_type", badge_type)
            
        query = query.range(offset, offset + limit - 1)
        result = query.execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching player badges: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch player badges"
        )

@router.get(
    "/{badge_id}",
    response_model=PlayerBadgeWithDetails
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_player_badge_by_id(
    request: Request,
    badge_id: str
) -> Dict[str, Any]:
    """Get a specific player badge by ID."""
    try:
        result = supabase.get_by_id("player_badges", badge_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player badge not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching player badge {badge_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch player badge"
        )

@router.get(
    "/player/{player_wallet}",
    response_model=List[PlayerBadgeWithDetails]
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_player_badges_by_wallet(
    request: Request,
    player_wallet: str
) -> List[Dict[str, Any]]:
    """Get all badges for a specific player wallet."""
    try:
        result = supabase.get_client().table("player_badges").select("*").eq("player_wallet", player_wallet).execute()
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching badges for player {player_wallet}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch player badges"
        )

@router.put(
    "/{badge_id}",
    response_model=PlayerBadge,
    dependencies=[Depends(require_admin_api_token)]
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def update_player_badge(
    request: Request,
    badge_id: str,
    player_badge_update: PlayerBadgeUpdate
) -> Dict[str, Any]:
    """Update a player badge."""
    try:
        update_data = {k: v for k, v in player_badge_update.model_dump().items() if v is not None}
        result = supabase.update("player_badges", badge_id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player badge not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating player badge {badge_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update player badge"
        )

@router.delete(
    "/{badge_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin_api_token)]
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def delete_player_badge(
    request: Request,
    badge_id: str
):
    """Delete a player badge."""
    try:
        result = supabase.delete("player_badges", badge_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player badge not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting player badge {badge_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete player badge"
        )

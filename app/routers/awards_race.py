"""
Awards Race Router

This module provides API endpoints for managing awards race data.
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
from app.schemas.awards import (
    AwardsRace, AwardsRaceCreate, AwardsRaceUpdate, 
    AwardsRaceWithDetails, AwardTypes
)

# Initialize router
router = APIRouter(
    prefix="/v1/awards-race",
    tags=["Awards Race"],
    responses={404: {"description": "Not found"}},
)

# Configure logging
logger = logging.getLogger(__name__)

@router.post(
    "/",
    response_model=AwardsRace,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_api_token)]
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def create_awards_race(
    request: Request,
    awards_race: AwardsRaceCreate
) -> Dict[str, Any]:
    """Create a new awards race entry."""
    try:
        result = supabase.insert("awards_race", awards_race.model_dump())
        return result
    except Exception as e:
        logger.error(f"Error creating awards race: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create awards race entry"
        )

@router.get(
    "/",
    response_model=List[AwardsRaceWithDetails]
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_awards_race(
    request: Request,
    tournament_id: Optional[str] = Query(None, description="Filter by tournament ID"),
    league_id: Optional[str] = Query(None, description="Filter by league ID"),
    team_id: Optional[str] = Query(None, description="Filter by team ID"),
    player_id: Optional[str] = Query(None, description="Filter by player ID"),
    award_type: Optional[AwardTypes] = Query(None, description="Filter by award type"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """Get awards race entries with filtering options."""
    try:
        query = supabase.get_client().table("awards_race").select("*")
        
        if tournament_id:
            query = query.eq("tournament_id", tournament_id)
        if league_id:
            query = query.eq("league_id", league_id)
        if team_id:
            query = query.eq("team_id", team_id)
        if player_id:
            query = query.eq("player_id", player_id)
        if award_type:
            query = query.eq("award_type", award_type.value)
            
        query = query.range(offset, offset + limit - 1)
        result = query.execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching awards race: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch awards race entries"
        )

@router.get(
    "/{awards_race_id}",
    response_model=AwardsRaceWithDetails
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_awards_race_by_id(
    request: Request,
    awards_race_id: str
) -> Dict[str, Any]:
    """Get a specific awards race entry by ID."""
    try:
        result = supabase.get_by_id("awards_race", awards_race_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Awards race entry not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching awards race {awards_race_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch awards race entry"
        )

@router.put(
    "/{awards_race_id}",
    response_model=AwardsRace,
    dependencies=[Depends(require_admin_api_token)]
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def update_awards_race(
    request: Request,
    awards_race_id: str,
    awards_race_update: AwardsRaceUpdate
) -> Dict[str, Any]:
    """Update an awards race entry."""
    try:
        update_data = {k: v for k, v in awards_race_update.model_dump().items() if v is not None}
        result = supabase.update("awards_race", awards_race_id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Awards race entry not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating awards race {awards_race_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update awards race entry"
        )

@router.delete(
    "/{awards_race_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin_api_token)]
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def delete_awards_race(
    request: Request,
    awards_race_id: str
):
    """Delete an awards race entry."""
    try:
        result = supabase.delete("awards_race", awards_race_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Awards race entry not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting awards race {awards_race_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete awards race entry"
        )

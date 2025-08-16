"""
Team Rosters Router

This module provides API endpoints for managing team rosters.
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
from app.schemas.team_roster import (
    TeamRoster, TeamRosterCreate, TeamRosterUpdate, 
    TeamRosterWithDetails
)

# Initialize router
router = APIRouter(
    prefix="/v1/team-rosters",
    tags=["Team Rosters"],
    responses={404: {"description": "Not found"}},
)

# Configure logging
logger = logging.getLogger(__name__)

@router.post(
    "/",
    response_model=TeamRoster,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_api_token)]
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def create_team_roster(
    request: Request,
    team_roster: TeamRosterCreate
) -> Dict[str, Any]:
    """Create a new team roster entry."""
    try:
        result = supabase.insert("team_rosters", team_roster.model_dump())
        return result
    except Exception as e:
        logger.error(f"Error creating team roster: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create team roster entry"
        )

@router.get(
    "/",
    response_model=List[TeamRosterWithDetails]
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_team_rosters(
    request: Request,
    team_id: Optional[str] = Query(None, description="Filter by team ID"),
    player_id: Optional[str] = Query(None, description="Filter by player ID"),
    tournament_id: Optional[str] = Query(None, description="Filter by tournament ID"),
    league_id: Optional[str] = Query(None, description="Filter by league ID"),
    is_captain: Optional[bool] = Query(None, description="Filter by captain status"),
    is_player_coach: Optional[bool] = Query(None, description="Filter by player coach status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """Get team rosters with filtering options."""
    try:
        query = supabase.get_client().table("team_rosters").select("*")
        
        if team_id:
            query = query.eq("team_id", team_id)
        if player_id:
            query = query.eq("player_id", player_id)
        if tournament_id:
            query = query.eq("tournament_id", tournament_id)
        if league_id:
            query = query.eq("league_id", league_id)
        if is_captain is not None:
            query = query.eq("is_captain", is_captain)
        if is_player_coach is not None:
            query = query.eq("is_player_coach", is_player_coach)
            
        query = query.range(offset, offset + limit - 1)
        result = query.execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching team rosters: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch team rosters"
        )

@router.get(
    "/{roster_id}",
    response_model=TeamRosterWithDetails
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_team_roster_by_id(
    request: Request,
    roster_id: str
) -> Dict[str, Any]:
    """Get a specific team roster entry by ID."""
    try:
        result = supabase.get_by_id("team_rosters", roster_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team roster entry not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching team roster {roster_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch team roster entry"
        )

@router.get(
    "/team/{team_id}",
    response_model=List[TeamRosterWithDetails]
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_team_roster_by_team(
    request: Request,
    team_id: str
) -> List[Dict[str, Any]]:
    """Get all roster entries for a specific team."""
    try:
        result = supabase.get_client().table("team_rosters").select("*").eq("team_id", team_id).execute()
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching roster for team {team_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch team roster"
        )

@router.get(
    "/player/{player_id}",
    response_model=List[TeamRosterWithDetails]
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_team_roster_by_player(
    request: Request,
    player_id: str
) -> List[Dict[str, Any]]:
    """Get all roster entries for a specific player."""
    try:
        result = supabase.get_client().table("team_rosters").select("*").eq("player_id", player_id).execute()
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching roster for player {player_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch player roster"
        )

@router.put(
    "/{roster_id}",
    response_model=TeamRoster,
    dependencies=[Depends(require_admin_api_token)]
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def update_team_roster(
    request: Request,
    roster_id: str,
    team_roster_update: TeamRosterUpdate
) -> Dict[str, Any]:
    """Update a team roster entry."""
    try:
        update_data = {k: v for k, v in team_roster_update.model_dump().items() if v is not None}
        result = supabase.update("team_rosters", roster_id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team roster entry not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating team roster {roster_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update team roster entry"
        )

@router.delete(
    "/{roster_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin_api_token)]
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def delete_team_roster(
    request: Request,
    roster_id: str
):
    """Delete a team roster entry."""
    try:
        result = supabase.delete("team_rosters", roster_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team roster entry not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting team roster {roster_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete team roster entry"
        )

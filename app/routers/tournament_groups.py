"""
Tournament Groups Router

This module provides API endpoints for managing tournament groups.
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
from app.schemas.tournament_group import (
    TournamentGroup, TournamentGroupCreate, TournamentGroupUpdate,
    TournamentGroupWithTeams, TournamentGroupMember, TournamentGroupMemberCreate,
    TournamentGroupMemberWithDetails
)

# Initialize router
router = APIRouter(
    prefix="/v1/tournament-groups",
    tags=["Tournament Groups"],
    responses={404: {"description": "Not found"}},
)

# Configure logging
logger = logging.getLogger(__name__)

@router.post(
    "/",
    response_model=TournamentGroup,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_api_token)]
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def create_tournament_group(
    request: Request,
    tournament_group: TournamentGroupCreate
) -> Dict[str, Any]:
    """Create a new tournament group."""
    try:
        result = supabase.insert("tournament_groups", tournament_group.model_dump())
        return result
    except Exception as e:
        logger.error(f"Error creating tournament group: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create tournament group"
        )

@router.get(
    "/",
    response_model=List[TournamentGroupWithTeams]
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_tournament_groups(
    request: Request,
    tournament_id: Optional[str] = Query(None, description="Filter by tournament ID"),
    league_season_id: Optional[str] = Query(None, description="Filter by league season ID"),
    status: Optional[str] = Query(None, description="Filter by group status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """Get tournament groups with filtering options."""
    try:
        query = supabase.get_client().table("tournament_groups").select("*")
        
        if tournament_id:
            query = query.eq("tournament_id", tournament_id)
        if league_season_id:
            query = query.eq("league_season_id", league_season_id)
        if status:
            query = query.eq("status", status)
            
        query = query.range(offset, offset + limit - 1)
        result = query.execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching tournament groups: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tournament groups"
        )

@router.get(
    "/{group_id}",
    response_model=TournamentGroupWithTeams
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_tournament_group_by_id(
    request: Request,
    group_id: str
) -> Dict[str, Any]:
    """Get a specific tournament group by ID."""
    try:
        result = supabase.get_by_id("tournament_groups", group_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tournament group not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching tournament group {group_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tournament group"
        )

@router.put(
    "/{group_id}",
    response_model=TournamentGroup,
    dependencies=[Depends(require_admin_api_token)]
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def update_tournament_group(
    request: Request,
    group_id: str,
    tournament_group_update: TournamentGroupUpdate
) -> Dict[str, Any]:
    """Update a tournament group."""
    try:
        update_data = {k: v for k, v in tournament_group_update.model_dump().items() if v is not None}
        result = supabase.update("tournament_groups", group_id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tournament group not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tournament group {group_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update tournament group"
        )

@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin_api_token)]
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def delete_tournament_group(
    request: Request,
    group_id: str
):
    """Delete a tournament group."""
    try:
        result = supabase.delete("tournament_groups", group_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tournament group not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting tournament group {group_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete tournament group"
        )

# Tournament Group Members endpoints

@router.post(
    "/{group_id}/members",
    response_model=TournamentGroupMember,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_api_token)]
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def add_team_to_group(
    request: Request,
    group_id: str,
    member: TournamentGroupMemberCreate
) -> Dict[str, Any]:
    """Add a team to a tournament group."""
    try:
        member_data = member.model_dump()
        member_data["group_id"] = group_id
        result = supabase.insert("tournament_group_members", member_data)
        return result
    except Exception as e:
        logger.error(f"Error adding team to group: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add team to group"
        )

@router.get(
    "/{group_id}/members",
    response_model=List[TournamentGroupMemberWithDetails]
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_group_members(
    request: Request,
    group_id: str
) -> List[Dict[str, Any]]:
    """Get all teams in a tournament group."""
    try:
        result = supabase.get_client().table("tournament_group_members").select("*").eq("group_id", group_id).execute()
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching group members for {group_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch group members"
        )

@router.delete(
    "/{group_id}/members/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin_api_token)]
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def remove_team_from_group(
    request: Request,
    group_id: str,
    team_id: str
):
    """Remove a team from a tournament group."""
    try:
        # Find the member entry
        result = supabase.get_client().table("tournament_group_members").select("*").eq("group_id", group_id).eq("team_id", team_id).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found in group"
            )
        
        member_id = result.data[0]["id"]
        supabase.delete("tournament_group_members", member_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing team from group: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove team from group"
        )

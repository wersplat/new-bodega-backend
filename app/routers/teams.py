"""
Teams Router (Supabase Backend)

This module provides a RESTful API for managing teams with improved
performance, better error handling, and comprehensive documentation.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.core.supabase import supabase
from app.core.auth_supabase import supabase_user_from_bearer, require_admin_api_token
from app.core.rate_limiter import limiter
from app.core.config import settings
from app.schemas.team import Team, TeamCreate, TeamUpdate, TeamWithPlayers, TeamWithStats, TeamListResponse

# Initialize router with rate limiting and explicit prefix
router = APIRouter(
    prefix="/v1/teams",
    tags=["Teams"],
    responses={404: {"description": "Not found"}},
)

# Configure logging
logger = logging.getLogger(__name__)

# Constants
UUID_PATTERN = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
UUID_EXAMPLE = "123e4567-e89b-12d3-a456-426614174000"



class TeamWithPlayers(Team):
    """Team model that includes player information."""
    players: List[Dict[str, Any]] = Field(default_factory=list, description="List of players on the team")

class TeamListResponse(BaseModel):
    """Paginated list of teams with metadata."""
    items: List[Team] = Field(..., description="List of teams")
    total: int = Field(..., description="Total number of teams matching the query")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    has_more: bool = Field(..., description="Whether there are more items available")

# Helper Functions
async def get_team_by_id(team_id: str) -> Optional[Dict[str, Any]]:
    """
    Helper function to get a team by ID with proper error handling.
    
    Args:
        team_id: The UUID of the team to retrieve
        
    Returns:
        Optional[Dict[str, Any]]: The team data if found, None otherwise
        
    Raises:
        HTTPException: If there's an error retrieving the team
    """
    try:
        if not team_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team ID is required"
            )
            
        result = supabase.get_by_id("teams", team_id)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving team {team_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the team"
        )

# API Endpoints
@router.post(
    "/",
    response_model=Team,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Team created successfully"},
        400: {"description": "Invalid input data or team name already taken"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def create_team(
    request: Request,
    team: TeamCreate,
    current_user: Dict[str, Any] = Depends(supabase_user_from_bearer)
) -> Dict[str, Any]:
    """
    Create a new team.
    
    This endpoint allows authenticated users to create a new team.
    The user who creates the team will be set as the team owner.
    """
    try:
        # Check if team name is already taken
        client = supabase.get_client()
        existing_team = client.table("teams")\
            .select("*")\
            .ilike("name", team.name)\
            .execute()
        
        if existing_team and hasattr(existing_team, 'data') and existing_team.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team name is already taken"
            )
        
        # Prepare team data
        team_data = team.dict(exclude_unset=True)
        # Prefer sub/user_id/id claim order
        user_id = current_user.get("sub") or current_user.get("user_id") or current_user.get("id")
        team_data["created_by"] = str(user_id) if user_id else None
        
        # Create team
        created_team = supabase.insert("teams", team_data)
        
        return created_team
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating team: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the team"
        )

@router.get(
    "/{team_id}",
    response_model=TeamWithPlayers,
    responses={
        200: {"description": "Team details retrieved successfully"},
        404: {"description": "Team not found"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_team(
    request: Request,
    team_id: str = Path(..., description="The UUID of the team to retrieve", 
                       examples=[UUID_EXAMPLE], pattern=UUID_PATTERN),
    include_players: bool = Query(
        True,
        description="Whether to include player details in the response"
    )
) -> Dict[str, Any]:
    """
    Get team details by ID.
    
    This endpoint retrieves detailed information about a specific team,
    including its players if requested.
    """
    try:
        team = await get_team_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team with ID {team_id} not found"
            )
        
        if include_players:
            # Get team players
            client = supabase.get_client()
            players = client.table("players")\
                .select("*")\
                .eq("current_team_id", team_id)\
                .execute()
            
            team["players"] = players.data if hasattr(players, 'data') else []
        
        return team
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving team {team_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the team"
        )

@router.get(
    "/",
    response_model=TeamListResponse,
    responses={
        200: {"description": "List of teams retrieved successfully"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_teams(
    request: Request,
    name: Optional[str] = Query(
        None,
        description="Filter teams by name (case-insensitive contains)",
        min_length=1,
        max_length=100
    ),
    region_id: Optional[str] = Query(
        None,
        description="Filter teams by region ID",
        pattern=UUID_PATTERN,
        examples=[UUID_EXAMPLE]
    ),
    is_active: Optional[bool] = Query(
        None,
        description="Filter teams by active status"
    ),
    page: int = Query(
        1,
        ge=1,
        description="Page number for pagination"
    ),
    size: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of items per page"
    )
) -> Dict[str, Any]:
    """
    List teams with optional filtering and pagination.
    
    This endpoint returns a paginated list of teams that match the specified filters.
    """
    try:
        offset = (page - 1) * size
        limit = size
        
        # Build query
        client = supabase.get_client()
        query = client.table("teams").select("*", count="exact")
        
        # Apply filters
        if name:
            query = query.ilike("name", f"%{name}%")
        if region_id:
            query = query.eq("region_id", region_id)
        if is_active is not None:
            query = query.eq("is_active", is_active)
        
        # Get total count
        count_result = query.execute()
        total = count_result.count if hasattr(count_result, 'count') else 0
        
        # Apply pagination
        query = query.range(offset, offset + limit - 1)
        
        # Execute query
        result = query.execute()
        items = result.data if hasattr(result, 'data') else []
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "has_more": (offset + len(items)) < total
        }
        
    except Exception as e:
        logger.error(f"Error listing teams: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving teams"
        )
        
        print("Result object:", result)
        print("Result type:", type(result))
        print("Result dir:", dir(result))
        
        if not hasattr(result, 'data'):
            error_msg = f"No 'data' attribute in result. Result: {result}"
            print(error_msg)
            return []
        
        print(f"Result data type: {type(result.data)}")
        print(f"Result data: {result.data}")
            
        print(f"Successfully retrieved {len(result.data)} teams")
        return result.data
        
    except Exception as e:
        error_msg = f"Error in list_teams: {str(e)}\nType: {type(e).__name__}"
        print(error_msg)
        import traceback
        traceback_str = traceback.format_exc()
        print(traceback_str)
        
        # Return a 500 error with detailed information
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to list teams",
                "message": str(e),
                "type": type(e).__name__
            }
        )

@router.put("/{team_id}", response_model=Team)
async def update_team(
    team_id: str,
    team_update: TeamUpdate,
    _: None = Depends(require_admin_api_token)
):
    """
    Update team information
    """
    # Check if team exists
    team = await get_team_by_id(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if user has permission to update the team
    # Note: Add your permission logic here
    
    try:
        updated_team = supabase.update("teams", team_id, team_update.model_dump(exclude_unset=True))
        return updated_team
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update team: {str(e)}"
        )

@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: str,
    _: None = Depends(require_admin_api_token)
):
    """
    Delete a team
    """
    # Check if team exists
    team = await get_team_by_id(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if user has permission to delete the team
    # Note: Add your permission logic here
    
    try:
        # First, remove all players from the team
        client = supabase.get_client()
        client.table("players").update({"current_team_id": None}).eq("current_team_id", team_id).execute()
        
        # Then delete the team
        supabase.delete("teams", team_id)
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete team: {str(e)}"
        )

@router.get("/search/{name}", response_model=List[Team])
async def search_teams_by_name(name: str):
    """
    Search teams by name
    """
    client = supabase.get_client()
    result = client.table("teams").select("*").ilike("name", f"%{name}%").execute()
    return result.data if hasattr(result, 'data') else []

@router.get("/search", response_model=List[Team])
async def search_teams(
    q: str = Query(..., description="Search query for team name", min_length=1, max_length=100),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results to return")
):
    """
    Search teams by name using a query parameter.

    This endpoint supports the query style used by the admin frontend:
    GET /v1/teams/search?q=NAME&limit=20
    """
    client = supabase.get_client()
    query = client.table("teams").select("*").ilike("name", f"%{q}%").limit(limit)
    result = query.execute()
    return result.data if hasattr(result, 'data') else []

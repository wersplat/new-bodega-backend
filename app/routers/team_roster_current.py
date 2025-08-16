"""
Team Roster Current Router

This module provides API endpoints for accessing the team_roster_current view,
which shows current team rosters with player details.

Endpoints:
- GET /: Get all current team rosters with pagination and filtering
- GET /team/{team_id}: Get current roster for a specific team
- GET /teams: Get all teams with their current rosters
"""

import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, status, Request, Query, Path

from app.core.supabase import supabase
from app.core.rate_limiter import limiter
from app.core.config import settings
from app.schemas.team_roster import (
    TeamRosterCurrent,
    TeamRosterCurrentList,
    TeamRosterCurrentByTeam
)

# Initialize router with rate limiting and explicit prefix
router = APIRouter(
    prefix="/v1/team-roster-current",
    tags=["Team Roster Current"],
    responses={404: {"description": "Not found"}},
)

# Configure logging
logger = logging.getLogger(__name__)

@router.get(
    "/",
    response_model=List[TeamRosterCurrent],
    responses={
        200: {"description": "Team roster current entries retrieved successfully"},
        400: {"description": "Invalid query parameters"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_team_roster_current(
    request: Request,
    # Pagination
    limit: int = Query(100, ge=1, le=1000, description="Number of entries to return (1-1000)"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    
    # Filtering
    team_id: Optional[str] = Query(None, description="Filter by team ID"),
    player_id: Optional[str] = Query(None, description="Filter by player ID"),
    is_captain: Optional[bool] = Query(None, description="Filter by captain status"),
    is_player_coach: Optional[bool] = Query(None, description="Filter by player coach status"),
    position: Optional[str] = Query(None, description="Filter by player position"),
    salary_tier: Optional[str] = Query(None, description="Filter by salary tier")
) -> List[Dict[str, Any]]:
    """
    Get current team rosters with comprehensive filtering and pagination.
    
    This endpoint provides access to the team_roster_current view, which shows
    current team rosters with player details including gamertag, position,
    salary tier, and role information.
    """
    try:
        # Build query
        query = supabase.get_client().table("team_roster_current").select("*")
        
        # Apply filters
        if team_id:
            query = query.eq("team_id", team_id)
        if player_id:
            query = query.eq("player_id", player_id)
        if is_captain is not None:
            query = query.eq("is_captain", is_captain)
        if is_player_coach is not None:
            query = query.eq("is_player_coach", is_player_coach)
        if position:
            query = query.eq("position", position)
        if salary_tier:
            query = query.eq("salary_tier", salary_tier)
        
        # Apply pagination
        query = query.range(offset, offset + limit - 1)
        
        # Execute query
        result = query.execute()
        
        if not result.data:
            return []
        
        return result.data
        
    except Exception as e:
        logger.error(f"Error retrieving team roster current: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving team roster data"
        )

@router.get(
    "/team/{team_id}",
    response_model=TeamRosterCurrentByTeam,
    responses={
        200: {"description": "Team roster retrieved successfully"},
        404: {"description": "Team not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_team_roster_by_team(
    request: Request,
    team_id: str = Path(..., description="Team ID to get roster for")
) -> Dict[str, Any]:
    """
    Get current roster for a specific team with detailed player information.
    
    Returns the complete roster for a team including all players,
    their roles (captain, coach), positions, and salary information.
    """
    try:
        # Get team roster
        result = supabase.get_client().table("team_roster_current")\
            .select("*")\
            .eq("team_id", team_id)\
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found or has no current roster"
            )
        
        roster_data = result.data
        
        # Get team name from first entry
        team_name = roster_data[0].get("team_name", "Unknown Team")
        
        # Separate players by role
        all_players = roster_data
        captains = [p for p in roster_data if p.get("is_captain")]
        coaches = [p for p in roster_data if p.get("is_player_coach")]
        
        return {
            "team_id": team_id,
            "team_name": team_name,
            "players": all_players,
            "total_players": len(all_players),
            "captains": captains,
            "coaches": coaches
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving team roster for team {team_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving team roster data"
        )

@router.get(
    "/teams",
    response_model=List[TeamRosterCurrentByTeam],
    responses={
        200: {"description": "All team rosters retrieved successfully"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_all_team_rosters(
    request: Request
) -> List[Dict[str, Any]]:
    """
    Get current rosters for all teams.
    
    Returns a list of all teams with their current rosters, organized
    by team with player details and role information.
    """
    try:
        # Get all team rosters
        result = supabase.get_client().table("team_roster_current")\
            .select("*")\
            .execute()
        
        if not result.data:
            return []
        
        # Group by team
        teams = {}
        for player in result.data:
            team_id = player.get("team_id")
            if not team_id:
                continue
                
            if team_id not in teams:
                teams[team_id] = {
                    "team_id": team_id,
                    "team_name": player.get("team_name", "Unknown Team"),
                    "players": [],
                    "captains": [],
                    "coaches": []
                }
            
            teams[team_id]["players"].append(player)
            
            if player.get("is_captain"):
                teams[team_id]["captains"].append(player)
            if player.get("is_player_coach"):
                teams[team_id]["coaches"].append(player)
        
        # Convert to list and add counts
        team_list = []
        for team_data in teams.values():
            team_data["total_players"] = len(team_data["players"])
            team_list.append(team_data)
        
        return team_list
        
    except Exception as e:
        logger.error(f"Error retrieving all team rosters: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving team roster data"
        )

@router.get(
    "/players/{player_id}",
    response_model=List[TeamRosterCurrent],
    responses={
        200: {"description": "Player roster entries retrieved successfully"},
        404: {"description": "Player not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_player_roster_entries(
    request: Request,
    player_id: str = Path(..., description="Player ID to get roster entries for")
) -> List[Dict[str, Any]]:
    """
    Get all current roster entries for a specific player.
    
    Returns all team roster entries for a player, which could include
    multiple teams if the player is on multiple teams.
    """
    try:
        result = supabase.get_client().table("team_roster_current")\
            .select("*")\
            .eq("player_id", player_id)\
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found in any current roster"
            )
        
        return result.data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving roster entries for player {player_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving player roster data"
        )

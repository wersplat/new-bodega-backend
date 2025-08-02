"""
Refactored Matches Router for Supabase Backend

This module provides a clean, RESTful API for managing matches with improved
performance, better error handling, and comprehensive documentation.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from fastapi import (
    APIRouter, Depends, HTTPException, status, 
    Query, Path, Body, Request
)
from pydantic import BaseModel, Field, validator, HttpUrl

from app.core.supabase import supabase
from app.core.auth import get_current_user, get_current_admin_user, RoleChecker
from app.core.rate_limiter import limiter
from app.core.config import settings
from app.schemas.match import (
    MatchStatus, MatchStage, MatchCreate, 
    MatchUpdate, Match, MatchWithDetails,
    PlayerMatchStats, MatchStats
)

import logging

# Initialize router with rate limiting
router = APIRouter(prefix="/matches", tags=["Matches"])

# Configure logging
logger = logging.getLogger(__name__)

# Constants
UUID_PATTERN = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
UUID_EXAMPLE = "123e4567-e89b-12d3-a456-426614174000"

class MatchResponse(Match):
    """Extended match response with additional computed fields."""
    is_live: bool = Field(
        False, 
        description="Whether the match is currently in progress"
    )
    time_elapsed: Optional[str] = Field(
        None,
        description="Time elapsed since match started (if in progress)"
    )

class MatchListResponse(BaseModel):
    """Paginated list of matches with metadata."""
    items: List[MatchResponse] = Field(..., description="List of matches")
    total: int = Field(..., description="Total number of matches matching the query")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    has_more: bool = Field(..., description="Whether there are more items available")

# Helper Functions

def get_match_by_id(match_id: str) -> Dict[str, Any]:
    """
    Retrieve a match by ID with proper error handling.
    
    Args:
        match_id: The UUID of the match to retrieve
        
    Returns:
        Dict[str, Any]: The match data
        
    Raises:
        HTTPException: If the match is not found or an error occurs
    """
    try:
        # Validate UUID format
        import re
        if not re.match(UUID_PATTERN, match_id, re.IGNORECASE):
            logger.warning(f"Invalid match ID format: {match_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid match ID format. Must be a valid UUID."
            )
            
        logger.debug(f"Fetching match with ID: {match_id}")
        result = supabase.get_by_id("matches", match_id)
        
        if not result:
            logger.debug(f"Match not found with ID: {match_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Match with ID {match_id} not found"
            )
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving match {match_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the match"
        )

# API Endpoints

@router.post(
    "/",
    response_model=MatchResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Match created successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Team(s) or event not found"},
        409: {"description": "Conflict with existing data"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def create_match(
    request: Request,
    match: MatchCreate,
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    Create a new match (Admin only).
    
    This endpoint allows administrators to create a new match between two teams,
    optionally associated with an event.
    """
    try:
        logger.info(f"Creating new match between teams {match.team_a_id} and {match.team_b_id}")
        
        # Validate that teams are different
        if match.team_a_id == match.team_b_id:
            logger.warning(f"Attempted to create match with same team for both sides: {match.team_a_id}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Team A and Team B must be different"
            )
        
        client = supabase.get_client()
        
        # Validate teams exist and get their names
        logger.debug(f"Validating teams: {match.team_a_id} and {match.team_b_id}")
        team_a_response = client.table("teams") \
            .select("id, name") \
            .eq("id", str(match.team_a_id)) \
            .execute()
            
        team_b_response = client.table("teams") \
            .select("id, name") \
            .eq("id", str(match.team_b_id)) \
            .execute()
        
        if not team_a_response.data or not team_b_response.data:
            missing_teams = []
            if not team_a_response.data:
                missing_teams.append(f"Team A: {match.team_a_id}")
            if not team_b_response.data:
                missing_teams.append(f"Team B: {match.team_b_id}")
                
            logger.warning(f"Team(s) not found: {', '.join(missing_teams)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"The following teams were not found: {', '.join(missing_teams)}"
            )
        
        team_a = team_a_response.data[0]
        team_b = team_b_response.data[0]
        
        # Validate event exists if provided
        if match.event_id:
            logger.debug(f"Validating event: {match.event_id}")
            event_response = client.table("events") \
                .select("id, name") \
                .eq("id", str(match.event_id)) \
                .execute()
                
            if not event_response.data:
                logger.warning(f"Event not found: {match.event_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Event with ID {match.event_id} not found"
                )
        
        # Prepare match data for insertion
        match_data = match.model_dump()
        match_data["id"] = str(uuid4())
        match_data["team_a_name"] = team_a["name"]
        match_data["team_b_name"] = team_b["name"]
        match_data["status"] = MatchStatus.SCHEDULED.value
        match_data["created_at"] = datetime.utcnow().isoformat()
        
        # Create the match
        result = supabase.insert("matches", match_data)
        
        if not result:
            logger.error(f"Failed to create match: {match_data}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create match"
            )
            
        logger.info(f"Successfully created match: {result.get('id')}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating match: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the match"
        )

@router.get(
    "/",
    response_model=MatchListResponse,
    responses={
        200: {"description": "List of matches matching the criteria"},
        400: {"description": "Invalid query parameters"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_matches(
    request: Request,
    status: Optional[MatchStatus] = Query(
        None, 
        description="Filter matches by status"
    ),
    event_id: Optional[str] = Query(
        None,
        description="Filter matches by event ID",
        pattern=UUID_PATTERN
    ),
    team_id: Optional[str] = Query(
        None,
        description="Filter matches by team ID (returns matches where the team is either team A or team B)",
        pattern=UUID_PATTERN
    ),
    stage: Optional[MatchStage] = Query(
        None,
        description="Filter matches by stage"
    ),
    start_date: Optional[datetime] = Query(
        None,
        description="Filter matches scheduled on or after this date"
    ),
    end_date: Optional[datetime] = Query(
        None,
        description="Filter matches scheduled on or before this date"
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
    ),
    sort_by: str = Query(
        "scheduled_at",
        description="Field to sort results by",
        pattern="^(scheduled_at|played_at|created_at|updated_at|score_a|score_b)$"
    ),
    sort_order: str = Query(
        "desc",
        description="Sort order (asc or desc)",
        pattern="^(asc|desc)$"
    )
) -> Dict[str, Any]:
    """
    List matches with filtering, sorting, and pagination.
    
    Returns a paginated list of matches that match the specified criteria.
    Supports filtering by status, event, team, stage, and date range.
    """
    try:
        logger.info("Listing matches with filters")
        
        # Build the query
        query = supabase.get_client().table("matches").select("*")
        
        # Apply filters
        if status:
            query = query.eq("status", status.value)
        if event_id:
            query = query.eq("event_id", event_id)
        if team_id:
            query = query.or_(f"team_a_id.eq.{team_id},team_b_id.eq.{team_id}")
        if stage:
            query = query.eq("stage", stage.value)
        if start_date:
            query = query.gte("scheduled_at", start_date.isoformat())
        if end_date:
            query = query.lte("scheduled_at", end_date.isoformat())
            
        # Apply sorting
        query = query.order(sort_by, desc=(sort_order.lower() == "desc"))
        
        # Apply pagination
        offset = (page - 1) * size
        query = query.range(offset, offset + size - 1)
        
        # Execute the query
        result = query.execute()
        
        # Get total count for pagination
        count_query = supabase.get_client().table("matches").select("id", count="exact")
        count_result = count_query.execute()
        total = count_result.count if hasattr(count_result, 'count') else 0
        
        # Add computed fields to each match
        matches = []
        now = datetime.utcnow()
        
        for match in (result.data if hasattr(result, 'data') else []):
            # Add is_live field
            match["is_live"] = (
                match.get("status") == MatchStatus.IN_PROGRESS.value and
                match.get("scheduled_at") and
                datetime.fromisoformat(match["scheduled_at"]) <= now
            )
            
            # Add time_elapsed if match is in progress
            if match["is_live"] and match.get("started_at"):
                started_at = datetime.fromisoformat(match["started_at"])
                elapsed = now - started_at
                match["time_elapsed"] = str(elapsed)
                
            matches.append(match)
        
        # Format the response
        return {
            "items": matches,
            "total": total,
            "page": page,
            "size": size,
            "has_more": (offset + len(matches)) < total if total else False
        }
        
    except Exception as e:
        logger.error(f"Error listing matches: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving matches"
        )

@router.get(
    "/{match_id}",
    response_model=MatchWithDetails,
    responses={
        200: {"description": "Match details"},
        404: {"description": "Match not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_match(
    request: Request,
    match_id: str = Path(..., description="The UUID of the match to retrieve", 
                        example=UUID_EXAMPLE, pattern=UUID_PATTERN),
    include_teams: bool = Query(
        True,
        description="Whether to include team details in the response"
    ),
    include_event: bool = Query(
        False,
        description="Whether to include event details in the response"
    ),
    include_stats: bool = Query(
        False,
        description="Whether to include player statistics in the response"
    )
) -> Dict[str, Any]:
    """
    Get match details by ID.
    
    Returns detailed information about a specific match, including
    team details, scores, and match status. Additional related data can be
    included using the query parameters.
    """
    try:
        logger.info(f"Fetching match details for ID: {match_id}")
        
        # Get the base match data
        match = get_match_by_id(match_id)
        
        # Add computed fields
        now = datetime.utcnow()
        match["is_live"] = (
            match.get("status") == MatchStatus.IN_PROGRESS.value and
            match.get("scheduled_at") and
            datetime.fromisoformat(match["scheduled_at"]) <= now
        )
        
        if match["is_live"] and match.get("started_at"):
            started_at = datetime.fromisoformat(match["started_at"])
            elapsed = now - started_at
            match["time_elapsed"] = str(elapsed)
        
        # Include team details if requested
        if include_teams:
            client = supabase.get_client()
            
            # Get team A details
            team_a = client.table("teams") \
                .select("*") \
                .eq("id", match["team_a_id"]) \
                .execute()
            
            # Get team B details
            team_b = client.table("teams") \
                .select("*") \
                .eq("id", match["team_b_id"]) \
                .execute()
            
            match["team_a"] = team_a.data[0] if team_a.data else None
            match["team_b"] = team_b.data[0] if team_b.data else None
            
            # Get winner details if available
            if match.get("winner_id"):
                winner = client.table("teams") \
                    .select("*") \
                    .eq("id", match["winner_id"]) \
                    .execute()
                match["winner"] = winner.data[0] if winner.data else None
        
        # Include event details if requested
        if include_event and match.get("event_id"):
            event = client.table("events") \
                .select("*") \
                .eq("id", match["event_id"]) \
                .execute()
            match["event"] = event.data[0] if event.data else None
        
        # Include player statistics if requested
        if include_stats:
            # Get player stats for the match
            stats = client.table("player_match_stats") \
                .select("*") \
                .eq("match_id", match_id) \
                .execute()
            
            # Separate stats by team
            match["team_a_players"] = [
                s for s in (stats.data if hasattr(stats, 'data') else []) 
                if s.get("team_id") == match["team_a_id"]
            ]
            match["team_b_players"] = [
                s for s in (stats.data if hasattr(stats, 'data') else []) 
                if s.get("team_id") == match["team_b_id"]
            ]
        
        return match
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving match {match_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the match"
        )

@router.put(
    "/{match_id}",
    response_model=MatchResponse,
    responses={
        200: {"description": "Match updated successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Match not found"},
        409: {"description": "Conflict with existing data"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def update_match(
    request: Request,
    match_id: str = Path(..., description="The UUID of the match to update", 
                        example=UUID_EXAMPLE, pattern=UUID_PATTERN),
    match_update: MatchUpdate = ...,
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    Update an existing match (Admin only).
    
    This endpoint allows administrators to update match information, including scores,
    status, and other details. When scores are updated, the winner is automatically
    determined unless explicitly overridden.
    """
    try:
        logger.info(f"Updating match: {match_id}")
        
        # Check if the match exists
        existing_match = get_match_by_id(match_id)
        
        # Prepare update data
        update_data = match_update.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Handle status changes
        if "status" in update_data:
            new_status = update_data["status"]
            
            # If changing to in_progress, set started_at if not already set
            if new_status == MatchStatus.IN_PROGRESS and not existing_match.get("started_at"):
                update_data["started_at"] = datetime.utcnow().isoformat()
            
            # If changing to completed, set ended_at if not already set
            if new_status == MatchStatus.COMPLETED and not existing_match.get("ended_at"):
                update_data["ended_at"] = datetime.utcnow().isoformat()
                
                # If scores are not provided, default to 0-0
                if "score_a" not in update_data:
                    update_data["score_a"] = 0
                if "score_b" not in update_data:
                    update_data["score_b"] = 0
                
                # Determine winner if not explicitly set
                if "winner_id" not in update_data:
                    if update_data.get("score_a", 0) > update_data.get("score_b", 0):
                        update_data["winner_id"] = existing_match["team_a_id"]
                        update_data["winner_name"] = existing_match["team_a_name"]
                    elif update_data.get("score_b", 0) > update_data.get("score_a", 0):
                        update_data["winner_id"] = existing_match["team_b_id"]
                        update_data["winner_name"] = existing_match["team_b_name"]
                    # For ties, winner_id remains None
        
        # Update the match
        result = supabase.update("matches", match_id, update_data)
        
        if not result:
            logger.error(f"Failed to update match: {match_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update match"
            )
            
        logger.info(f"Successfully updated match: {match_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating match {match_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the match"
        )

@router.delete(
    "/{match_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Match deleted successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Match not found"},
        409: {"description": "Cannot delete match with stats"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def delete_match(
    request: Request,
    match_id: str = Path(..., description="The UUID of the match to delete", 
                        example=UUID_EXAMPLE, pattern=UUID_PATTERN),
    force: bool = Query(
        False,
        description="Force deletion even if the match has statistics"
    ),
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
) -> None:
    """
    Delete a match (Admin only).
    
    By default, matches with statistics cannot be deleted unless the force
    parameter is set to True.
    """
    try:
        logger.info(f"Deleting match: {match_id} (force={force})")
        
        # Check if the match exists
        match = get_match_by_id(match_id)
        
        # Check for statistics (unless force is True)
        if not force:
            stats = supabase.get_client().table("player_match_stats") \
                .select("id") \
                .eq("match_id", match_id) \
                .limit(1) \
                .execute()
                
            if hasattr(stats, 'data') and stats.data:
                logger.warning(
                    f"Cannot delete match {match_id}: Has {len(stats.data)} player statistics"
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "Cannot delete match with player statistics. "
                        "Set force=true to delete anyway."
                    )
                )
        
        # Delete the match
        result = supabase.delete("matches", match_id)
        
        if not result:
            logger.error(f"Failed to delete match: {match_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete match"
            )
            
        logger.info(f"Successfully deleted match: {match_id}")
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting match {match_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the match"
        )

@router.post(
    "/{match_id}/stats",
    status_code=status.HTTP_200_OK,
    response_model=List[PlayerMatchStats],
    responses={
        200: {"description": "Statistics submitted successfully"},
        400: {"description": "Invalid statistics data"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Match not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def submit_match_stats(
    request: Request,
    match_id: str = Path(..., description="The UUID of the match", 
                        example=UUID_EXAMPLE, pattern=UUID_PATTERN),
    current_user: Dict[str, Any] = Depends(get_current_admin_user),
    stats: List[PlayerMatchStats] = Body(..., description="List of player match statistics")
) -> List[Dict[str, Any]]:
    """
    Submit player statistics for a match (Admin only).
    
    This endpoint allows administrators to submit detailed statistics for
    players in a match. Existing statistics for the same match and players
    will be updated.
    """
    try:
        logger.info(f"Submitting stats for match: {match_id}")
        
        # Check if the match exists
        match = get_match_by_id(match_id)
        
        # Prepare stats data
        stats_data = []
        for stat in stats:
            stat_dict = stat.model_dump()
            stat_dict["match_id"] = match_id
            stat_dict["created_at"] = datetime.utcnow().isoformat()
            stat_dict["updated_at"] = datetime.utcnow().isoformat()
            stats_data.append(stat_dict)
        
        # Upsert the stats
        result = supabase.upsert("player_match_stats", stats_data, on_conflict=["match_id", "player_id"])
        
        if not result:
            logger.error(f"Failed to submit stats for match: {match_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit match statistics"
            )
            
        logger.info(f"Successfully submitted {len(stats_data)} stats for match: {match_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting stats for match {match_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while submitting match statistics"
        )

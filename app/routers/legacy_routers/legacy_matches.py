"""
Matches Router

This module provides API endpoints for managing and querying match data.
It handles operations for creating, reading, updating, and deleting matches,
as well as querying matches by various criteria.

Endpoints:
    POST / - Create a new match
    GET /{match_id} - Get match details by ID
    GET / - List matches with optional filtering
    PUT /{match_id} - Update match information
    DELETE /{match_id} - Delete a match
    GET /team/{team_id} - Get matches for a specific team
    GET /tournament/{tournament_id} - Get matches for a specific tournament

Authentication is required for all write operations (POST, PUT, DELETE).
Rate limiting is applied to all endpoints to prevent abuse.
"""

import logging
import re
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any, Union
from uuid import UUID

from fastapi import (
    APIRouter, Depends, HTTPException, status, Query, Request, Path
)
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4

from app.core.supabase import supabase
from app.core.auth import get_current_active_user, get_current_admin_user
from app.core.rate_limiter import limiter
from app.core.config import settings
from app.schemas.match import (
    MatchCreate, 
    Match as MatchSchema, 
    MatchUpdate, 
    MatchWithDetails,
    MatchStatus,
    MatchStage
)
from app.schemas.player_stats import PlayerStats as PlayerStatsSchema

# Configure logger
logger = logging.getLogger(__name__)

# Constants
UUID_REGEX = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
UUID_EXAMPLE = "123e4567-e89b-12d3-a456-426614174000"

# Initialize router with rate limiting
router = APIRouter(prefix="/matches", tags=["matches"])

async def get_match_by_id(match_id: str) -> Optional[Dict[str, Any]]:
    """
    Helper function to get a match by ID from Supabase with validation and error handling.
    
    Args:
        match_id: The UUID of the match to retrieve
        
    Returns:
        Optional[Dict[str, Any]]: The match data if found, None otherwise
        
    Raises:
        HTTPException: If the match ID is invalid or an error occurs
    """
    try:
        # Validate UUID format
        if not re.match(UUID_REGEX, match_id, re.IGNORECASE):
            logger.warning(f"Invalid match ID format: {match_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid match ID format. Must be a valid UUID."
            )
            
        logger.debug(f"Fetching match with ID: {match_id}")
        result = supabase.fetch_by_id("matches", match_id)
        
        if not result:
            logger.debug(f"Match not found with ID: {match_id}")
            return None
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error retrieving match {match_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the match"
        )

@router.post(
    "/",
    response_model=MatchSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Match created successfully"},
        400: {"description": "Invalid input data or validation error"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Team(s) or tournament not found"},
        409: {"description": "Conflict with existing data (e.g., teams are the same)"},
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
    Create a new match (admin only).
    
    This endpoint allows administrators to create a new match record with the provided details.
    The match can be associated with a tournament and will automatically determine the winner
    based on scores if not explicitly provided.
    
    Args:
        request: The incoming request object (for rate limiting)
        match: The match data to create
        current_user: The authenticated admin user creating the match
        
    Returns:
        Dict[str, Any]: The created match data
        
    Raises:
        HTTPException: If validation fails, teams are not found, or an error occurs
    """
    logger.info(f"Creating new match between teams {match.team_a_id} and {match.team_b_id}")
    
    # Validate that teams exist and are different
    if match.team_a_id == match.team_b_id:
        logger.warning(
            f"Attempted to create match with same team for both sides: {match.team_a_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Team A and Team B must be different"
        )
    
    try:
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
        
        # Validate tournament exists if provided
        if match.tournament_id:
            logger.debug(f"Validating tournament: {match.tournament_id}")
            tournament_response = client.table("tournaments") \
                .select("id, name") \
                .eq("id", str(match.tournament_id)) \
                .execute()
                
            if not tournament_response.data:
                logger.warning(f"Tournament not found: {match.tournament_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tournament with ID {match.tournament_id} not found"
                )
        
        # Prepare match data for insertion
        match_data = match.model_dump(exclude_unset=True)
        match_data["team_a_name"] = team_a["name"]
        match_data["team_b_name"] = team_b["name"]
        
        # Set winner based on scores if not provided
        if match.winner_id is None and match.score_a is not None and match.score_b is not None:
            if match.score_a > match.score_b:
                match_data["winner_id"] = str(match.team_a_id)
                match_data["winner_name"] = team_a["name"]
                logger.debug(f"Team A ({team_a['name']}) set as winner by score")
            elif match.score_b > match.score_a:
                match_data["winner_id"] = str(match.team_b_id)
                match_data["winner_name"] = team_b["name"]
                logger.debug(f"Team B ({team_b['name']}) set as winner by score")
            # If scores are equal, winner remains None (tie)
        elif match.winner_id is not None:
            # Set winner name if winner_id is provided
            winner = team_a if str(match.winner_id) == str(match.team_a_id) else team_b
            match_data["winner_name"] = winner["name"]
            logger.debug(f"Winner explicitly set to: {winner['name']}")
        
        # Set default values
        match_data["created_by"] = str(current_user.id)
        match_data["created_at"] = datetime.now(timezone.utc).isoformat()
        
        if not match.played_at:
            match_data["played_at"] = match_data["created_at"]
            logger.debug("Set played_at to current time")
        
        logger.info(f"Creating match between {team_a['name']} and {team_b['name']}")
        
        # Create the match
        created_match = supabase.insert("matches", match_data)
        
        if not created_match:
            logger.error("Failed to create match in database (no error raised but empty result)")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create match in database"
            )
            
        logger.info(f"Successfully created match with ID: {created_match.get('id')}")
        return created_match
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error creating match: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the match"
        )

@router.get(
    "/{match_id}",
    response_model=MatchWithDetails,
    responses={
        200: {"description": "Match details retrieved successfully"},
        400: {"description": "Invalid match ID format"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Match not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_match(
    request: Request,
    match_id: str = Path(
        ...,
        description="The UUID of the match to retrieve",
        examples=[UUID_EXAMPLE],
        pattern=UUID_REGEX,
        openapi_examples={
            "example1": {"summary": "Sample match ID 1", "value": "123e4567-e89b-12d3-a456-426614174000"},
            "example2": {"summary": "Sample match ID 2", "value": "87654321-4321-8765-4321-876543210987"}
        }
    ),
    include_teams: bool = Query(
        False,
        description="Whether to include full team details in the response"
    ),
    include_tournament: bool = Query(
        False,
        description="Whether to include the full tournament details in the response"
    ),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific match by ID.
    
    This endpoint retrieves comprehensive information about a match, including
    team details, scores, and match status. Additional related data can be
    included using the query parameters.
    
    Args:
        request: The incoming request object (for rate limiting)
        match_id: The UUID of the match to retrieve
        include_teams: Whether to include full team details
        include_tournament: Whether to include the full tournament details
        current_user: The currently authenticated user
        
    Returns:
        Dict[str, Any]: The match details, optionally including related data
        
    Raises:
        HTTPException: If the match is not found or an error occurs
    """
    try:
        logger.info(f"Retrieving match with ID: {match_id}")
        
        # Get the match with basic details
        match = await get_match_by_id(match_id)
        if not match:
            logger.warning(f"Match not found: {match_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Match with ID {match_id} not found"
            )
            
        result = dict(match)  # Create a mutable copy
        client = supabase.get_client()
        
        # Include team details if requested
        if include_teams:
            logger.debug(f"Fetching team details for match {match_id}")
            try:
                team_ids = [str(match["team_a_id"]), str(match["team_b_id"])]
                teams_response = client.table("teams") \
                    .select("*") \
                    .in_("id", team_ids) \
                    .execute()
                
                if hasattr(teams_response, 'data') and teams_response.data:
                    teams = {str(team["id"]): team for team in teams_response.data}
                    result["team_a"] = teams.get(str(match["team_a_id"]))
                    result["team_b"] = teams.get(str(match["team_b_id"]))
                
            except Exception as e:
                logger.error(
                    f"Error fetching team details for match {match_id}: {str(e)}",
                    exc_info=True
                )
                # Don't fail the request if we can't get team details
                result["team_a"] = None
                result["team_b"] = None
        
        # Include tournament details if requested and match has a tournament
        if include_tournament and match.get("tournament_id"):
            logger.debug(f"Fetching tournament details for match {match_id}")
            try:
                tournament_response = client.table("tournaments") \
                    .select("*") \
                    .eq("id", str(match["tournament_id"])) \
                    .single() \
                    .execute()
                
                if hasattr(tournament_response, 'data') and tournament_response.data:
                    result["tournament"] = tournament_response.data
                
            except Exception as e:
                logger.error(
                    f"Error fetching tournament details for match {match_id}: {str(e)}",
                    exc_info=True
                )
                # Don't fail the request if we can't get tournament details
                result["tournament"] = None
        
        logger.info(f"Successfully retrieved match: {match_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error retrieving match {match_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the match"
        )
    return match_with_details

@router.get(
    "/",
    response_model=List[MatchSchema],
    responses={
        200: {"description": "List of matches retrieved successfully"},
        400: {"description": "Invalid query parameters"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        422: {"description": "Validation error for query parameters"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_matches(
    request: Request,
    skip: int = Query(
        0,
        ge=0,
        description="Number of records to skip for pagination",
        example=0
    ),
    limit: int = Query(
        100,
        ge=1,
        le=500,
        description="Maximum number of records to return (1-500)",
        example=100
    ),
    team_id: Optional[UUID] = Query(
        None,
        description="Filter matches by team ID (returns matches where the team is either team A or team B)",
        examples=[UUID_EXAMPLE]
    ),
    tournament_id: Optional[UUID] = Query(
        None,
        description="Filter matches by tournament ID",
        examples=[UUID_EXAMPLE]
    ),
    status: Optional[MatchStatus] = Query(
        None,
        description="Filter matches by status"
    ),
    start_date: Optional[datetime] = Query(
        None,
        description="Filter matches played on or after this date/time",
        example="2023-01-01T00:00:00Z"
    ),
    end_date: Optional[datetime] = Query(
        None,
        description="Filter matches played on or before this date/time",
        example="2023-12-31T23:59:59Z"
    ),
    sort_by: str = Query(
        "played_at",
        description="Field to sort results by",
        example="played_at",
        pattern="^(played_at|created_at|updated_at|score_a|score_b)$"
    ),
    sort_order: str = Query(
        "desc",
        description="Sort order (asc or desc)",
        example="desc",
        pattern="^(asc|desc)$"
    ),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """
    List matches with optional filtering, sorting, and pagination.
    
    This endpoint returns a paginated list of matches that match the specified filters.
    Results can be sorted and paginated for efficient data retrieval.
    
    Args:
        request: The incoming request object (for rate limiting)
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return (1-500)
        team_id: Filter matches by team ID
        tournament_id: Filter matches by tournament ID
        status: Filter matches by status
        start_date: Filter matches played on or after this date/time
        end_date: Filter matches played on or before this date/time
        sort_by: Field to sort results by
        sort_order: Sort order (asc or desc)
        current_user: The currently authenticated user
        
    Returns:
        List[Dict[str, Any]]: A list of match objects
        
    Raises:
        HTTPException: If an error occurs during processing
    """
    try:
        logger.info(
            f"Listing matches with filters - team_id: {team_id}, tournament_id: {tournament_id}, "
            f"status: {status}, start_date: {start_date}, end_date: {end_date}, "
            f"skip: {skip}, limit: {limit}, sort: {sort_by} {sort_order}"
        )
        
        # Build the base query
        query = supabase.get_client().table("matches").select("*")
        
        # Apply filters
        if team_id:
            logger.debug(f"Filtering by team_id: {team_id}")
            query = query.or_(f"team_a_id.eq.{team_id},team_b_id.eq.{team_id}")
        
        if tournament_id:
            logger.debug(f"Filtering by tournament_id: {tournament_id}")
            query = query.eq("tournament_id", str(tournament_id))
            
        if status:
            logger.debug(f"Filtering by status: {status}")
            query = query.eq("status", status.value)
        
        if start_date:
            logger.debug(f"Filtering by start_date: {start_date}")
            query = query.gte("played_at", start_date.isoformat())
        
        if end_date:
            logger.debug(f"Filtering by end_date: {end_date}")
            query = query.lte("played_at", end_date.isoformat())
            
        # Validate date range
        if start_date and end_date and start_date > end_date:
            logger.warning("Invalid date range: start_date is after end_date")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date must be before or equal to end_date"
            )
        
        # Apply sorting
        logger.debug(f"Sorting by {sort_by} in {sort_order} order")
        query = query.order(sort_by, desc=sort_order.lower() == "desc")
        
        # Apply pagination
        logger.debug(f"Applying pagination - skip: {skip}, limit: {limit}")
        query = query.range(skip, skip + limit - 1)
        
        # Execute the query
        logger.debug("Executing database query")
        result = query.execute()
        
        # Process results
        matches = result.data if hasattr(result, 'data') else []
        logger.info(f"Retrieved {len(matches)} matches")
        
        return matches
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error listing matches: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving matches"
        )

@router.put(
    "/{match_id}",
    response_model=MatchSchema,
    responses={
        200: {"description": "Match updated successfully"},
        400: {"description": "Invalid input data or validation error"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Match not found"},
        409: {"description": "Conflict with existing data"},
        422: {"description": "Validation error for input data"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def update_match(
    request: Request,
    match_id: str = Path(
        ...,
        description="The UUID of the match to update",
        examples=[UUID_EXAMPLE],
        pattern=UUID_REGEX
    ),
    match_update: MatchUpdate = ...,
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    Update an existing match (admin only).
    
    This endpoint allows administrators to update match information, including scores,
    status, and other details. When scores are updated, the winner is automatically
    determined unless explicitly overridden.
    
    Args:
        request: The incoming request object (for rate limiting)
        match_id: The UUID of the match to update
        match_update: The updated match data
        current_user: The authenticated admin user making the update
        
    Returns:
        Dict[str, Any]: The updated match data
        
    Raises:
        HTTPException: If the match is not found, validation fails, or an error occurs
    """
    logger.info(f"Updating match with ID: {match_id}")
    
    try:
        # Check if match exists
        match = await get_match_by_id(match_id)
        if not match:
            logger.warning(f"Match not found for update: {match_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Match with ID {match_id} not found"
            )

        # Get the update data, excluding unset fields
        update_data = match_update.model_dump(exclude_unset=True)
        
        # Get team names if teams are being updated
        client = supabase.get_client()
        if "team_a_id" in update_data or "team_b_id" in update_data:
            team_a_id = str(update_data.get("team_a_id", match.get("team_a_id")))
            team_b_id = str(update_data.get("team_b_id", match.get("team_b_id")))
            
            # Check if teams are different
            if team_a_id == team_b_id:
                logger.warning(f"Attempted to update match {match_id} with same team for both sides: {team_a_id}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Team A and Team B must be different"
                )
            
            # Validate teams exist and get their names
            team_ids = list({team_a_id, team_b_id})  # Remove duplicates
            teams_response = client.table("teams") \
                .select("id, name") \
                .in_("id", team_ids) \
                .execute()
            
            if len(teams_response.data) != len(team_ids):
                found_team_ids = {str(team["id"]) for team in teams_response.data}
                missing_teams = [tid for tid in team_ids if tid not in found_team_ids]
                logger.warning(f"Team(s) not found: {', '.join(missing_teams)}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"The following teams were not found: {', '.join(missing_teams)}"
                )
            
            # Update team names in the update data
            teams = {str(team["id"]): team for team in teams_response.data}
            if "team_a_id" in update_data:
                update_data["team_a_name"] = teams[team_a_id]["name"]
            if "team_b_id" in update_data:
                update_data["team_b_name"] = teams[team_b_id]["name"]
        
        # If updating scores, also update the winner if not explicitly set
        if ("score_a" in update_data or "score_b" in update_data) and "winner_id" not in update_data:
            score_a = update_data.get("score_a", match.get("score_a"))
            score_b = update_data.get("score_b", match.get("score_b"))
            
            if score_a is not None and score_b is not None:
                logger.debug(f"Updating winner based on scores: {score_a}-{score_b}")
                if score_a > score_b:
                    update_data["winner_id"] = update_data.get("team_a_id", match["team_a_id"])
                    update_data["winner_name"] = update_data.get("team_a_name", match["team_a_name"])
                    logger.debug(f"Team A ({update_data['winner_name']}) set as winner by score")
                elif score_b > score_a:
                    update_data["winner_id"] = update_data.get("team_b_id", match["team_b_id"])
                    update_data["winner_name"] = update_data.get("team_b_name", match["team_b_name"])
                    logger.debug(f"Team B ({update_data['winner_name']}) set as winner by score")
                else:
                    # If it's a tie, clear the winner
                    update_data["winner_id"] = None
                    update_data["winner_name"] = None
                    logger.debug("Match is a tie, clearing winner")
        
        # If updating the winner, validate it's one of the teams
        if "winner_id" in update_data and update_data["winner_id"] is not None:
            team_a_id = str(update_data.get("team_a_id", match.get("team_a_id")))
            team_b_id = str(update_data.get("team_b_id", match.get("team_b_id")))
            winner_id = str(update_data["winner_id"])
            
            if winner_id not in [team_a_id, team_b_id]:
                logger.warning(f"Invalid winner_id {winner_id} not matching either team")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Winner must be either team_a or team_b"
                )
            
            # Set the winner name
            if winner_id == team_a_id:
                update_data["winner_name"] = update_data.get("team_a_name", match["team_a_name"])
            else:
                update_data["winner_name"] = update_data.get("team_b_name", match["team_b_name"])
            
            logger.debug(f"Winner explicitly set to: {update_data['winner_name']}")
        
        # Add audit fields
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        update_data["updated_by"] = str(current_user.id)
        
        logger.debug(f"Updating match {match_id} with data: {update_data}")
        
        # Update the match
        updated_match = supabase.update("matches", match_id, update_data)
        
        if not updated_match:
            logger.error(f"Failed to update match {match_id} in database (no error raised but empty result)")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update match in database"
            )
        
        logger.info(f"Successfully updated match: {match_id}")
        return updated_match
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error updating match {match_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the match"
        )

@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_match(
    match_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Delete a match
    """
    # Check if match exists
    match = await get_match_by_id(match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Check if user has permission to delete the match
    # Note: Add your permission logic here
    
    try:
        # First, delete all player stats for this match
        client = supabase.get_client()
        client.table("player_stats").delete().eq("match_id", match_id).execute()
        
        # Then delete the match
        supabase.delete("matches", match_id)
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete match: {str(e)}"
        )

@router.get("/team/{team_id}", response_model=List[MatchSchema])
async def get_team_matches(
    team_id: str,
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    """
    Get all matches for a specific team
    """
    client = supabase.get_client()
    result = client.table("matches")\
        .select("*")\
        .or_(f"team_a_id.eq.{team_id},team_b_id.eq.{team_id}")\
        .order("played_at", desc=True)\
        .range(skip, skip + limit - 1)\
        .execute()
    
    return result.data if hasattr(result, 'data') else []

@router.get("/tournament/{tournament_id}", response_model=List[MatchSchema])
async def get_tournament_matches(
    tournament_id: str,
    stage: Optional[str] = None,
    limit: int = Query(100, ge=1, le=200),
    skip: int = Query(0, ge=0)
):
    """
    Get matches for a specific tournament
    """
    client = supabase.get_client()
    query = client.table("matches") \
        .select("*") \
        .eq("tournament_id", tournament_id)
    
    if stage:
        query = query.eq("stage", stage)
    
    result = query.order("played_at", desc=True)\
                 .range(skip, skip + limit - 1)\
                 .execute()
    
    return result.data if hasattr(result, 'data') else []

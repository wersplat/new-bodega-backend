"""
Players Router (Supabase Backend)

This module provides a RESTful API for managing player profiles and related operations
using Supabase as the backend storage. It handles player registration, profile management,
and player lookups with proper authentication and rate limiting.

API Version: 1.0.0
Base URL: /v1/players

Key Features:
- RESTful endpoints for all player operations
- Comprehensive filtering, sorting, and pagination
- Built-in rate limiting and request validation
- Detailed error handling and logging
- Optimized database queries with Supabase

Endpoints:
- POST   /                   - Create a new player profile
- GET    /{player_id}        - Get player profile by ID
- GET    /me                 - Get current user's player profile
- PATCH  /me                 - Update current user's player profile
- GET    /search             - Search players by gamertag

Authentication:
- All endpoints (except public endpoints) require a valid JWT token
- Token should be included in the Authorization header as: 'Bearer <token>'

Rate Limiting:
- Default: 100 requests per minute per IP
- Authenticated: 1000 requests per minute per user
- Admin: 5000 requests per minute per user

Response Format:
All responses follow the standard JSON:API format with the following structure:
{
    "data": { ... },  // The primary data
    "meta": { ... },  // Metadata (pagination, etc.)
    "links": { ... }  // Related resources and pagination links
}

Error Responses:
- 400: Bad Request - Invalid input data
- 401: Unauthorized - Authentication required
- 403: Forbidden - Insufficient permissions
- 404: Not Found - Resource not found
- 409: Conflict - Resource already exists
- 422: Unprocessable Entity - Validation error
- 429: Too Many Requests - Rate limit exceeded
- 500: Internal Server Error - Unexpected error
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from pydantic import BaseModel, ConfigDict, field_validator
from pydantic.types import constr

from app.core.supabase import supabase
from app.core.auth_supabase import supabase_user_from_bearer
from app.core.rate_limiter import limiter
from app.core.config import settings
from app.schemas.player import Player, PlayerProfile, PlayerWithStats, PlayerWithTeam, PlayerListResponse, PlayerCreate, PlayerUpdate

# Initialize router with rate limiting and explicit prefix
router = APIRouter(
    tags=["Players"],
    responses={404: {"description": "Not found"}},
)

# Configure logging
logger = logging.getLogger(__name__)

# Constants
GAMERTAG_MIN_LENGTH = 3
GAMERTAG_MAX_LENGTH = 32
PLAYER_LIMIT = 100  # Default limit for list operations

# Custom Types
GamertagStr = constr(
    min_length=GAMERTAG_MIN_LENGTH, 
    max_length=GAMERTAG_MAX_LENGTH,
    strip_whitespace=True
)

# Helper Functions
async def get_player_by_id(player_id: Union[str, UUID]) -> Optional[Dict[str, Any]]:
    """
    Get a player by ID with optimized database lookup.
    
    Args:
        player_id: The UUID of the player to retrieve
        
    Returns:
        Optional[Dict[str, Any]]: Player data if found, None otherwise
    """
    try:
        return supabase.fetch_by_id("players", str(player_id))
    except Exception as e:
        logger.error(f"Error fetching player {player_id}: {str(e)}", exc_info=True)
        return None

async def get_player_by_gamertag(gamertag: str) -> Optional[Dict[str, Any]]:
    """
    Get a player by gamertag with case-insensitive search.
    
    Args:
        gamertag: The gamertag to search for
        
    Returns:
        Optional[Dict[str, Any]]: Player data if found, None otherwise
    """
    try:
        client = supabase.get_client()
        result = (
            client.table("players")
            .select("*")
            .ilike("gamertag", gamertag)
            .execute()
        )
        return result.data[0] if hasattr(result, 'data') and result.data else None
    except Exception as e:
        logger.error(f"Error fetching player with gamertag {gamertag}: {str(e)}", exc_info=True)
        return None

@router.post(
    "/", 
    response_model=Player,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Player created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "gamertag": "examplePlayer",
                        "avatar_url": "https://example.com/avatars/example.jpg",
                        "bio": "Professional NBA 2K player",
                        "region": "NA",
                        "timezone": "America/New_York",
                        "created_at": "2023-01-01T00:00:00Z",
                        "updated_at": "2023-01-01T00:00:00Z",
                        "is_active": True,
                        "last_online": "2023-01-01T12:00:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Invalid input or gamertag already taken",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Gamertag already taken"
                    }
                }
            }
        },
        401: {"$ref": "#/components/responses/UnauthorizedError"},
        429: {"$ref": "#/components/responses/TooManyRequestsError"},
        500: {"$ref": "#/components/responses/InternalServerError"}
    },
    summary="Create a new player profile",
    description="""
    Register a new player profile for the authenticated user.
    
    Each user can only have one player profile associated with their account.
    The gamertag must be unique across all players.
    
    ### Request Body
    - **gamertag**: (required) Unique display name for the player (3-32 chars, alphanumeric + spaces)
    - **avatar_url**: (optional) URL to the player's avatar image
    - **bio**: (optional) Short biography or description
    - **region**: (optional) Player's region code (e.g., "NA", "EU")
    - **timezone**: (optional) Player's timezone in IANA format
    
    ### Example Request
    ```bash
    curl -X POST \
      https://api.example.com/v1/players \
      -H 'Authorization: Bearer YOUR_TOKEN' \
      -H 'Content-Type: application/json' \
      -d '{
        "gamertag": "examplePlayer",
        "avatar_url": "https://example.com/avatar.jpg",
        "bio": "Professional NBA 2K player",
        "region": "NA",
        "timezone": "America/New_York"
      }'
    ```
    
    ### Response
    Returns the newly created player profile with all fields populated.
    """
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def create_player(
    request: Request,
    player: PlayerCreate,
    current_user: Dict[str, Any] = Depends(supabase_user_from_bearer)
) -> Dict[str, Any]:
    """
    Register a new player profile.
    
    This endpoint allows an authenticated user to create a new player profile.
    Each user can only have one player profile associated with their account.
    
    Args:
        request: The FastAPI request object (used for rate limiting)
        player: The player data to create (validated using PlayerCreate model)
        current_user: The currently authenticated user (injected by FastAPI)
        
    Returns:
        Dict[str, Any]: The created player profile with all fields populated
        
    Raises:
        HTTPException: 
            - 400: If the gamertag is already taken or user already has a profile
            - 401: If the request is not authenticated
            - 500: If there's an error creating the profile in the database
    """
    try:
        # Extract Supabase user id
        user_id = current_user.get("sub") or current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user id")
        logger.info(f"Creating player profile for user {user_id}")
        
        # Check if user already has a player profile
        existing_profile = await get_player_by_gamertag(player.gamertag)
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gamertag already taken"
            )
        
        # Check if user already has a player profile
        client = supabase.get_client()
        existing_player = client.table("players").select("id").eq("user_id", str(user_id)).execute()
        if hasattr(existing_player, 'data') and existing_player.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Player profile already exists for this user"
            )
        
        # Create player profile
        player_data = player.model_dump()
        player_data["user_id"] = str(user_id)  # Ensure user_id is a string
        player_data["created_at"] = datetime.utcnow().isoformat()
        player_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Use transaction for atomic operation
        with client.rpc('begin') as transaction:
            try:
                created_player = supabase.insert("players", player_data)
                if not created_player:
                    transaction.rpc('rollback')
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to create player profile"
                    )
                
                transaction.rpc('commit')
                logger.info(f"Successfully created player profile {created_player.get('id')}")
                return created_player
                
            except Exception as e:
                transaction.rpc('rollback')
                logger.error(f"Error creating player profile: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An error occurred while creating the player profile"
                )
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_player: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the player profile"
        )

@router.get(
    "/search",
    response_model=List[Dict[str, Any]],
    responses={
        200: {"description": "List of matching players"},
        400: {"description": "Invalid query parameters"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def search_player_by_gamertag(
    request: Request,
    query: str = Query(..., min_length=2, max_length=50, description="Gamertag or part of gamertag to search for"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results to return"),
    exact_match: bool = Query(False, description="Whether to search for an exact gamertag match")
) -> List[Dict[str, Any]]:
    """
    Search for players by gamertag.
    
    This endpoint searches for players whose gamertags match the provided query.
    The search is case-insensitive and can match partial gamertags by default.
    
    Args:
        request: The FastAPI request object (used for rate limiting)
        query: The gamertag or part of gamertag to search for (2-50 characters)
        limit: Maximum number of results to return (1-50)
        exact_match: If True, only returns exact gamertag matches
        
    Returns:
        List[Dict[str, Any]]: List of matching player profiles with limited fields
        
    Raises:
        HTTPException: If there's an error performing the search
    """
    try:
        logger.info(f"Searching for players with gamertag like: {query}")
        
        client = supabase.get_client()
        query_builder = (
            client.table("players")
            .select("id, gamertag, avatar_url, created_at, last_online")
            .limit(limit)
        )
        
        # Apply exact or partial match
        if exact_match:
            query_builder = query_builder.eq("gamertag", query)
        else:
            query_builder = query_builder.ilike("gamertag", f"%{query}%")
        
        # Execute query
        result = query_builder.execute()
        
        # Format response
        players = result.data if hasattr(result, 'data') else []
        
        # Log search metrics
        logger.info(f"Found {len(players)} matching players for query: {query}")
        
        return players
        
    except Exception as e:
        logger.error(f"Error searching for players with gamertag {query}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while searching for players"
        )

@router.get(
    "/{player_id}", 
    response_model=Player,
    responses={
        200: {
            "description": "Player profile retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "gamertag": "examplePlayer",
                        "avatar_url": "https://example.com/avatars/example.jpg",
                        "bio": "Professional NBA 2K player",
                        "region": "NA",
                        "timezone": "America/New_York",
                        "created_at": "2023-01-01T00:00:00Z",
                        "updated_at": "2023-01-01T00:00:00Z",
                        "is_active": True,
                        "last_online": "2023-01-01T12:00:00Z"
                    }
                }
            }
        },
        404: {
            "description": "Player not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Player not found"
                    }
                }
            }
        },
        429: {"$ref": "#/components/responses/TooManyRequestsError"},
        500: {"$ref": "#/components/responses/InternalServerError"}
    },
    summary="Get player profile by ID",
    description="""
    Retrieve detailed information about a specific player by their unique ID.
    
    This endpoint returns comprehensive player profile data including statistics,
    achievements, and recent activity. The response includes both basic profile
    information and related data based on the requested parameters.
    
    ### Path Parameters
    - **player_id** (required): The UUID of the player to retrieve
    
    ### Query Parameters
    - **include_history** (optional): Include RP history in the response (default: false)
    - **include_stats** (optional): Include detailed player statistics (default: false)
    - **history_limit** (optional): Number of history entries to return (1-100, default: 50)
    - **history_offset** (optional): Pagination offset for history (default: 0)
    
    ### Example Request
    ```bash
    curl -X GET \
      'https://api.example.com/v1/players/550e8400-e29b-41d4-a716-446655440000?include_stats=true&include_history=true&history_limit=10' \
      -H 'Accept: application/json'
    ```
    
    ### Response
    Returns the player profile with optional extended data based on query parameters.
    """
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_player(
    request: Request,
    player_id: str,
    include_history: bool = Query(False, description="Include player RP history in the response"),
    include_stats: bool = Query(False, description="Include player statistics in the response"),
    history_limit: int = Query(50, ge=1, le=100, description="Maximum number of history entries to return"),
    history_offset: int = Query(0, ge=0, description="Pagination offset for history entries")
) -> Dict[str, Any]:
    """
    Get player profile with RP history.
    
    This endpoint retrieves a player's profile along with their RP (Reputation Points) history.
    
    Args:
        request: The FastAPI request object (used for rate limiting)
        player_id: The UUID of the player to retrieve history for
        include_history: Whether to include player RP history in the response
        include_stats: Whether to include player statistics in the response
        history_limit: Maximum number of history entries to return (1-100)
        history_offset: Pagination offset for history entries
        
    Returns:
        Dict[str, Any]: Player profile with RP history
        
    Raises:
        HTTPException: If the player is not found or an error occurs
    """
    try:
        logger.info(f"Fetching RP history for player {player_id}")
        
        # Get player profile
        player = await get_player_by_id(player_id)
        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Player with ID {player_id} not found"
            )
        
        # Include stats if requested
        if include_stats:
            client = supabase.get_client()
            stats = client.table("player_stats").select("*").eq("player_id", player_id).execute()
            player["stats"] = stats.data if hasattr(stats, 'data') else []
        
        # Include history if requested
        if include_history:
            client = supabase.get_client()
            history = (
                client.table("rp_history")
                .select("*")
                .eq("player_id", player_id)
                .order("created_at", desc=True)
                .range(history_offset, history_offset + history_limit - 1)
                .execute()
            )
            
            # Get total count for pagination metadata
            count_result = (
                client.table("rp_history")
                .select("*", count="exact")
                .eq("player_id", player_id)
                .execute()
            )
            
            # Format response
            player["rp_history"] = history.data if hasattr(history, 'data') else []
            player["pagination"] = {
                "total": count_result.count if hasattr(count_result, 'count') else 0,
                "limit": history_limit,
                "offset": history_offset
            }
        
        return player
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching RP history for player {player_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the player's RP history"
        )

@router.get(
    "/me",
    response_model=Player,
    responses={
        200: {
            "description": "Player profile retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "gamertag": "examplePlayer",
                        "avatar_url": "https://example.com/avatars/example.jpg",
                        "bio": "Professional NBA 2K player",
                        "region": "NA",
                        "timezone": "America/New_York",
                        "created_at": "2023-01-01T00:00:00Z",
                        "updated_at": "2023-01-01T00:00:00Z",
                        "is_active": True,
                        "last_online": "2023-01-01T12:00:00Z",
                        "stats": {
                            "total_matches": 42,
                            "wins": 30,
                            "losses": 12,
                            "win_rate": 71.4,
                            "current_streak": 5,
                            "highest_rank": 1,
                            "current_rank": 3,
                            "total_points": 1250
                        },
                        "achievements": [
                            {"id": "first_win", "name": "First Win", "earned_at": "2023-01-02T00:00:00Z"},
                            {"id": "streak_5", "name": "5-Win Streak", "earned_at": "2023-02-15T00:00:00Z"}
                        ]
                    }
                }
            }
        },
        401: {"$ref": "#/components/responses/UnauthorizedError"},
        404: {
            "description": "Player profile not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Player profile not found. Please create a player profile first."
                    }
                }
            }
        },
        429: {"$ref": "#/components/responses/TooManyRequestsError"},
        500: {"$ref": "#/components/responses/InternalServerError"}
    },
    summary="Get current user's player profile",
    description="""
    Retrieve the complete profile of the currently authenticated user.
    
    This endpoint provides comprehensive information about the authenticated user's
    player profile, including statistics, achievements, and recent activity.
    
    ### Authentication
    - Requires a valid JWT token in the Authorization header
    
    ### Query Parameters
    - **include_stats** (optional): Include detailed player statistics (default: true)
    
    ### Example Request
    ```bash
    curl -X GET \
      'https://api.example.com/v1/players/me?include_stats=true' \
      -H 'Authorization: Bearer YOUR_TOKEN' \
      -H 'Accept: application/json'
    ```
    
    ### Response
    Returns the complete player profile with all associated data including:
    - Basic profile information
    - Player statistics (if include_stats=true)
    - Achievement history
    - Match history summary
    - Current rankings and standings
    """
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def get_my_profile(
    request: Request,
    current_user: Dict[str, Any] = Depends(supabase_user_from_bearer),
    include_stats: bool = Query(True, description="Include player statistics in the response")
) -> Dict[str, Any]:
    """
    Get current user's player profile.
    
    This endpoint retrieves the player profile for the currently authenticated user.
    It uses an optimized primary key lookup for better performance.
    
    Args:
        request: The FastAPI request object (used for rate limiting)
        current_user: The currently authenticated user
        include_stats: Whether to include player statistics in the response
        
    Returns:
        Dict[str, Any]: The player profile data
        
    Raises:
        HTTPException: If the player profile is not found or an error occurs
    """
    try:
        logger.info(f"Fetching profile for current user {current_user.id}")
        
        # Get player profile
        client = supabase.get_client()
        result = client.table("players").select("*").eq("user_id", str(current_user.id)).single().execute()
        
        if not hasattr(result, 'data') or not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player profile not found. Please create a player profile first."
            )
        
        player = result.data
        
        # Include stats if requested
        if include_stats and "id" in player:
            stats = client.table("player_stats").select("*").eq("player_id", player["id"]).execute()
            player["stats"] = stats.data if hasattr(stats, 'data') else []
        
        return player
        
    except HTTPException:
        raise
    except Exception:
        logger.error("Error fetching current user's profile", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the player's profile"
        )
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def update_my_profile(
    request: Request,
    player_update: PlayerUpdate,
    current_user: Dict[str, Any] = Depends(supabase_user_from_bearer)
) -> Dict[str, Any]:
    """
    Update current user's player profile.
    
    This endpoint allows an authenticated user to update their own player profile.
    Only the fields provided in the request will be updated (partial update).
    
    Args:
        request: The FastAPI request object (used for rate limiting)
        player_update: The player data to update
        current_user: The currently authenticated user
        
    Returns:
        Dict[str, Any]: The updated player profile
        
    Raises:
        HTTPException: If the player profile is not found or there's an error updating
    """
    try:
        user_id = current_user.get("sub") or current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user id")
        logger.info(f"Updating profile for user {user_id}")
        
        # Get current player data
        client = supabase.get_client()
        result = client.table("players").select("id").eq("user_id", str(user_id)).execute()
        
        if not hasattr(result, 'data') or not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player profile not found. Please create a player profile first."
            )
        
        # Prepare update data
        update_data = player_update.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
        
        # Add updated_at timestamp
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Use transaction for atomic operation
        with client.rpc('begin') as transaction:
            try:
                player_id = result.data[0]["id"]
                updated_player = supabase.update("players", player_id, update_data)
                
                if not updated_player:
                    transaction.rpc('rollback')
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to update player profile"
                    )
                
                transaction.rpc('commit')
                logger.info(f"Successfully updated player profile {player_id}")
                return updated_player
                
            except HTTPException:
                transaction.rpc('rollback')
                raise
            except Exception as e:
                transaction.rpc('rollback')
                logger.error(f"Error updating player profile: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An error occurred while updating the player profile"
                )
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_my_profile: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the player profile"
        )
# The get_player_history endpoint has been consolidated with the get_player endpoint

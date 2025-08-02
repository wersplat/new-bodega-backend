"""
Players Router

This module provides API endpoints for managing player profiles and related operations.
It handles player registration, profile management, and player lookups using Supabase as the backend.

Endpoints:
- POST /: Create a new player profile
- GET /{player_id}: Get player by ID
- GET /me/profile: Get current user's player profile
- PATCH /me/profile: Update current user's player profile
- GET /{player_id}/history: Get player's RP history
- GET /search: Search for players by gamertag
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from pydantic import BaseModel, Field

from app.core.supabase import supabase
from app.core.auth import get_current_active_user, RoleChecker
from app.core.rate_limiter import limiter
from app.core.config import settings
from app.schemas.player import (
    PlayerCreate, 
    Player as PlayerSchema, 
    PlayerProfile, 
    PlayerUpdate, 
    PlayerWithHistory, 
    RPHistory
)

# Initialize router with rate limiting
router = APIRouter(prefix="/players", tags=["Players"])

# Configure logging
logger = logging.getLogger(__name__)

async def get_player_by_id(player_id: str) -> Optional[Dict[str, Any]]:
    """
    Helper function to get a player by ID from Supabase using optimized primary key lookup.
    
    Args:
        player_id: The UUID of the player to retrieve
        
    Returns:
        Optional[Dict[str, Any]]: Player data if found, None otherwise
    """
    try:
        return supabase.fetch_by_id("players", player_id)
    except Exception as e:
        logger.error(f"Error fetching player {player_id}: {str(e)}", exc_info=True)
        return None

async def get_player_by_gamertag(gamertag: str) -> Optional[Dict[str, Any]]:
    """
    Helper function to get a player by gamertag from Supabase.
    
    Args:
        gamertag: The gamertag to search for
        
    Returns:
        Optional[Dict[str, Any]]: Player data if found, None otherwise
    """
    try:
        client = supabase.get_client()
        result = client.table("players").select("*").eq("gamertag", gamertag).execute()
        return result.data[0] if hasattr(result, 'data') and result.data else None
    except Exception as e:
        logger.error(f"Error fetching player with gamertag {gamertag}: {str(e)}", exc_info=True)
        return None

@router.post(
    "/", 
    response_model=PlayerSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Player created successfully"},
        400: {"description": "Invalid input or gamertag already taken"},
        401: {"description": "Not authenticated"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def create_player(
    request: Request,
    player: PlayerCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Register a new player profile.
    
    This endpoint allows an authenticated user to create a new player profile.
    Each user can only have one player profile associated with their account.
    
    Args:
        request: The FastAPI request object (used for rate limiting)
        player: The player data to create
        current_user: The currently authenticated user
        
    Returns:
        Dict[str, Any]: The created player profile
        
    Raises:
        HTTPException: If the gamertag is already taken or there's an error creating the profile
    """
    try:
        logger.info(f"Creating player profile for user {current_user.id}")
        
        # Check if user already has a player profile
        existing_profile = await get_player_by_gamertag(player.gamertag)
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gamertag already taken"
            )
        
        # Check if user already has a player profile
        client = supabase.get_client()
        existing_player = client.table("players").select("id").eq("user_id", str(current_user.id)).execute()
        if hasattr(existing_player, 'data') and existing_player.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Player profile already exists for this user"
            )
        
        # Create player profile
        player_data = player.model_dump()
        player_data["user_id"] = str(current_user.id)  # Ensure user_id is a string
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
    "/{player_id}", 
    response_model=PlayerSchema,
    responses={
        200: {"description": "Player profile retrieved successfully"},
        404: {"description": "Player not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_player(
    request: Request,
    player_id: str,
    include_stats: bool = Query(False, description="Include player statistics in the response")
) -> Dict[str, Any]:
    """
    Get player profile by ID.
    
    This endpoint retrieves a player's profile information by their unique ID.
    Optionally includes player statistics if requested.
    
    Args:
        request: The FastAPI request object (used for rate limiting)
        player_id: The UUID of the player to retrieve
        include_stats: Whether to include player statistics in the response
        
    Returns:
        Dict[str, Any]: The player profile data
        
    Raises:
        HTTPException: If the player is not found or an error occurs
    """
    try:
        logger.info(f"Fetching player profile for ID: {player_id}")
        
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
        
        return player
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching player {player_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the player profile"
        )

@router.get(
    "/me/profile", 
    response_model=PlayerSchema,
    responses={
        200: {"description": "Player profile retrieved successfully"},
        401: {"description": "Not authenticated"},
        404: {"description": "Player profile not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def get_my_profile(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
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
    except Exception as e:
        logger.error(f"Error fetching profile for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving your player profile"
        )

@router.patch(
    "/me/profile", 
    response_model=PlayerSchema,
    responses={
        200: {"description": "Player profile updated successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Not authenticated"},
        404: {"description": "Player profile not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def update_my_profile(
    request: Request,
    player_update: PlayerUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
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
        logger.info(f"Updating profile for user {current_user.id}")
        
        # Get current player data
        client = supabase.get_client()
        result = client.table("players").select("id").eq("user_id", str(current_user.id)).execute()
        
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

@router.get(
    "/{player_id}/history",
    response_model=PlayerWithHistory,
    responses={
        200: {"description": "Player profile with RP history retrieved successfully"},
        404: {"description": "Player not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_player_history(
    request: Request,
    player_id: str,
    limit: int = Query(50, ge=1, le=100, description="Maximum number of history entries to return"),
    offset: int = Query(0, ge=0, description="Pagination offset")
) -> Dict[str, Any]:
    """
    Get player profile with RP history.
    
    This endpoint retrieves a player's profile along with their RP (Reputation Points) history.
    The history is paginated and ordered by creation date in descending order.
    
    Args:
        request: The FastAPI request object (used for rate limiting)
        player_id: The UUID of the player to retrieve history for
        limit: Maximum number of history entries to return (1-100)
        offset: Pagination offset for history entries
        
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
        
        # Get RP history with pagination
        client = supabase.get_client()
        history = (
            client.table("rp_history")
            .select("*")
            .eq("player_id", player_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
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
            "limit": limit,
            "offset": offset
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

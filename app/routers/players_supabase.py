"""
Players router for player profile management and lookups using Supabase
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.core.supabase import supabase
from app.core.auth import get_current_active_user
from app.schemas.player import PlayerCreate, Player as PlayerSchema, PlayerProfile, PlayerUpdate, PlayerWithHistory, RPHistory

router = APIRouter()

async def get_player_by_id(player_id: str) -> Optional[Dict[str, Any]]:
    """Helper function to get a player by ID from Supabase"""
    result = supabase.fetch_by_id("players", player_id)
    return result

async def get_player_by_gamertag(gamertag: str) -> Optional[Dict[str, Any]]:
    """Helper function to get a player by gamertag from Supabase"""
    client = supabase.get_client()
    result = client.table("players").select("*").eq("gamertag", gamertag).execute()
    if hasattr(result, 'data') and result.data:
        return result.data[0]
    return None

@router.post("/", response_model=PlayerSchema)
async def create_player(
    player: PlayerCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Register a new player profile
    """
    # Check if user already has a player profile
    existing_player = await get_player_by_gamertag(player.gamertag)
    if existing_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gamertag already taken"
        )
    
    # Create player profile
    player_data = player.model_dump()
    player_data["user_id"] = current_user.id  # Link to the authenticated user
    
    try:
        created_player = supabase.insert("players", player_data)
        return created_player
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create player: {str(e)}"
        )

@router.get("/{player_id}", response_model=PlayerSchema)
async def get_player(player_id: str):
    """
    Get player profile by ID
    """
    player = await get_player_by_id(player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    return player

@router.get("/me/profile", response_model=PlayerSchema)
async def get_my_profile(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get current user's player profile
    """
    client = supabase.get_client()
    result = client.table("players").select("*").eq("user_id", str(current_user.id)).execute()
    
    if not hasattr(result, 'data') or not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player profile not found"
        )
    
    return result.data[0]

@router.patch("/me/profile", response_model=PlayerSchema)
async def update_my_profile(
    player_update: PlayerUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Update current user's player profile
    """
    client = supabase.get_client()
    
    # Get current player data
    result = client.table("players").select("id").eq("user_id", str(current_user.id)).execute()
    if not hasattr(result, 'data') or not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player profile not found"
        )
    
    player_id = result.data[0]['id']
    
    # Update only the fields that were provided
    update_data = player_update.model_dump(exclude_unset=True)
    
    try:
        updated_player = supabase.update("players", player_id, update_data)
        return updated_player
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update player: {str(e)}"
        )

@router.get("/{player_id}/history", response_model=PlayerWithHistory)
async def get_player_history(player_id: str):
    """
    Get player profile with RP history
    """
    # Get player
    player = await get_player_by_id(player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    # Get RP history (assuming there's an rp_history table)
    client = supabase.get_client()
    try:
        result = client.table("rp_history").select("*").eq("player_id", player_id).execute()
        history = result.data if hasattr(result, 'data') else []
    except:
        # If the table doesn't exist or there's an error, return empty history
        history = []
    
    return PlayerWithHistory(**player, rp_history=history)

@router.get("/search/{gamertag}", response_model=List[PlayerSchema])
async def search_player_by_gamertag(gamertag: str):
    """
    Search for player by gamertag
    """
    client = supabase.get_client()
    
    # Use ilike for case-insensitive search if available, otherwise use eq
    try:
        result = client.table("players").select("*").ilike("gamertag", f"%{gamertag}%").execute()
    except:
        # Fallback to exact match if ilike is not available
        result = client.table("players").select("*").eq("gamertag", gamertag).execute()
    
    return result.data if hasattr(result, 'data') else []

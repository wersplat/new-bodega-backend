"""
Players router for player profile management and lookups using Supabase
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.core.supabase import supabase
from app.core.auth import get_current_active_user
from app.schemas.player import PlayerCreate, Player as PlayerSchema, PlayerProfile, PlayerUpdate, PlayerWithHistory, RPHistory

router = APIRouter()

def get_player_by_id(player_id: str) -> Optional[Dict[str, Any]]:
    """Helper function to get a player by ID from Supabase using optimized primary key lookup"""
    return supabase.fetch_by_id("players", player_id)

def get_player_by_gamertag(gamertag: str) -> Optional[Dict[str, Any]]:
    """Helper function to get a player by gamertag from Supabase"""
    client = supabase.get_client()
    result = client.table("players").select("*").eq("gamertag", gamertag).execute()
    return result.data[0] if hasattr(result, 'data') and result.data else None

@router.post("/", response_model=PlayerSchema)
def create_player(
    player: PlayerCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Register a new player profile
    """
    # Check if user already has a player profile
    existing_player = get_player_by_gamertag(player.gamertag)
    if existing_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gamertag already taken"
        )
    
    # Create player profile
    player_data = player.model_dump()
    player_data["user_id"] = str(current_user.id)  # Ensure user_id is a string
    
    created_player = supabase.insert("players", player_data)
    if not created_player:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create player"
        )
    return created_player

@router.get("/{player_id}", response_model=PlayerSchema)
def get_player(player_id: str):
    """
    Get player profile by ID
    """
    player = get_player_by_id(player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    return player

@router.get("/me/profile", response_model=PlayerSchema)
def get_my_profile(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get current user's player profile using optimized primary key lookup
    """
    # First try to find the player by user_id
    client = supabase.get_client()
    result = client.table("players").select("*").eq("user_id", str(current_user.id)).single().execute()
    
    if not hasattr(result, 'data') or not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player profile not found"
        )
    
    return result.data

@router.patch("/me/profile", response_model=PlayerSchema)
def update_my_profile(
    player_update: PlayerUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Update current user's player profile
    """
    # Get current player data
    client = supabase.get_client()
    result = client.table("players").select("id").eq("user_id", str(current_user.id)).execute()
    
    if not hasattr(result, 'data') or not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player profile not found"
        )
    
    player_id = result.data[0]["id"]
    update_data = player_update.model_dump(exclude_unset=True)
    
    # Update the player profile
    updated_player = supabase.update("players", player_id, update_data)
    if not updated_player:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update player profile"
        )
    return updated_player

@router.get("/{player_id}/history", response_model=PlayerWithHistory)
def get_player_history(player_id: str):
    """
    Get player profile with RP history
    """
    # Get player data
    player = get_player_by_id(player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    # Get RP history
    client = supabase.get_client()
    history_result = client.table("rp_history").select("*").eq("player_id", player_id).order("created_at", desc=True).execute()
    
    history = []
    if hasattr(history_result, 'data') and history_result.data:
        history = [RPHistory(**item) for item in history_result.data]
    
    return PlayerWithHistory(
        **player,
        rp_history=history
    )

@router.get("/search/{gamertag}", response_model=List[PlayerSchema])
def search_player_by_gamertag(gamertag: str):
    """
    Search for player by gamertag
    """
    client = supabase.get_client()
    result = client.table("players").select("*").ilike("gamertag", f"%{gamertag}%").limit(10).execute()
    
    return result.data if hasattr(result, 'data') and result.data else []

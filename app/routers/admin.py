"""
Admin router for RP updates and badge assignment using Supabase
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.core.auth import get_current_admin_user
from app.core.auth_supabase import require_admin_api_token
from app.core.supabase import supabase
from app.schemas.user import UserInDB
from app.schemas.player import PlayerProfile

# Request/Response models
class AdminCheckRequest(BaseModel):
    user_id: str
    email: Optional[str] = None

class AdminCheckResponse(BaseModel):
    is_admin: bool
    user_id: str
    email: Optional[str] = None

class RPUpdateRequest(BaseModel):
    player_id: str  # UUID as string
    rp_change: int
    reason: str

class BadgeAwardRequest(BaseModel):
    player_wallet: str  # Wallet address
    badge_type: str  # Badge type identifier
    match_id: int  # Match ID where badge was earned
    league_id: Optional[str] = None
    tournament_id: Optional[str] = None
    season_id: Optional[str] = None

class PlayerBadgeResponse(BaseModel):
    id: str  # UUID as string
    player_wallet: str  # Wallet address
    badge_type: str  # Badge type
    match_id: int  # Match ID
    league_id: Optional[str] = None
    tournament_id: Optional[str] = None
    season_id: Optional[str] = None
    ipfs_uri: Optional[str] = None
    token_id: Optional[int] = None
    tx_hash: Optional[str] = None
    created_at: str

# Helper function to calculate rank based on RP
def calculate_rank(rp: int) -> str:
    if rp >= 2000:
        return "Challenger"
    elif rp >= 1800:
        return "Grandmaster"
    elif rp >= 1600:
        return "Master"
    elif rp >= 1400:
        return "Diamond"
    elif rp >= 1200:
        return "Platinum"
    elif rp >= 1000:
        return "Gold"
    elif rp >= 800:
        return "Silver"
    elif rp >= 600:
        return "Bronze"
    else:
        return "Iron"

# Initialize router with explicit prefix and standardized tags
router = APIRouter(
    tags=["Admin"],
    responses={404: {"description": "Not found"}},
)

# Public admin check endpoint (no admin auth required)
@router.post("/check-public", response_model=AdminCheckResponse)
async def check_admin_status_public(
    admin_check: AdminCheckRequest
):
    """
    Check if a user has admin privileges (public endpoint)
    """
    try:
        # Check if user email is in admin list
        admin_emails = [
            'christian@bodegacatsgc.gg',
            'admin@bodegacatsgc.gg',
            # Add more admin emails as needed
        ]
        
        is_admin_email = admin_check.email and admin_check.email.lower() in admin_emails
        
        return AdminCheckResponse(
            is_admin=is_admin_email,
            user_id=admin_check.user_id,
            email=admin_check.email
        )
    except Exception:
        return AdminCheckResponse(
            is_admin=False,
            user_id=admin_check.user_id,
            email=admin_check.email
        )

# Protected admin endpoints (require admin authentication)
@router.post("/check", response_model=AdminCheckResponse)
async def check_admin_status(
    admin_check: AdminCheckRequest,
    current_user: UserInDB = Depends(get_current_admin_user)
):
    """
    Check if a user has admin privileges
    """
    try:
        # If the current user can access this endpoint, they are an admin
        # This endpoint is protected by get_current_admin_user dependency
        return AdminCheckResponse(
            is_admin=True,
            user_id=admin_check.user_id,
            email=admin_check.email
        )
    except Exception:
        # If there's any error (like authentication failure), user is not admin
        return AdminCheckResponse(
            is_admin=False,
            user_id=admin_check.user_id,
            email=admin_check.email
        )

@router.post("/update-rp")
async def update_player_rp(
    rp_update: RPUpdateRequest,
    _: None = Depends(require_admin_api_token)
):
    """
    Update player RP (admin only)
    """
    try:
        # Find player in Supabase
        player_result = supabase.get_client().table("players").select("*").eq("id", rp_update.player_id).single().execute()
        
        if not player_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found"
            )
        
        player = player_result.data
        
        # Store old RP
        old_rp = player.get("current_rp", 0)
        
        # Calculate new RP
        new_rp = old_rp + rp_update.rp_change
        
        # Get peak RP
        peak_rp = player.get("peak_rp", old_rp)
        
        # Update peak RP if necessary
        if new_rp > peak_rp:
            peak_rp = new_rp
        
        # Update player in Supabase
        supabase.get_client().table("players").update({
            "current_rp": new_rp,
            "peak_rp": peak_rp
        }).eq("id", rp_update.player_id).execute()
        
        # Create RP history entry
        now = datetime.utcnow().isoformat()
        history_id = str(uuid.uuid4())
        
        supabase.get_client().table("rp_history").insert({
            "id": history_id,
            "player_id": rp_update.player_id,
            "old_rp": old_rp,
            "new_rp": new_rp,
            "change_reason": rp_update.reason,
            "updated_by": "admin_api",
            "created_at": now
        }).execute()
        
        return {
            "message": "RP updated successfully",
            "player_id": rp_update.player_id,
            "old_rp": old_rp,
            "new_rp": new_rp
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating player RP: {str(e)}"
        )

@router.post("/award-badge", response_model=PlayerBadgeResponse)
async def award_badge(
    badge_award: BadgeAwardRequest,
    _: None = Depends(require_admin_api_token)
):
    """
    Award badge to player (admin only)
    
    Note: player_badges table uses player_wallet and match_id (bigint), 
    not player_id and badge_id UUIDs as in legacy implementation.
    """
    try:
        # Validate match exists
        match_result = supabase.get_client().table("matches").select("id").eq("id", badge_award.match_id).execute()
        if not match_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found"
            )
        
        # Check if player already has this badge for this match
        existing_badge_result = supabase.get_client().table("player_badges") \
            .select("*") \
            .eq("player_wallet", badge_award.player_wallet) \
            .eq("badge_type", badge_award.badge_type) \
            .eq("match_id", badge_award.match_id) \
            .execute()
        
        if existing_badge_result.data and len(existing_badge_result.data) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Player already has this badge for this match"
            )
        
        # Award badge
        badge_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        player_badge_data = {
            "id": badge_id,
            "player_wallet": badge_award.player_wallet,
            "badge_type": badge_award.badge_type,
            "match_id": badge_award.match_id,
            "league_id": badge_award.league_id,
            "tournament_id": badge_award.tournament_id,
            "season_id": badge_award.season_id,
            "created_at": now
        }
        
        supabase.get_client().table("player_badges").insert(player_badge_data).execute()
        
        return PlayerBadgeResponse(
            id=badge_id,
            player_wallet=badge_award.player_wallet,
            badge_type=badge_award.badge_type,
            match_id=badge_award.match_id,
            league_id=badge_award.league_id,
            tournament_id=badge_award.tournament_id,
            season_id=badge_award.season_id,
            created_at=now
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error awarding badge: {str(e)}"
        )

@router.get("/players", response_model=List[PlayerProfile])
async def list_all_players(
    limit: int = 100,
    offset: int = 0,
    _: None = Depends(require_admin_api_token)
):
    """
    List all players (admin only)
    """
    try:
        # Get all players with pagination from Supabase
        players_result = supabase.get_client().table("players").select("*, users(*)").range(offset, offset + limit - 1).execute()
        
        if not players_result.data:
            return []
        
        # Convert to PlayerProfile
        return [
            PlayerProfile(
                id=player["id"],
                username=player["users"]["username"],
                discord_id=player["users"].get("discord_id"),
                rp=player.get("current_rp", 0),
                wins=player.get("wins", 0),
                losses=player.get("losses", 0),
                rank=calculate_rank(player.get("current_rp", 0))
            )
            for player in players_result.data
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing players: {str(e)}"
        )

# Note: Legacy badge management endpoints removed. 
# Use /v1/player-badges/ endpoints for player badge management.
# Achievements are managed via /v1/achievements/ endpoints.
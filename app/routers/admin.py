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
from app.schemas.badge import PlayerBadge as BadgeSchema

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
    player_id: str  # UUID as string
    badge_id: str  # UUID as string

class PlayerBadgeResponse(BaseModel):
    id: str  # UUID as string
    player_id: str  # UUID as string
    badge_id: str  # UUID as string
    badge_name: str
    badge_description: str
    awarded_at: str
    is_equipped: bool

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
    """
    try:
        # Check if player exists in Supabase
        player_result = supabase.get_client().table("players").select("*").eq("id", badge_award.player_id).single().execute()
        if not player_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found"
            )
        
        # Check if badge exists in Supabase
        badge_result = supabase.get_client().table("badges").select("*").eq("id", badge_award.badge_id).single().execute()
        if not badge_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Badge not found"
            )
        
        badge = badge_result.data
        
        # Check if player already has this badge
        existing_badge_result = supabase.get_client().table("player_badges") \
            .select("*") \
            .eq("player_id", badge_award.player_id) \
            .eq("badge_id", badge_award.badge_id) \
            .execute()
        
        if existing_badge_result.data and len(existing_badge_result.data) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Player already has this badge"
            )
        
        # Award badge
        badge_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        player_badge_data = {
            "id": badge_id,
            "player_id": badge_award.player_id,
            "badge_id": badge_award.badge_id,
            "is_equipped": False,
            "awarded_at": now
        }
        
        supabase.get_client().table("player_badges").insert(player_badge_data).execute()
        
        return PlayerBadgeResponse(
            id=badge_id,
            player_id=badge_award.player_id,
            badge_id=badge_award.badge_id,
            badge_name=badge["name"],
            badge_description=badge["description"],
            awarded_at=now,
            is_equipped=False
        )
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

@router.get("/badges", response_model=List[BadgeSchema])
async def list_all_badges(
    _: None = Depends(require_admin_api_token)
):
    """
    List all badges (admin only)
    """
    try:
        # Get all badges from Supabase
        badges_result = supabase.get_client().table("badges").select("*").eq("is_active", True).execute()
        
        if not badges_result.data:
            return []
        
        # Convert to BadgeSchema
        return [
            BadgeSchema(
                id=badge["id"],
                name=badge["name"],
                description=badge["description"] or "",
                icon_url=badge.get("icon_url", ""),
                rarity=badge.get("rarity", "common"),
                is_active=badge.get("is_active", True)
            )
            for badge in badges_result.data
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing badges: {str(e)}"
        )

@router.post("/badges", response_model=BadgeSchema)
async def create_badge(
    badge: BadgeSchema,
    _: None = Depends(require_admin_api_token)
):
    """
    Create a new badge (admin only)
    """
    try:
        # Generate UUID for new badge
        badge_id = str(uuid.uuid4())
        
        # Prepare badge data
        badge_data = {
            "id": badge_id,
            "name": badge.name,
            "description": badge.description or "",
            "icon_url": badge.icon_url or "",
            "rarity": badge.rarity or "common",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "created_by": "admin_api"
        }
        
        # Insert badge into Supabase
        supabase.get_client().table("badges").insert(badge_data).execute()
        
        # Return the created badge
        return BadgeSchema(
            id=badge_id,
            name=badge.name,
            description=badge.description or "",
            icon_url=badge.icon_url or "",
            rarity=badge.rarity or "common",
            is_active=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating badge: {str(e)}"
        )

@router.delete("/badges/{badge_id}")
async def delete_badge(
    badge_id: str,
    _: None = Depends(require_admin_api_token)
):
    """
    Delete a badge (admin only)
    """
    try:
        # Check if badge exists
        badge_result = supabase.get_client().table("badges").select("*").eq("id", badge_id).single().execute()
        
        if not badge_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Badge not found"
            )
        
        # Soft delete by setting is_active to False
        supabase.get_client().table("badges").update({
            "is_active": False,
            "updated_at": datetime.utcnow().isoformat(),
            "updated_by": "admin_api"
        }).eq("id", badge_id).execute()
        
        return {"message": "Badge deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting badge: {str(e)}"
        )
"""
Discord router for bot integration and Discord ID lookups using Supabase
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.core.config import settings
from app.core.supabase import supabase
from app.schemas.player import PlayerProfile
from app.schemas.user import UserCreate, UserInDB

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

router = APIRouter()

class DiscordPlayerCreate(BaseModel):
    discord_id: str
    gamertag: str
    region: str
    team_name: Optional[str] = None

class DiscordPlayerResponse(BaseModel):
    player_id: int
    gamertag: str
    current_rp: float
    tier: str
    team_name: Optional[str] = None
    region: Optional[str] = None
    discord_id: str

async def verify_discord_api_key(x_api_key: str = Header(None)):
    """Verify Discord API key for bot endpoints"""
    if not x_api_key or x_api_key != settings.DISCORD_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return x_api_key

@router.get("/players/{discord_id}", response_model=DiscordPlayerResponse)
async def get_player_by_discord_id(
    discord_id: str,
    api_key: str = Depends(verify_discord_api_key)
):
    """
    Get player profile by Discord ID (bot-safe endpoint)
    """
    try:
        # Find user by Discord ID
        user_result = supabase.get_client().table("users").select("*").eq("discord_id", discord_id).single().execute()
        
        if not user_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found with this Discord ID"
            )
        
        user = user_result.data
        
        # Get player profile
        player_result = supabase.get_client().table("players").select("*").eq("user_id", user["id"]).single().execute()
        
        if not player_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player profile not found"
            )
        
        player = player_result.data
        
        # Calculate tier based on RP
        tier = calculate_rank(player.get("current_rp", 0))
        
        return DiscordPlayerResponse(
            player_id=player["id"],
            gamertag=player["gamertag"],
            current_rp=player.get("current_rp", 0),
            tier=tier,
            team_name=player.get("team_name"),
            region=player.get("region"),
            discord_id=discord_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving player: {str(e)}"
        )

@router.post("/players/register", response_model=DiscordPlayerResponse)
async def register_player_via_discord(
    player_data: DiscordPlayerCreate,
    api_key: str = Depends(verify_discord_api_key)
):
    """
    Register a new player via Discord bot (light account creation)
    """
    try:
        # Check if Discord ID already exists
        existing_user_result = supabase.get_client().table("users").select("*").eq("discord_id", player_data.discord_id).execute()
        
        if existing_user_result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discord ID already registered"
            )
        
        # Check if gamertag is already taken
        existing_gamertag_result = supabase.get_client().table("players").select("*").eq("gamertag", player_data.gamertag).execute()
        
        if existing_gamertag_result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gamertag already taken"
            )
        
        # Create a new user with Discord ID
        user_id = str(uuid.uuid4())
        new_user_data = {
            "id": user_id,
            "discord_id": player_data.discord_id,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        user_result = supabase.get_client().table("users").insert(new_user_data).execute()
        
        if not user_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Create a player profile
        player_id = str(uuid.uuid4())
        new_player_data = {
            "id": player_id,
            "user_id": user_id,
            "gamertag": player_data.gamertag,
            "region": player_data.region,
            "team_name": player_data.team_name,
            "current_rp": 0,  # Start with 0 RP
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        player_result = supabase.get_client().table("players").insert(new_player_data).execute()
        
        if not player_result.data:
            # Rollback user creation if player creation fails
            supabase.get_client().table("users").delete().eq("id", user_id).execute()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create player profile"
            )
        
        return DiscordPlayerResponse(
            player_id=player_id,
            gamertag=player_data.gamertag,
            current_rp=0,
            tier="Iron",  # Starting tier
            team_name=player_data.team_name,
            region=player_data.region,
            discord_id=player_data.discord_id
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering player: {str(e)}"
        )

@router.get("/players/{discord_id}/rank")
async def get_player_rank(
    discord_id: str,
    api_key: str = Depends(verify_discord_api_key)
):
    """
    Get player's global rank by Discord ID
    """
    try:
        # Find user by Discord ID
        user_result = supabase.get_client().table("users").select("*").eq("discord_id", discord_id).single().execute()
        
        if not user_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found with this Discord ID"
            )
        
        user = user_result.data
        
        # Get player profile
        player_result = supabase.get_client().table("players").select("*").eq("user_id", user["id"]).single().execute()
        
        if not player_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player profile not found"
            )
        
        player = player_result.data
        current_rp = player.get("current_rp", 0)
        
        # Calculate global rank by counting players with higher RP
        rank_result = supabase.get_client().table("players").select("count").gt("current_rp", current_rp).execute()
        rank = (rank_result.count or 0) + 1
        
        # Calculate tier based on RP
        tier = calculate_rank(current_rp)
        
        return {
            "discord_id": discord_id,
            "gamertag": player["gamertag"],
            "current_rp": current_rp,
            "global_rank": rank,
            "tier": tier
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving player rank: {str(e)}"
        )

@router.get("/players/{discord_id}/tier-rank")
async def get_player_tier_rank(
    discord_id: str,
    api_key: str = Depends(verify_discord_api_key)
):
    """
    Get player's rank within their tier by Discord ID
    """
    try:
        # Find user by Discord ID
        user_result = supabase.get_client().table("users").select("*").eq("discord_id", discord_id).single().execute()
        
        if not user_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found with this Discord ID"
            )
        
        user = user_result.data
        
        # Get player profile
        player_result = supabase.get_client().table("players").select("*").eq("user_id", user["id"]).single().execute()
        
        if not player_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player profile not found"
            )
        
        player = player_result.data
        current_rp = player.get("current_rp", 0)
        
        # Calculate tier based on RP
        tier = calculate_rank(current_rp)
        
        # Get players in the same tier with higher RP
        # This is an approximation since we're calculating tier on the fly
        tier_min_rp = 0
        tier_max_rp = 0
        
        if tier == "Iron":
            tier_min_rp = 0
            tier_max_rp = 599
        elif tier == "Bronze":
            tier_min_rp = 600
            tier_max_rp = 799
        elif tier == "Silver":
            tier_min_rp = 800
            tier_max_rp = 999
        elif tier == "Gold":
            tier_min_rp = 1000
            tier_max_rp = 1199
        elif tier == "Platinum":
            tier_min_rp = 1200
            tier_max_rp = 1399
        elif tier == "Diamond":
            tier_min_rp = 1400
            tier_max_rp = 1599
        elif tier == "Master":
            tier_min_rp = 1600
            tier_max_rp = 1799
        elif tier == "Grandmaster":
            tier_min_rp = 1800
            tier_max_rp = 1999
        else:  # Challenger
            tier_min_rp = 2000
            tier_max_rp = 9999
        
        # Get players in same tier with higher RP
        tier_rank_result = supabase.get_client().table("players") \
            .select("count") \
            .gte("current_rp", tier_min_rp) \
            .lte("current_rp", tier_max_rp) \
            .gt("current_rp", current_rp) \
            .execute()
        
        tier_rank = (tier_rank_result.count or 0) + 1
        
        # Get total players in tier
        total_in_tier_result = supabase.get_client().table("players") \
            .select("count") \
            .gte("current_rp", tier_min_rp) \
            .lte("current_rp", tier_max_rp) \
            .execute()
        
        total_in_tier = total_in_tier_result.count or 0
        
        return {
            "discord_id": discord_id,
            "gamertag": player["gamertag"],
            "tier": tier,
            "tier_rank": tier_rank,
            "total_in_tier": total_in_tier,
            "current_rp": current_rp
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving player tier rank: {str(e)}"
        )

@router.get("/stats")
async def get_discord_stats(
    api_key: str = Depends(verify_discord_api_key)
):
    """
    Get Discord integration statistics
    """
    try:
        # Count users with discord_id not null
        users_result = supabase.get_client().table("users").select("count").not_("discord_id", "is", "null").execute()
        total_users = users_result.count or 0
        
        # Count players linked to users with discord_id not null
        # This requires a more complex query since we need to join tables
        # Using a raw SQL query with the Supabase client
        players_result = supabase.get_client().rpc(
            "count_discord_players",
            {}
        ).execute()
        
        # If the RPC function doesn't exist, we'll fall back to a simpler but less accurate count
        if not players_result.data or not isinstance(players_result.data, list) or len(players_result.data) == 0:
            # Fallback: Just count all players (this is not accurate but better than nothing)
            players_result = supabase.get_client().table("players").select("count").execute()
            total_players = players_result.count or 0
        else:
            total_players = players_result.data[0].get("count", 0)
        
        return {
            "total_discord_users": total_users,
            "total_discord_players": total_players
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving Discord stats: {str(e)}"
        )
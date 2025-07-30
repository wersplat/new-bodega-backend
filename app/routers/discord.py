"""
Discord router for bot integration and Discord ID lookups
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.player import Player
from app.schemas.player import PlayerProfile
from app.schemas.user import UserCreate

router = APIRouter()

class DiscordPlayerCreate(BaseModel):
    discord_id: str
    gamertag: str
    platform: str
    team_name: Optional[str] = None
    region: Optional[str] = None

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
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_discord_api_key)
):
    """
    Get player profile by Discord ID (bot-safe endpoint)
    """
    # Find user by Discord ID
    user = db.query(User).filter(User.discord_id == discord_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found with this Discord ID"
        )
    
    # Get player profile
    player = db.query(Player).filter(Player.user_id == user.id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player profile not found"
        )
    
    return DiscordPlayerResponse(
        player_id=player.id,
        gamertag=player.gamertag,
        current_rp=player.current_rp,
        tier=player.tier.value,
        team_name=player.team_name,
        region=player.region,
        discord_id=discord_id
    )

@router.post("/players/register", response_model=DiscordPlayerResponse)
async def register_player_via_discord(
    player_data: DiscordPlayerCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_discord_api_key)
):
    """
    Register a new player via Discord bot (light account creation)
    """
    # Check if Discord ID already exists
    existing_user = db.query(User).filter(User.discord_id == player_data.discord_id).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Discord ID already registered"
        )
    
    # Check if gamertag is already taken
    existing_gamertag = db.query(Player).filter(Player.gamertag == player_data.gamertag).first()
    if existing_gamertag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gamertag already taken"
        )
    
    # Create user account with Discord ID
    user = User(
        username=f"discord_{player_data.discord_id}",
        email=f"{player_data.discord_id}@discord.local",
        hashed_password="",  # No password for Discord users
        discord_id=player_data.discord_id,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create player profile
    player = Player(
        user_id=user.id,
        gamertag=player_data.gamertag,
        platform=player_data.platform,
        team_name=player_data.team_name,
        region=player_data.region
    )
    
    db.add(player)
    db.commit()
    db.refresh(player)
    
    return DiscordPlayerResponse(
        player_id=player.id,
        gamertag=player.gamertag,
        current_rp=player.current_rp,
        tier=player.tier.value,
        team_name=player.team_name,
        region=player.region,
        discord_id=player_data.discord_id
    )

@router.get("/players/{discord_id}/rank")
async def get_player_rank(
    discord_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_discord_api_key)
):
    """
    Get player's global rank by Discord ID
    """
    # Find user by Discord ID
    user = db.query(User).filter(User.discord_id == discord_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found with this Discord ID"
        )
    
    # Get player profile
    player = db.query(Player).filter(Player.user_id == user.id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player profile not found"
        )
    
    # Calculate global rank
    rank = db.query(Player).filter(Player.current_rp > player.current_rp).count() + 1
    
    return {
        "discord_id": discord_id,
        "gamertag": player.gamertag,
        "current_rp": player.current_rp,
        "global_rank": rank,
        "tier": player.tier.value
    }

@router.get("/players/{discord_id}/tier-rank")
async def get_player_tier_rank(
    discord_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_discord_api_key)
):
    """
    Get player's rank within their tier by Discord ID
    """
    # Find user by Discord ID
    user = db.query(User).filter(User.discord_id == discord_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found with this Discord ID"
        )
    
    # Get player profile
    player = db.query(Player).filter(Player.user_id == user.id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player profile not found"
        )
    
    # Calculate tier rank
    tier_rank = db.query(Player).filter(
        Player.tier == player.tier,
        Player.current_rp > player.current_rp
    ).count() + 1
    
    # Get total players in tier
    total_in_tier = db.query(Player).filter(Player.tier == player.tier).count()
    
    return {
        "discord_id": discord_id,
        "gamertag": player.gamertag,
        "tier": player.tier.value,
        "tier_rank": tier_rank,
        "total_in_tier": total_in_tier,
        "current_rp": player.current_rp
    }

@router.get("/stats")
async def get_discord_stats(
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_discord_api_key)
):
    """
    Get Discord integration statistics
    """
    total_users = db.query(User).filter(User.discord_id.isnot(None)).count()
    total_players = db.query(Player).join(User).filter(User.discord_id.isnot(None)).count()
    
    return {
        "total_discord_users": total_users,
        "total_discord_players": total_players
    } 
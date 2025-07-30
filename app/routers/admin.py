"""
Admin router for RP updates and badge assignment
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_admin_user
from app.models.user import User
from app.models.player import Player, RPHistory
from app.models.badge import Badge, PlayerBadge
from app.schemas.player import PlayerProfile
from app.schemas.badge import Badge as BadgeSchema, PlayerBadge as PlayerBadgeSchema

router = APIRouter()

class RPUpdateRequest(BaseModel):
    player_id: int
    new_rp: float
    reason: str

class BadgeAwardRequest(BaseModel):
    player_id: int
    badge_id: int

class PlayerBadgeResponse(BaseModel):
    id: int
    player_id: int
    badge_id: int
    badge_name: str
    badge_description: str
    awarded_at: str
    is_equipped: bool

@router.post("/update-rp")
async def update_player_rp(
    rp_update: RPUpdateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update player RP (admin only)
    """
    # Find player
    player = db.query(Player).filter(Player.id == rp_update.player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    # Store old RP
    old_rp = player.current_rp
    
    # Update RP
    player.current_rp = rp_update.new_rp
    
    # Update peak RP if necessary
    if rp_update.new_rp > player.peak_rp:
        player.peak_rp = rp_update.new_rp
    
    # Create RP history entry
    rp_history = RPHistory(
        player_id=player.id,
        old_rp=old_rp,
        new_rp=rp_update.new_rp,
        change_reason=rp_update.reason,
        updated_by=current_user.id
    )
    
    db.add(rp_history)
    db.commit()
    db.refresh(player)
    
    return {
        "message": "RP updated successfully",
        "player_id": player.id,
        "old_rp": old_rp,
        "new_rp": player.current_rp
    }

@router.post("/award-badge", response_model=PlayerBadgeResponse)
async def award_badge(
    badge_award: BadgeAwardRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Award badge to player (admin only)
    """
    # Check if player exists
    player = db.query(Player).filter(Player.id == badge_award.player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    # Check if badge exists
    badge = db.query(Badge).filter(Badge.id == badge_award.badge_id).first()
    if not badge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Badge not found"
        )
    
    # Check if player already has this badge
    existing_badge = db.query(PlayerBadge).filter(
        PlayerBadge.player_id == badge_award.player_id,
        PlayerBadge.badge_id == badge_award.badge_id
    ).first()
    
    if existing_badge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player already has this badge"
        )
    
    # Award badge
    player_badge = PlayerBadge(
        player_id=badge_award.player_id,
        badge_id=badge_award.badge_id,
        awarded_by=current_user.id
    )
    
    db.add(player_badge)
    db.commit()
    db.refresh(player_badge)
    
    return PlayerBadgeResponse(
        id=player_badge.id,
        player_id=player_badge.player_id,
        badge_id=player_badge.badge_id,
        badge_name=badge.name,
        badge_description=badge.description or "",
        awarded_at=player_badge.awarded_at.isoformat(),
        is_equipped=player_badge.is_equipped
    )

@router.get("/players", response_model=List[PlayerProfile])
async def list_all_players(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    List all players (admin only)
    """
    players = db.query(Player).offset(offset).limit(limit).all()
    return players

@router.get("/badges", response_model=List[BadgeSchema])
async def list_all_badges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    List all badges (admin only)
    """
    badges = db.query(Badge).filter(Badge.is_active == True).all()
    return badges

@router.post("/badges", response_model=BadgeSchema)
async def create_badge(
    badge: BadgeSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new badge (admin only)
    """
    db_badge = Badge(
        name=badge.name,
        description=badge.description,
        icon_url=badge.icon_url,
        rarity=badge.rarity
    )
    
    db.add(db_badge)
    db.commit()
    db.refresh(db_badge)
    
    return db_badge

@router.delete("/badges/{badge_id}")
async def delete_badge(
    badge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete a badge (admin only)
    """
    badge = db.query(Badge).filter(Badge.id == badge_id).first()
    if not badge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Badge not found"
        )
    
    # Soft delete by setting is_active to False
    badge.is_active = False
    db.commit()
    
    return {"message": "Badge deleted successfully"} 
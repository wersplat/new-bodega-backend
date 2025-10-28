"""
Achievements Router

This module provides API endpoints for managing achievements and achievement rules.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from pydantic import BaseModel, ConfigDict, Field

from app.core.supabase import supabase
from app.core.auth_supabase import require_admin_api_token, supabase_user_from_bearer
from app.core.rate_limiter import limiter
from app.core.config import settings

# Initialize router
router = APIRouter(
    prefix="/v1/achievements",
    tags=["Achievements"],
    responses={404: {"description": "Not found"}},
)

# Configure logging
logger = logging.getLogger(__name__)

# Pydantic Models

class AchievementBase(BaseModel):
    """Base achievement model"""
    name: str = Field(..., description="Unique achievement name")
    description: Optional[str] = Field(None, description="Achievement description")
    type: Optional[str] = Field(None, description="Achievement type")
    category: Optional[str] = Field(None, description="Achievement category")
    rarity: Optional[str] = Field(None, description="Achievement rarity (Common, Rare, Epic, Legendary)")
    achievement_badge: Optional[str] = Field(None, description="Badge URL")
    rp_value: Optional[int] = Field(None, ge=0, description="RP value awarded")
    is_player: Optional[bool] = Field(None, description="Is player achievement")
    is_team: Optional[bool] = Field(None, description="Is team achievement")

class AchievementCreate(AchievementBase):
    """Create achievement request"""
    pass

class AchievementUpdate(BaseModel):
    """Update achievement request"""
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    category: Optional[str] = None
    rarity: Optional[str] = None
    achievement_badge: Optional[str] = None
    rp_value: Optional[int] = Field(None, ge=0)
    is_player: Optional[bool] = None
    is_team: Optional[bool] = None

class Achievement(AchievementBase):
    """Achievement response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    created_at: str

class AchievementRuleBase(BaseModel):
    """Base achievement rule model"""
    name: str = Field(..., description="Achievement name this rule applies to")
    tier: str = Field(..., description="Achievement tier (bronze, silver, gold, platinum, etc)")
    scope: str = Field(..., description="Scope (per_game, season, career, streak, event)")
    predicate: Dict[str, Any] = Field(..., description="JSON predicate for rule evaluation")
    game_year: Optional[str] = None
    league_id: Optional[str] = None
    season_id: Optional[str] = None
    window_size: Optional[int] = Field(None, ge=1, description="Window size for rolling evaluations")
    window_predicate: Optional[Dict[str, Any]] = None
    award_template: Optional[Dict[str, Any]] = None
    requires_approval: bool = Field(False, description="Whether achievement requires manual approval")
    is_active: bool = Field(True, description="Whether rule is active")

class AchievementRuleCreate(AchievementRuleBase):
    """Create achievement rule request"""
    pass

class AchievementRuleUpdate(BaseModel):
    """Update achievement rule request"""
    tier: Optional[str] = None
    scope: Optional[str] = None
    predicate: Optional[Dict[str, Any]] = None
    game_year: Optional[str] = None
    league_id: Optional[str] = None
    season_id: Optional[str] = None
    window_size: Optional[int] = Field(None, ge=1)
    window_predicate: Optional[Dict[str, Any]] = None
    award_template: Optional[Dict[str, Any]] = None
    requires_approval: Optional[bool] = None
    is_active: Optional[bool] = None

class AchievementRule(AchievementRuleBase):
    """Achievement rule response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    created_at: str
    updated_at: str

class PlayerAchievement(BaseModel):
    """Player achievement response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    player_id: str
    rule_id: str
    title: str
    tier: str
    game_year: str
    league_id: str
    season_id: Optional[str] = None
    match_id: Optional[str] = None
    scope_key: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None
    level: int
    awarded_at: str
    issuer: str
    version: str
    signature: Optional[str] = None
    sig_alg: Optional[str] = None
    asset_svg_url: Optional[str] = None
    asset_png_url: Optional[str] = None
    token_uri: Optional[str] = None
    nft_mint_id: Optional[str] = None

# Achievements Endpoints

@router.get(
    "/",
    response_model=List[Achievement],
    summary="List all achievements"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_achievements(
    request: Request,
    category: Optional[str] = Query(None, description="Filter by category"),
    rarity: Optional[str] = Query(None, description="Filter by rarity"),
    type: Optional[str] = Query(None, description="Filter by type"),
    is_player: Optional[bool] = Query(None, description="Filter player achievements"),
    is_team: Optional[bool] = Query(None, description="Filter team achievements"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    List all achievements with optional filtering.
    
    Returns a list of available achievements that can be earned by players or teams.
    """
    try:
        query = supabase.get_client().table("achievements").select("*")
        
        if category:
            query = query.eq("category", category)
        if rarity:
            query = query.eq("rarity", rarity)
        if type:
            query = query.eq("type", type)
        if is_player is not None:
            query = query.eq("is_player", is_player)
        if is_team is not None:
            query = query.eq("is_team", is_team)
            
        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
        result = query.execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching achievements: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch achievements"
        )

@router.get(
    "/{achievement_id}",
    response_model=Achievement,
    summary="Get achievement by ID"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_achievement_by_id(
    request: Request,
    achievement_id: str
) -> Dict[str, Any]:
    """Get a specific achievement by ID."""
    try:
        result = supabase.get_by_id("achievements", achievement_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Achievement not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching achievement {achievement_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch achievement"
        )

@router.post(
    "/",
    response_model=Achievement,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_api_token)],
    summary="Create new achievement"
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def create_achievement(
    request: Request,
    achievement: AchievementCreate
) -> Dict[str, Any]:
    """Create a new achievement (admin only)."""
    try:
        achievement_data = achievement.model_dump()
        achievement_data["id"] = str(uuid4())
        achievement_data["created_at"] = datetime.utcnow().isoformat()
        
        result = supabase.insert("achievements", achievement_data)
        return result
    except Exception as e:
        logger.error(f"Error creating achievement: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create achievement"
        )

@router.put(
    "/{achievement_id}",
    response_model=Achievement,
    dependencies=[Depends(require_admin_api_token)],
    summary="Update achievement"
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def update_achievement(
    request: Request,
    achievement_id: str,
    achievement_update: AchievementUpdate
) -> Dict[str, Any]:
    """Update an achievement (admin only)."""
    try:
        update_data = {k: v for k, v in achievement_update.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
            
        result = supabase.update("achievements", achievement_id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Achievement not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating achievement {achievement_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update achievement"
        )

@router.delete(
    "/{achievement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin_api_token)],
    summary="Delete achievement"
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def delete_achievement(
    request: Request,
    achievement_id: str
):
    """Delete an achievement (admin only)."""
    try:
        result = supabase.delete("achievements", achievement_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Achievement not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting achievement {achievement_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete achievement"
        )

# Achievement Rules Endpoints

@router.get(
    "/rules/",
    response_model=List[AchievementRule],
    summary="List achievement rules"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_achievement_rules(
    request: Request,
    achievement_name: Optional[str] = Query(None, description="Filter by achievement name"),
    tier: Optional[str] = Query(None, description="Filter by tier"),
    scope: Optional[str] = Query(None, description="Filter by scope"),
    game_year: Optional[str] = Query(None, description="Filter by game year"),
    league_id: Optional[str] = Query(None, description="Filter by league ID"),
    season_id: Optional[str] = Query(None, description="Filter by season ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    List achievement rules with optional filtering.
    
    Achievement rules define the conditions under which achievements are awarded.
    """
    try:
        query = supabase.get_client().table("achievement_rules").select("*")
        
        if achievement_name:
            query = query.eq("name", achievement_name)
        if tier:
            query = query.eq("tier", tier)
        if scope:
            query = query.eq("scope", scope)
        if game_year:
            query = query.eq("game_year", game_year)
        if league_id:
            query = query.eq("league_id", league_id)
        if season_id:
            query = query.eq("season_id", season_id)
        if is_active is not None:
            query = query.eq("is_active", is_active)
            
        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
        result = query.execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching achievement rules: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch achievement rules"
        )

@router.get(
    "/rules/{rule_id}",
    response_model=AchievementRule,
    summary="Get achievement rule by ID"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_achievement_rule_by_id(
    request: Request,
    rule_id: str
) -> Dict[str, Any]:
    """Get a specific achievement rule by ID."""
    try:
        result = supabase.get_by_id("achievement_rules", rule_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Achievement rule not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching achievement rule {rule_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch achievement rule"
        )

@router.post(
    "/rules/",
    response_model=AchievementRule,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_api_token)],
    summary="Create achievement rule"
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def create_achievement_rule(
    request: Request,
    rule: AchievementRuleCreate
) -> Dict[str, Any]:
    """
    Create a new achievement rule (admin only).
    
    Achievement rules define the conditions and parameters for awarding achievements.
    """
    try:
        # Verify achievement exists
        achievement_result = supabase.get_client().table("achievements").select("id").eq("name", rule.name).execute()
        if not achievement_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Achievement '{rule.name}' not found. Create the achievement first."
            )
        
        rule_data = rule.model_dump()
        rule_data["id"] = str(uuid4())
        rule_data["created_at"] = datetime.utcnow().isoformat()
        rule_data["updated_at"] = datetime.utcnow().isoformat()
        
        result = supabase.insert("achievement_rules", rule_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating achievement rule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create achievement rule"
        )

@router.put(
    "/rules/{rule_id}",
    response_model=AchievementRule,
    dependencies=[Depends(require_admin_api_token)],
    summary="Update achievement rule"
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def update_achievement_rule(
    request: Request,
    rule_id: str,
    rule_update: AchievementRuleUpdate
) -> Dict[str, Any]:
    """Update an achievement rule (admin only)."""
    try:
        update_data = {k: v for k, v in rule_update.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
        
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        result = supabase.update("achievement_rules", rule_id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Achievement rule not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating achievement rule {rule_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update achievement rule"
        )

@router.delete(
    "/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin_api_token)],
    summary="Delete achievement rule"
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def delete_achievement_rule(
    request: Request,
    rule_id: str
):
    """Delete an achievement rule (admin only)."""
    try:
        result = supabase.delete("achievement_rules", rule_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Achievement rule not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting achievement rule {rule_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete achievement rule"
        )

# Player Achievements Endpoints

@router.get(
    "/player/{player_id}",
    response_model=List[PlayerAchievement],
    summary="Get player achievements"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_player_achievements(
    request: Request,
    player_id: str,
    game_year: Optional[str] = Query(None, description="Filter by game year"),
    league_id: Optional[str] = Query(None, description="Filter by league"),
    season_id: Optional[str] = Query(None, description="Filter by season"),
    tier: Optional[str] = Query(None, description="Filter by tier"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get all achievements earned by a specific player.
    """
    try:
        query = supabase.get_client().table("player_awards").select("*").eq("player_id", player_id)
        
        if game_year:
            query = query.eq("game_year", game_year)
        if league_id:
            query = query.eq("league_id", league_id)
        if season_id:
            query = query.eq("season_id", season_id)
        if tier:
            query = query.eq("tier", tier)
            
        query = query.order("awarded_at", desc=True).range(offset, offset + limit - 1)
        result = query.execute()
        
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching player achievements for {player_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch player achievements"
        )

@router.get(
    "/categories/",
    summary="Get achievement categories"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_achievement_categories(
    request: Request
) -> Dict[str, Any]:
    """
    Get all available achievement categories with counts.
    """
    try:
        result = supabase.get_client().table("achievements").select("category").execute()
        
        categories = {}
        for achievement in (result.data if hasattr(result, 'data') else []):
            category = achievement.get("category")
            if category:
                categories[category] = categories.get(category, 0) + 1
        
        return {
            "categories": [
                {"name": cat, "count": count}
                for cat, count in sorted(categories.items())
            ],
            "total": len(categories)
        }
    except Exception as e:
        logger.error(f"Error fetching achievement categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch achievement categories"
        )

@router.get(
    "/rarities/",
    summary="Get achievement rarities"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_achievement_rarities(
    request: Request
) -> Dict[str, Any]:
    """
    Get all available achievement rarities with counts.
    """
    try:
        result = supabase.get_client().table("achievements").select("rarity").execute()
        
        rarities = {}
        for achievement in (result.data if hasattr(result, 'data') else []):
            rarity = achievement.get("rarity")
            if rarity:
                rarities[rarity] = rarities.get(rarity, 0) + 1
        
        return {
            "rarities": [
                {"name": rarity, "count": count}
                for rarity, count in sorted(rarities.items())
            ],
            "total": len(rarities)
        }
    except Exception as e:
        logger.error(f"Error fetching achievement rarities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch achievement rarities"
        )

@router.get(
    "/eligibility/{player_id}",
    summary="Get player achievement eligibility"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_player_achievement_eligibility(
    request: Request,
    player_id: str
) -> Dict[str, Any]:
    """
    Get achievement eligibility data for a player from the eligibility mart.
    
    This endpoint provides insights into which achievements a player is close to earning.
    """
    try:
        result = supabase.get_client().table("achievement_eligibility_mart") \
            .select("*").eq("player_id", player_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player eligibility data not found"
            )
        
        return result.data[0] if result.data else {}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching achievement eligibility for {player_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch achievement eligibility"
        )


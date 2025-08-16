"""
Admin Match Router for Match Stat Entry functionality

This module provides endpoints for admin match stat entry, including autosave,
finalization, OCR prefill, and stat retrieval.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request, Body, Path
from pydantic import BaseModel, Field

from app.core.supabase import supabase
from app.core.auth_supabase import require_admin_api_token
from app.core.rate_limiter import limiter
from app.core.config import settings
from app.schemas.match import PlayerMatchStats
from app.schemas.player_stats import PlayerStatsCreate

# Initialize router
router = APIRouter(
    tags=["Admin Matches"],
    responses={404: {"description": "Not found"}},
)

# Configure logging
logger = logging.getLogger(__name__)

# Request/Response models
class AutosaveRequest(BaseModel):
    players: List[Dict[str, Any]] = Field(..., description="List of player stats")
    meta: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class AutosaveResponse(BaseModel):
    ok: bool = Field(..., description="Whether the operation was successful")
    updatedCount: int = Field(..., description="Number of records updated")
    warnings: List[Dict[str, Any]] = Field(default_factory=list, description="Validation warnings")

class FinalizeRequest(BaseModel):
    players: List[Dict[str, Any]] = Field(..., description="List of player stats")

class FinalizeResponse(BaseModel):
    ok: bool = Field(..., description="Whether the operation was successful")
    matchId: str = Field(..., description="Match ID")
    winner_team_id: Optional[str] = Field(None, description="Winner team ID")
    final_score: Dict[str, int] = Field(..., description="Final scores")

class OcrPrefillRequest(BaseModel):
    screenshot_url: str = Field(..., description="URL of the screenshot to process")

class OcrPrefillResponse(BaseModel):
    ok: bool = Field(..., description="Whether the operation was successful")
    players: List[Dict[str, Any]] = Field(..., description="List of player stats from OCR")
    confidence_scores: Dict[str, float] = Field(..., description="Confidence scores for each field")
    warnings: List[Dict[str, Any]] = Field(default_factory=list, description="OCR warnings")

class MatchStatsResponse(BaseModel):
    players: List[Dict[str, Any]] = Field(..., description="List of player stats for the match")

# Helper functions
def validate_player_stats(stats: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Validate player statistics and return warnings"""
    warnings = []
    
    # Field goal validation
    fgm = stats.get('fgm', 0)
    fga = stats.get('fga', 0)
    if fgm > fga:
        warnings.append({
            'type': 'error',
            'field': 'fgm',
            'message': 'Field goals made cannot exceed field goals attempted'
        })
    
    # Three point validation
    three_pm = stats.get('three_points_made', 0)
    three_pa = stats.get('three_points_attempted', 0)
    if three_pm > three_pa:
        warnings.append({
            'type': 'error',
            'field': 'three_points_made',
            'message': 'Three points made cannot exceed three points attempted'
        })
    
    # Free throw validation
    ftm = stats.get('ftm', 0)
    fta = stats.get('fta', 0)
    if ftm > fta:
        warnings.append({
            'type': 'error',
            'field': 'ftm',
            'message': 'Free throws made cannot exceed free throws attempted'
        })
    
    return warnings

def calculate_team_totals(players: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calculate team totals from player stats"""
    totals = {
        'points': 0,
        'rebounds': 0,
        'assists': 0,
        'steals': 0,
        'blocks': 0,
        'turnovers': 0,
        'fgm': 0,
        'fga': 0,
        'three_points_made': 0,
        'three_points_attempted': 0,
        'ftm': 0,
        'fta': 0,
        'fouls': 0,
        'minutes': 0,
    }
    
    for player in players:
        stats = player.get('stats', {})
        for key in totals:
            totals[key] += stats.get(key, 0)
    
    return totals

def get_match_context(match_id: str) -> Dict[str, Any]:
    """Get match context including teams and rosters"""
    try:
        # Get match details
        match = supabase.fetch_by_id("matches", match_id)
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Match with ID {match_id} not found"
            )
        
        # Get team details
        team_a_id = match.get('team_a_id')
        team_b_id = match.get('team_b_id')
        
        if not team_a_id or not team_b_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Match is missing team information"
            )
        
        team_a = supabase.fetch_by_id("teams", team_a_id)
        team_b = supabase.fetch_by_id("teams", team_b_id)
        
        # Get rosters
        roster_a = supabase.get_client().table("team_rosters").select(
            "player_id, team_id, is_captain, is_player_coach, players!inner(id, gamertag, position)"
        ).eq("team_id", team_a_id).is_("left_at", None).execute()
        
        roster_b = supabase.get_client().table("team_rosters").select(
            "player_id, team_id, is_captain, is_player_coach, players!inner(id, gamertag, position)"
        ).eq("team_id", team_b_id).is_("left_at", None).execute()
        
        return {
            'match': match,
            'team_a': team_a,
            'team_b': team_b,
            'roster_a': roster_a.data if roster_a.data else [],
            'roster_b': roster_b.data if roster_b.data else [],
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting match context: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get match context"
        )

# Endpoints
@router.post(
    "/matches/{match_id}/autosave",
    response_model=AutosaveResponse,
    status_code=status.HTTP_200_OK
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def autosave_match_stats(
    request: Request,
    match_id: str = Path(..., description="Match ID"),
    _: None = Depends(require_admin_api_token),
    data: AutosaveRequest = Body(...)
) -> AutosaveResponse:
    """
    Autosave draft match statistics.
    
    This endpoint saves player statistics in draft mode without finalizing the match.
    """
    try:
        logger.info(f"Autosaving stats for match: {match_id}")
        
        # Get match context
        context = get_match_context(match_id)
        
        # Validate player stats
        all_warnings = []
        for player in data.players:
            warnings = validate_player_stats(player.get('stats', {}))
            for warning in warnings:
                warning['player_id'] = player.get('player_id')
                all_warnings.append(warning)
        
        # Check for critical errors
        critical_errors = [w for w in all_warnings if w.get('type') == 'error']
        if critical_errors:
            return AutosaveResponse(
                ok=False,
                updatedCount=0,
                warnings=critical_errors
            )
        
        # Prepare stats data for upsert
        stats_data = []
        for player in data.players:
            stats = player.get('stats', {})
            stat_record = {
                'match_id': match_id,
                'player_id': player.get('player_id'),
                'team_id': player.get('team_id'),
                'player_name': player.get('player_name'),
                'points': stats.get('points'),
                'rebounds': stats.get('rebounds'),
                'assists': stats.get('assists'),
                'steals': stats.get('steals'),
                'blocks': stats.get('blocks'),
                'turnovers': stats.get('turnovers'),
                'fgm': stats.get('fgm'),
                'fga': stats.get('fga'),
                'three_points_made': stats.get('three_points_made'),
                'three_points_attempted': stats.get('three_points_attempted'),
                'ftm': stats.get('ftm'),
                'fta': stats.get('fta'),
                'fouls': stats.get('fouls'),
                'minutes': stats.get('minutes'),
                'updated_at': datetime.utcnow().isoformat(),
            }
            stats_data.append(stat_record)
        
        # Upsert player stats
        result = supabase.upsert(
            "player_stats", 
            stats_data, 
            on_conflict=["match_id", "player_id"]
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save player statistics"
            )
        
        # Update match submission status to draft
        try:
            supabase.get_client().table("match_submissions").update({
                'status': 'draft',
                'reviewed_at': datetime.utcnow().isoformat()
            }).eq('match_id', match_id).execute()
        except Exception as e:
            logger.warning(f"Failed to update match submission status: {e}")
        
        logger.info(f"Successfully autosaved {len(stats_data)} player stats for match: {match_id}")
        
        return AutosaveResponse(
            ok=True,
            updatedCount=len(stats_data),
            warnings=all_warnings
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error autosaving stats for match {match_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while autosaving match statistics"
        )

@router.post(
    "/matches/{match_id}/finalize",
    response_model=FinalizeResponse,
    status_code=status.HTTP_200_OK
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def finalize_match_stats(
    request: Request,
    match_id: str = Path(..., description="Match ID"),
    _: None = Depends(require_admin_api_token),
    data: FinalizeRequest = Body(...)
) -> FinalizeResponse:
    """
    Finalize and publish match statistics.
    
    This endpoint finalizes the match by calculating final scores, determining the winner,
    and publishing the statistics.
    """
    try:
        logger.info(f"Finalizing stats for match: {match_id}")
        
        # Get match context
        context = get_match_context(match_id)
        
        # Validate player stats
        all_warnings = []
        for player in data.players:
            warnings = validate_player_stats(player.get('stats', {}))
            for warning in warnings:
                warning['player_id'] = player.get('player_id')
                all_warnings.append(warning)
        
        # Check for critical errors - block finalization if any errors exist
        critical_errors = [w for w in all_warnings if w.get('type') == 'error']
        if critical_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot finalize - validation errors found"
            )
        
        # Calculate team totals
        team_totals = {}
        for player in data.players:
            team_id = player.get('team_id')
            if team_id not in team_totals:
                team_totals[team_id] = {
                    'points': 0,
                    'rebounds': 0,
                    'assists': 0,
                    'steals': 0,
                    'blocks': 0,
                    'turnovers': 0,
                    'fgm': 0,
                    'fga': 0,
                    'three_points_made': 0,
                    'three_points_attempted': 0,
                    'ftm': 0,
                    'fta': 0,
                    'fouls': 0,
                    'minutes': 0,
                }
            
            stats = player.get('stats', {})
            for key in team_totals[team_id]:
                team_totals[team_id][key] += stats.get(key, 0)
        
        # Determine winner
        team_ids = list(team_totals.keys())
        if len(team_ids) != 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid number of teams"
            )
        
        team_a_score = team_totals[team_ids[0]]['points']
        team_b_score = team_totals[team_ids[1]]['points']
        winner_id = team_ids[0] if team_a_score > team_b_score else team_ids[1] if team_b_score > team_a_score else None
        
        # Update match with final scores and winner
        match_update = {
            'score_a': team_a_score,
            'score_b': team_b_score,
            'winner_id': winner_id,
            'played_at': datetime.utcnow().isoformat(),
        }
        
        result = supabase.update("matches", match_id, match_update)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update match"
            )
        
        # Save final player stats
        stats_data = []
        for player in data.players:
            stats = player.get('stats', {})
            stat_record = {
                'match_id': match_id,
                'player_id': player.get('player_id'),
                'team_id': player.get('team_id'),
                'player_name': player.get('player_name'),
                'points': stats.get('points'),
                'rebounds': stats.get('rebounds'),
                'assists': stats.get('assists'),
                'steals': stats.get('steals'),
                'blocks': stats.get('blocks'),
                'turnovers': stats.get('turnovers'),
                'fgm': stats.get('fgm'),
                'fga': stats.get('fga'),
                'three_points_made': stats.get('three_points_made'),
                'three_points_attempted': stats.get('three_points_attempted'),
                'ftm': stats.get('ftm'),
                'fta': stats.get('fta'),
                'fouls': stats.get('fouls'),
                'minutes': stats.get('minutes'),
                'updated_at': datetime.utcnow().isoformat(),
            }
            stats_data.append(stat_record)
        
        result = supabase.upsert(
            "player_stats", 
            stats_data, 
            on_conflict=["match_id", "player_id"]
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save final player statistics"
            )
        
        # Update match submission status to approved
        try:
            supabase.get_client().table("match_submissions").update({
                'status': 'approved',
                'reviewed_at': datetime.utcnow().isoformat()
            }).eq('match_id', match_id).execute()
        except Exception as e:
            logger.warning(f"Failed to update match submission status: {e}")
        
        logger.info(f"Successfully finalized match: {match_id}")
        
        return FinalizeResponse(
            ok=True,
            matchId=match_id,
            winner_team_id=winner_id,
            final_score={
                'team_a': team_a_score,
                'team_b': team_b_score,
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finalizing stats for match {match_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while finalizing match statistics"
        )

@router.post(
    "/matches/{match_id}/ocr-prefill",
    response_model=OcrPrefillResponse,
    status_code=status.HTTP_200_OK
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def ocr_prefill_match_stats(
    request: Request,
    match_id: str = Path(..., description="Match ID"),
    _: None = Depends(require_admin_api_token),
    data: OcrPrefillRequest = Body(...)
) -> OcrPrefillResponse:
    """
    Prefill match statistics using OCR from a screenshot.
    
    This endpoint processes a screenshot using OCR to extract player statistics
    and maps them to the correct players using fuzzy matching.
    """
    try:
        logger.info(f"OCR prefill for match: {match_id}")
        
        # Get match context for roster information
        context = get_match_context(match_id)
        all_roster_players = context['roster_a'] + context['roster_b']
        
        # Simulate OCR processing (replace with actual OCR service)
        # For now, we'll return mock data
        ocr_result = {
            'success': True,
            'data': [
                {
                    'player_name': 'Player1',
                    'stats': {
                        'points': 15,
                        'rebounds': 8,
                        'assists': 4,
                        'steals': 2,
                        'blocks': 1,
                        'turnovers': 3,
                        'fgm': 6,
                        'fga': 12,
                        'three_points_made': 1,
                        'three_points_attempted': 3,
                        'ftm': 2,
                        'fta': 3,
                        'fouls': 2,
                        'minutes': 28,
                    }
                },
                {
                    'player_name': 'Player2',
                    'stats': {
                        'points': 22,
                        'rebounds': 5,
                        'assists': 7,
                        'steals': 1,
                        'blocks': 0,
                        'turnovers': 2,
                        'fgm': 8,
                        'fga': 15,
                        'three_points_made': 2,
                        'three_points_attempted': 5,
                        'ftm': 4,
                        'fta': 4,
                        'fouls': 1,
                        'minutes': 32,
                    }
                }
            ]
        }
        
        if not ocr_result['success']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OCR processing failed"
            )
        
        # Map OCR results to roster players using fuzzy matching
        mapped_players = []
        confidence_scores = {}
        warnings = []
        
        for ocr_player in ocr_result['data']:
            # Simple fuzzy matching (replace with more sophisticated algorithm)
            best_match = None
            best_score = float('inf')
            
            for roster_player in all_roster_players:
                roster_name = roster_player.get('players', {}).get('gamertag', '')
                ocr_name = ocr_player['player_name']
                
                # Simple Levenshtein-like distance
                distance = abs(len(roster_name) - len(ocr_name))
                if distance < best_score and distance <= 3:
                    best_score = distance
                    best_match = roster_player
            
            if best_match:
                player_data = {
                    'player_id': best_match['player_id'],
                    'team_id': best_match['team_id'],
                    'player_name': best_match['players']['gamertag'],
                    'stats': ocr_player['stats']
                }
                mapped_players.append(player_data)
                
                # Generate confidence scores
                for field, value in ocr_player['stats'].items():
                    if value is not None:
                        confidence = max(0.7, 1 - (value / 100))  # Higher confidence for lower values
                        confidence_scores[f"{best_match['player_id']}.{field}"] = confidence
                        
                        if confidence < 0.8:
                            warnings.append({
                                'type': 'warning',
                                'player_id': best_match['player_id'],
                                'field': field,
                                'message': f'Low confidence ({confidence:.1%}) for {field}'
                            })
            else:
                warnings.append({
                    'type': 'warning',
                    'message': f'Could not match OCR player "{ocr_player["player_name"]}" to roster'
                })
        
        logger.info(f"OCR prefill completed for match: {match_id}")
        
        return OcrPrefillResponse(
            ok=True,
            players=mapped_players,
            confidence_scores=confidence_scores,
            warnings=warnings
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in OCR prefill for match {match_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during OCR prefill"
        )

@router.get(
    "/matches/{match_id}/stats",
    response_model=MatchStatsResponse,
    status_code=status.HTTP_200_OK
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_match_stats(
    request: Request,
    match_id: str = Path(..., description="Match ID"),
    _: None = Depends(require_admin_api_token)
) -> MatchStatsResponse:
    """
    Get current match statistics.
    
    This endpoint retrieves all player statistics for a specific match.
    """
    try:
        logger.info(f"Getting stats for match: {match_id}")
        
        # Get match context
        context = get_match_context(match_id)
        
        # Get existing player stats
        existing_stats = supabase.get_client().table("player_stats").select("*").eq("match_id", match_id).execute()
        
        # Transform to match frontend format
        players = []
        all_roster_players = context['roster_a'] + context['roster_b']
        
        for roster_player in all_roster_players:
            player_id = roster_player['player_id']
            existing_stat = None
            
            if existing_stats.data:
                existing_stat = next(
                    (stat for stat in existing_stats.data if stat['player_id'] == player_id),
                    None
                )
            
            player_data = {
                'player_id': player_id,
                'team_id': roster_player['team_id'],
                'player_name': roster_player['players']['gamertag'],
                'stats': {
                    'points': existing_stat.get('points') if existing_stat else None,
                    'rebounds': existing_stat.get('rebounds') if existing_stat else None,
                    'assists': existing_stat.get('assists') if existing_stat else None,
                    'steals': existing_stat.get('steals') if existing_stat else None,
                    'blocks': existing_stat.get('blocks') if existing_stat else None,
                    'turnovers': existing_stat.get('turnovers') if existing_stat else None,
                    'fgm': existing_stat.get('fgm') if existing_stat else None,
                    'fga': existing_stat.get('fga') if existing_stat else None,
                    'three_points_made': existing_stat.get('three_points_made') if existing_stat else None,
                    'three_points_attempted': existing_stat.get('three_points_attempted') if existing_stat else None,
                    'ftm': existing_stat.get('ftm') if existing_stat else None,
                    'fta': existing_stat.get('fta') if existing_stat else None,
                    'fouls': existing_stat.get('fouls') if existing_stat else None,
                    'minutes': existing_stat.get('minutes') if existing_stat else None,
                }
            }
            players.append(player_data)
        
        logger.info(f"Retrieved {len(players)} player stats for match: {match_id}")
        
        return MatchStatsResponse(players=players)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stats for match {match_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving match statistics"
        )

"""
Admin actions router to support GraphQL admin mutations.
All endpoints require an admin API token.
"""

from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from fastapi import APIRouter, Depends, HTTPException, Path, Request
from pydantic import BaseModel, Field, ConfigDict

from app.core.supabase import supabase
from app.core.rate_limiter import limiter
from app.core.auth_supabase import require_admin_api_token


router = APIRouter(
    prefix="/v1",
    tags=["Admin"],
    responses={404: {"description": "Not found"}},
)


class CamelModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class RosterAddRequest(CamelModel):
    team_id: str = Field(..., alias="teamId")
    player_id: str = Field(..., alias="playerId")
    is_captain: Optional[bool] = Field(False, alias="isCaptain")
    is_player_coach: Optional[bool] = Field(False, alias="isPlayerCoach")


class RankingPointsRequest(CamelModel):
    team_id: str = Field(..., alias="teamId")
    event_id: Optional[str] = Field(None, alias="eventId")
    points: int
    source: Optional[str] = None


class PlayerRpTransactionRequest(CamelModel):
    player_id: str = Field(..., alias="playerId")
    delta: int
    reason: Optional[str] = None


class MatchPointsRequest(CamelModel):
    match_id: str = Field(..., alias="matchId")
    team_id: str = Field(..., alias="teamId")
    points: int
    source: Optional[str] = None


class MatchMvpRequest(CamelModel):
    match_id: str = Field(..., alias="matchId")
    player_id: str = Field(..., alias="playerId")


class ReviewMatchSubmissionRequest(CamelModel):
    decision: str  # approve | reject | flag
    notes: Optional[str] = None


@router.post("/rosters")
@limiter.limit("60/minute")
async def add_player_to_roster(
    request: Request,
    body: RosterAddRequest,
    _: None = Depends(require_admin_api_token),
):
    """Add a player to a team roster."""
    data = {
        "id": str(uuid.uuid4()),
        "team_id": body.team_id,
        "player_id": body.player_id,
        "is_captain": body.is_captain or False,
        "is_player_coach": body.is_player_coach or False,
        "created_at": datetime.utcnow().isoformat(),
        "created_by": "admin_api",
    }
    res = supabase.get_client().table("team_rosters").insert(data).execute()
    if not getattr(res, "data", None):
        raise HTTPException(status_code=500, detail="Failed to add roster entry")
    return res.data[0]


@router.delete("/rosters/{roster_id}")
@limiter.limit("60/minute")
async def remove_player_from_roster(
    request: Request,
    roster_id: str = Path(..., description="Roster entry ID"),
    _: None = Depends(require_admin_api_token),
):
    supabase.get_client().table("team_rosters").delete().eq("id", roster_id).execute()
    return {"success": True}


@router.post("/ranking-points")
@limiter.limit("60/minute")
async def award_ranking_points(
    request: Request,
    body: RankingPointsRequest,
    _: None = Depends(require_admin_api_token),
):
    data = {
        "id": str(uuid.uuid4()),
        "team_id": body.team_id,
        "event_id": body.event_id,
        "points": body.points,
        "source": body.source or "manual",
        "created_at": datetime.utcnow().isoformat(),
        "created_by": "admin_api",
    }
    res = supabase.get_client().table("ranking_points").insert(data).execute()
    if not getattr(res, "data", None):
        raise HTTPException(status_code=500, detail="Failed to award ranking points")
    return res.data[0]


@router.post("/player-rp-transactions")
@limiter.limit("60/minute")
async def create_player_rp_transaction(
    request: Request,
    body: PlayerRpTransactionRequest,
    _: None = Depends(require_admin_api_token),
):
    client = supabase.get_client()
    # Fetch current player RP
    player_res = (
        client.table("players").select("id,current_rp,peak_rp").eq("id", body.player_id).single().execute()
    )
    if not getattr(player_res, "data", None):
        raise HTTPException(status_code=404, detail="Player not found")

    player = player_res.data
    old_rp = player.get("current_rp", 0) or 0
    new_rp = old_rp + body.delta
    peak_rp = max(player.get("peak_rp", old_rp) or 0, new_rp)

    # Update player RP
    client.table("players").update({"current_rp": new_rp, "peak_rp": peak_rp}).eq("id", body.player_id).execute()

    # Insert rp_history
    history = {
        "id": str(uuid.uuid4()),
        "player_id": body.player_id,
        "old_rp": old_rp,
        "new_rp": new_rp,
        "change_reason": body.reason or "admin_adjustment",
        "updated_by": "admin_api",
        "created_at": datetime.utcnow().isoformat(),
    }
    hist_res = client.table("rp_history").insert(history).execute()
    if not getattr(hist_res, "data", None):
        raise HTTPException(status_code=500, detail="Failed to create RP transaction")
    return hist_res.data[0]


@router.post("/rp-transactions")
@limiter.limit("60/minute")
async def create_rp_transaction(
    request: Request,
    body: Dict[str, Any],
    _: None = Depends(require_admin_api_token),
):
    # Accepts generic payload; if playerId present, route to player path
    player_id = body.get("playerId") or body.get("player_id")
    delta = body.get("delta")
    reason = body.get("reason")
    if player_id and isinstance(delta, int):
        req = PlayerRpTransactionRequest(playerId=player_id, delta=delta, reason=reason)
        return await create_player_rp_transaction(request, req, None)  # type: ignore[arg-type]
    raise HTTPException(status_code=400, detail="Unsupported rp-transaction payload")


@router.post("/match-points")
@limiter.limit("60/minute")
async def award_match_points(
    request: Request,
    body: MatchPointsRequest,
    _: None = Depends(require_admin_api_token),
):
    # Minimal implementation: record as ranking_points with source tagged to match
    data = {
        "id": str(uuid.uuid4()),
        "team_id": body.team_id,
        "event_id": None,
        "points": body.points,
        "source": body.source or f"match:{body.match_id}",
        "created_at": datetime.utcnow().isoformat(),
        "created_by": "admin_api",
    }
    res = supabase.get_client().table("ranking_points").insert(data).execute()
    if not getattr(res, "data", None):
        raise HTTPException(status_code=500, detail="Failed to award match points")
    return res.data[0]


@router.post("/match-mvp")
@limiter.limit("60/minute")
async def set_match_mvp(
    request: Request,
    body: MatchMvpRequest,
    _: None = Depends(require_admin_api_token),
):
    client = supabase.get_client()
    data = {
        "match_id": body.match_id,
        "player_id": body.player_id,
        "updated_at": datetime.utcnow().isoformat(),
        "updated_by": "admin_api",
    }
    res = client.table("match_mvp").upsert(data, on_conflict=["match_id"]).execute()
    if not getattr(res, "data", None):
        raise HTTPException(status_code=500, detail="Failed to set match MVP")
    return res.data[0]


@router.post("/submissions/{submission_id}/review")
@limiter.limit("60/minute")
async def review_match_submission(
    request: Request,
    submission_id: str,
    body: ReviewMatchSubmissionRequest,
    _: None = Depends(require_admin_api_token),
):
    decision_map = {
        "approve": "approved",
        "reject": "rejected",
        "flag": "flagged",
    }
    status_value = decision_map.get(body.decision)
    if not status_value:
        raise HTTPException(status_code=400, detail="Invalid decision")

    client = supabase.get_client()
    update = {
        "status": status_value,
        "review_notes": body.notes or None,
        "reviewed_at": datetime.utcnow().isoformat(),
        "reviewed_by": "admin_api",
    }
    res = client.table("match_submissions").update(update).eq("id", submission_id).execute()
    if not getattr(res, "data", None):
        raise HTTPException(status_code=500, detail="Failed to review submission")
    return res.data[0]



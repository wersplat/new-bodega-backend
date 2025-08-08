"""
Admin actions router to support GraphQL admin mutations.
All endpoints require an admin API token.
"""

from datetime import datetime
import logging
from typing import Optional, Dict, Any
import uuid

from fastapi import APIRouter, Depends, HTTPException, Path, Request, Query
from pydantic import BaseModel, Field, ConfigDict

from app.core.supabase import supabase
from app.core.rate_limiter import limiter
from app.core.auth_supabase import require_admin_api_token


router = APIRouter(
    prefix="/v1",
    tags=["Admin"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)


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


def _map_submission_row_to_dto(row: Dict[str, Any]) -> Dict[str, Any]:
    """Shape raw match_submissions row to the admin UI's expected structure."""
    # Try to surface scores if present under common column names or payload
    def _extract_score_candidates(r: Dict[str, Any]) -> Dict[str, int]:
        score_a = (
            r.get("team_a_score")
            or r.get("home_score")
            or r.get("score_a")
            or 0
        )
        score_b = (
            r.get("team_b_score")
            or r.get("away_score")
            or r.get("score_b")
            or 0
        )
        # If payload/json exists, look inside
        payload = r.get("payload") or r.get("data") or {}
        if isinstance(payload, dict):
            score_a = payload.get("homeScore", score_a)
            score_b = payload.get("awayScore", score_b)
        try:
            score_a = int(score_a) if score_a is not None else 0
        except Exception:
            score_a = 0
        try:
            score_b = int(score_b) if score_b is not None else 0
        except Exception:
            score_b = 0
        return {"home": score_a, "away": score_b}

    scores = _extract_score_candidates(row)
    return {
        "id": row.get("id"),
        "status": (row.get("review_status") or "pending"),
        "submittedAt": row.get("created_at"),
        "submittedBy": {
            "id": row.get("reviewed_by") or "",
            "email": "",
        },
        "matchData": {
            "homeTeam": {
                "id": row.get("team_a_id") or "",
                "name": row.get("team_a_name") or "",
            },
            "awayTeam": {
                "id": row.get("team_b_id") or "",
                "name": row.get("team_b_name") or "",
            },
            # Scores if present; otherwise 0
            "homeScore": scores["home"],
            "awayScore": scores["away"],
            "date": row.get("created_at"),
            "players": [],
        },
        "notes": None,
        "flags": [],
    }


def _get_match_scores(client, match_id: Optional[str]) -> Dict[str, int]:
    """Fetch scores from matches table when available."""
    default = {"home": 0, "away": 0}
    if not match_id:
        return default
def _is_pending_status(value: Optional[str]) -> bool:
    if value is None:
        return True
    try:
        norm = str(value).strip().lower()
    except Exception:
        return False
    return norm == "" or norm == "pending"
    try:
        res = client.table("matches").select("score_a,score_b").eq("id", match_id).single().execute()
        data = getattr(res, "data", None) or {}
        home = data.get("score_a") or 0
        away = data.get("score_b") or 0
        try:
            home = int(home)
        except Exception:
            home = 0
        try:
            away = int(away)
        except Exception:
            away = 0
        return {"home": home, "away": away}
    except Exception as e:
        logger.error(f"_get_match_scores error for {match_id}: {e}")
        return default


@router.get("/match-submissions")
@limiter.limit("60/minute")
async def list_match_submissions(
    request: Request,
    status: Optional[str] = Query(default=None),
    _: None = Depends(require_admin_api_token),
):
    """List match submissions, optionally filtered by review status.

    Treat NULL review_status as "pending" for convenience.
    """
    try:
        client = supabase.get_client()
        res = client.table("match_submissions").select("*").order("created_at", desc=True).execute()
        rows = getattr(res, "data", []) or []

        if status:
            if str(status).strip().lower() == "pending":
                rows = [r for r in rows if _is_pending_status(r.get("review_status"))]
            else:
                rows = [r for r in rows if str(r.get("review_status")) == status]

        items = []
        for row in rows:
            try:
                dto = _map_submission_row_to_dto(row)
                # Enrich from matches when match_id present
                mid = row.get("match_id")
                if mid:
                    scores = _get_match_scores(client, mid)
                    dto["matchData"]["homeScore"] = scores["home"]
                    dto["matchData"]["awayScore"] = scores["away"]
                items.append(dto)
            except Exception as map_err:
                logger.error(f"map submission row error: {map_err}; row id={row.get('id')}")
                continue
        return {"items": items}
    except Exception as e:
        logger.error(f"list_match_submissions error: {e}")
        # Never 500 to the admin UI for list; return empty
        return {"items": []}


@router.get("/match-submissions/pending")
@limiter.limit("60/minute")
async def list_match_submissions_pending(
    request: Request,
    _: None = Depends(require_admin_api_token),
):
    """Deterministic endpoint for pending submissions (includes NULL)."""
    try:
        client = supabase.get_client()
        res = client.table("match_submissions").select("*").order("created_at", desc=True).execute()
        rows = getattr(res, "data", []) or []
        rows = [r for r in rows if _is_pending_status(r.get("review_status"))]
        items = []
        for row in rows:
            try:
                dto = _map_submission_row_to_dto(row)
                mid = row.get("match_id")
                if mid:
                    scores = _get_match_scores(client, mid)
                    dto["matchData"]["homeScore"] = scores["home"]
                    dto["matchData"]["awayScore"] = scores["away"]
                items.append(dto)
            except Exception as map_err:
                logger.error(f"map submission row error: {map_err}; row id={row.get('id')}")
                continue
        return {"items": items}
    except Exception as e:
        logger.error(f"list_match_submissions_pending error: {e}")
        return {"items": []}


@router.get("/match-submissions/{submission_id}")
@limiter.limit("60/minute")
async def get_match_submission(
    request: Request,
    submission_id: str,
    _: None = Depends(require_admin_api_token),
):
    """Fetch a single match submission by id."""
    client = supabase.get_client()
    res = (
        client.table("match_submissions").select("*").eq("id", submission_id).single().execute()
    )
    row = getattr(res, "data", None)
    if not row:
        raise HTTPException(status_code=404, detail="Submission not found")
    dto = _map_submission_row_to_dto(row)
    mid = row.get("match_id")
    if mid:
        scores = _get_match_scores(client, mid)
        dto["matchData"]["homeScore"] = scores["home"]
        dto["matchData"]["awayScore"] = scores["away"]
    return {"submission": dto}


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



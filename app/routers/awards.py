"""
Awards Endpoints (FastAPI)

Exposes awards list, summary, and years endpoints backed by Supabase view
`team_awards_all_mv`.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Query, HTTPException
from app.core.supabase import supabase

router = APIRouter(prefix="/v1/awards", tags=["Awards"])


def parse_entity(entity: Optional[str], team_id: Optional[str]) -> str:
    if entity and entity.startswith("team:"):
        return entity.split(":", 1)[1]
    if team_id:
        return team_id
    raise HTTPException(status_code=400, detail="Missing team entity. Use entity=team:<uuid> or teamId=<uuid>")


@router.get("/")
def list_awards(
    entity: Optional[str] = Query(None, description="team:<uuid> entity"),
    teamId: Optional[str] = Query(None, description="Team UUID (alternative to entity)"),
    tier: Optional[List[str]] = Query(None, description="Repeatable event tiers (T1,T2,T3,T4)"),
    _class: Optional[str] = Query(None, alias="class", description="award_class filter"),
    year: Optional[str] = Query(None, description="Year tag like 2K26"),
    search: Optional[str] = Query(None, description="Fuzzy search on event_name"),
    limit: int = Query(24, ge=1, le=100),
    cursor: Optional[str] = Query(None),
):
    team_id = parse_entity(entity, teamId)
    client = supabase.get_client()

    query = client.table("team_awards_all_mv").select("*").eq("team_id", team_id)
    if tier:
        # filter only valid tiers
        tiers = [t for t in tier if t in ("T1", "T2", "T3", "T4")]
        if tiers:
            query = query.in_("event_tier", tiers)
    if _class:
        query = query.eq("award_class", _class)
    if year:
        query = query.eq("year", year)
    if search:
        query = query.ilike("event_name", f"%{search}%")

    # Cursor keyset: (awarded_at DESC, source_row_id DESC)
    if cursor:
        try:
            import base64, json
            decoded = json.loads(base64.b64decode(cursor).decode("utf-8"))
            a = decoded.get("awardedAt")
            i = decoded.get("id")
            ors = []
            if a:
                ors.append(f"awarded_at.lt.{a}")
            if a and i:
                ors.append(f"and(awarded_at.eq.{a},source_row_id.lt.{i})")
            if not a and i:
                ors.append(f"source_row_id.lt.{i}")
            if ors:
                query = query.or_(",".join(ors))
        except Exception:
            pass

    query = query.order("awarded_at", desc=True).order("source_row_id", desc=True).limit(limit)
    resp = query.execute()
    data = getattr(resp, "data", []) or []

    def coalesce_date(row: Dict[str, Any]) -> Optional[str]:
        d = row.get("awarded_at") or row.get("end_date") or row.get("start_date")
        return d

    next_cursor = None
    if data:
        last = data[-1]
        try:
            import base64, json
            next_cursor = base64.b64encode(
                json.dumps({"awardedAt": coalesce_date(last), "id": last.get("source_row_id")}).encode("utf-8")
            ).decode("utf-8")
        except Exception:
            next_cursor = None

    return {"items": data, "nextCursor": next_cursor, "hasMore": len(data) == limit}


@router.get("/summary")
def awards_summary(
    entity: Optional[str] = Query(None),
    teamId: Optional[str] = Query(None),
):
    team_id = parse_entity(entity, teamId)
    client = supabase.get_client()
    # Use RPC to run SQL if needed, or compute client-side
    resp = client.table("team_awards_all_mv").select(
        "award_class,event_tier,awarded_at,start_date,end_date"
    ).eq("team_id", team_id).limit(10000).execute()
    rows = getattr(resp, "data", []) or []
    championships = sum(1 for r in rows if r.get("award_class") == "championship")
    tiers = len({r.get("event_tier") for r in rows if r.get("event_tier")})

    def to_date(r: Dict[str, Any]):
        return r.get("awarded_at") or r.get("end_date") or r.get("start_date")

    dates = [to_date(r) for r in rows if to_date(r)]
    first = min(dates) if dates else None
    latest = max(dates) if dates else None
    return {"championships": championships, "tiers": tiers, "first_title_at": first, "latest_title_at": latest}


@router.get("/years")
def awards_years(
    entity: Optional[str] = Query(None),
    teamId: Optional[str] = Query(None),
):
    team_id = parse_entity(entity, teamId)
    client = supabase.get_client()
    resp = client.table("team_awards_all_mv").select(
        "season_number,year,awarded_at,start_date,end_date"
    ).eq("team_id", team_id).limit(10000).execute()
    rows = getattr(resp, "data", []) or []

    from collections import defaultdict
    counts = defaultdict(int)
    def year_tag(r: Dict[str, Any]) -> Optional[str]:
        if r.get("year"):
            return r["year"]
        # derive 2KYY from date
        d = r.get("awarded_at") or r.get("end_date") or r.get("start_date")
        if not d:
            return None
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(str(d).replace('Z',''))
            yy = str(dt.year - 2000).zfill(2)
            return f"2K{yy}"
        except Exception:
            return None

    for r in rows:
        tag = year_tag(r)
        if not tag:
            continue
        key = (r.get("season_number"), tag)
        counts[key] += 1

    result = [
        {"season_number": k[0], "year_tag": k[1], "titles_in_season": v}
        for k, v in counts.items()
    ]
    result.sort(key=lambda x: ((x["season_number"] or 0), x["year_tag"]), reverse=True)
    return result



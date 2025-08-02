"""
Teams router for team management and lookups
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.core.supabase import supabase
from app.core.auth import get_current_active_user
from app.schemas.team import TeamCreate, Team as TeamSchema, TeamUpdate, TeamWithPlayers

router = APIRouter(prefix="", tags=["teams"])

async def get_team_by_id(team_id: str) -> Optional[Dict[str, Any]]:
    """Helper function to get a team by ID from Supabase"""
    result = supabase.fetch_by_id("teams", team_id)
    return result

@router.post("/", response_model=TeamSchema, status_code=status.HTTP_201_CREATED)
async def create_team(
    team: TeamCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Create a new team
    """
    # Check if team name is already taken
    client = supabase.get_client()
    existing_team = client.table("teams").select("*").eq("name", team.name).execute()
    
    if hasattr(existing_team, 'data') and existing_team.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team name already taken"
        )
    
    # Create team
    team_data = team.model_dump()
    team_data["created_by"] = str(current_user.id) if hasattr(current_user, 'id') else None
    
    try:
        created_team = supabase.insert("teams", team_data)
        return created_team
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create team: {str(e)}"
        )

@router.get("/{team_id}", response_model=TeamWithPlayers)
async def get_team(team_id: str):
    """
    Get team details by ID
    """
    team = await get_team_by_id(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Get team players
    client = supabase.get_client()
    players = client.table("players").select("*").eq("current_team_id", team_id).execute()
    
    team_with_players = dict(team)
    team_with_players["players"] = players.data if hasattr(players, 'data') else []
    
    return team_with_players

@router.get("/", response_model=List[TeamSchema])
async def list_teams(
    skip: int = 0,
    limit: int = 100,
    region_id: Optional[str] = None,
    name: Optional[str] = None
):
    """
    List all teams with optional filtering
    """
    try:
        print("Getting Supabase client...")
        client = supabase.get_client()
        print("Supabase client obtained successfully")
        
        print("Executing query...")
        query = client.table("teams").select("*")
        print("Base query created")
        
        if region_id:
            print(f"Filtering by region_id: {region_id}")
            query = query.eq("region_id", region_id)
        if name:
            print(f"Filtering by name: {name}")
            query = query.ilike("name", f"%{name}%")
        
        print("Executing query with range...")
        result = query.range(skip, skip + limit - 1).execute()
        print("Query executed")
        
        print("Result object:", result)
        print("Result type:", type(result))
        print("Result dir:", dir(result))
        
        if not hasattr(result, 'data'):
            error_msg = f"No 'data' attribute in result. Result: {result}"
            print(error_msg)
            return []
        
        print(f"Result data type: {type(result.data)}")
        print(f"Result data: {result.data}")
            
        print(f"Successfully retrieved {len(result.data)} teams")
        return result.data
        
    except Exception as e:
        error_msg = f"Error in list_teams: {str(e)}\nType: {type(e).__name__}"
        print(error_msg)
        import traceback
        traceback_str = traceback.format_exc()
        print(traceback_str)
        
        # Return a 500 error with detailed information
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to list teams",
                "message": str(e),
                "type": type(e).__name__
            }
        )

@router.put("/{team_id}", response_model=TeamSchema)
async def update_team(
    team_id: str,
    team_update: TeamUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Update team information
    """
    # Check if team exists
    team = await get_team_by_id(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if user has permission to update the team
    # Note: Add your permission logic here
    
    try:
        updated_team = supabase.update("teams", team_id, team_update.model_dump(exclude_unset=True))
        return updated_team
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update team: {str(e)}"
        )

@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Delete a team
    """
    # Check if team exists
    team = await get_team_by_id(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if user has permission to delete the team
    # Note: Add your permission logic here
    
    try:
        # First, remove all players from the team
        client = supabase.get_client()
        client.table("players").update({"current_team_id": None}).eq("current_team_id", team_id).execute()
        
        # Then delete the team
        supabase.delete("teams", team_id)
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete team: {str(e)}"
        )

@router.get("/search/{name}", response_model=List[TeamSchema])
async def search_teams_by_name(name: str):
    """
    Search teams by name
    """
    client = supabase.get_client()
    result = client.table("teams").select("*").ilike("name", f"%{name}%").execute()
    return result.data if hasattr(result, 'data') else []

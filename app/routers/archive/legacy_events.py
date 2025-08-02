"""
LEGACY ROUTER - DO NOT USE DIRECTLY

This is a legacy router that has been replaced by events_supabase.py.
It is kept for reference purposes only and its endpoints are disabled.
"""

import os
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.auth import get_current_active_user, get_current_user
from app.models.user import User
from app.models.event import Event
from app.schemas.event import EventCreate, Event as EventSchema, EventUpdate

# Create router with disabled tag to clearly identify it in API docs
router = APIRouter(tags=["LEGACY - DISABLED"])

# Only register endpoints if explicitly enabled (which should not be done in production)
if os.environ.get("ENABLE_LEGACY_ENDPOINTS", "").lower() == "true":
    # Original event router endpoints would be here
    pass
else:
    # Add a warning endpoint to indicate this router is disabled
    @router.get("/", include_in_schema=False)
    def legacy_disabled():
        """This endpoint is disabled as it has been replaced by the Supabase version."""
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This legacy endpoint has been disabled. Please use the new API endpoints."
        )

"""
Notifications Router

This module provides API endpoints for managing user notifications.
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
    prefix="/v1/notifications",
    tags=["Notifications"],
    responses={404: {"description": "Not found"}},
)

# Configure logging
logger = logging.getLogger(__name__)

# Pydantic Models

class NotificationBase(BaseModel):
    """Base notification model"""
    title: str = Field(..., description="Notification title", max_length=200)
    message: Optional[str] = Field(None, description="Notification message")
    type: str = Field("info", description="Notification type (info, warning, error, success)")

class NotificationCreate(NotificationBase):
    """Create notification request"""
    user_id: Optional[str] = Field(None, description="Target user ID (if None, broadcasts to all)")

class NotificationUpdate(BaseModel):
    """Update notification request"""
    title: Optional[str] = Field(None, max_length=200)
    message: Optional[str] = None
    type: Optional[str] = None
    read: Optional[bool] = None

class Notification(NotificationBase):
    """Notification response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: Optional[str] = None
    read: bool
    created_at: str
    updated_at: str

class NotificationListResponse(BaseModel):
    """Paginated notification list response"""
    items: List[Notification]
    total: int
    unread_count: int
    page: int
    size: int
    has_more: bool

# Notification Endpoints

@router.get(
    "/",
    response_model=NotificationListResponse,
    summary="List user notifications"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_my_notifications(
    request: Request,
    current_user: Dict[str, Any] = Depends(supabase_user_from_bearer),
    read: Optional[bool] = Query(None, description="Filter by read status"),
    type: Optional[str] = Query(None, description="Filter by notification type"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page")
) -> Dict[str, Any]:
    """
    List notifications for the current user.
    
    Returns paginated notifications with unread count.
    """
    try:
        user_id = current_user.get("sub") or current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user id"
            )
        
        # Build query
        query = supabase.get_client().table("notifications").select("*", count="exact")
        
        # Filter by user_id or broadcast notifications (user_id is null)
        query = query.or_(f"user_id.eq.{user_id},user_id.is.null")
        
        if read is not None:
            query = query.eq("read", read)
        if type:
            query = query.eq("type", type)
        
        # Get total count
        count_result = query.execute()
        total = count_result.count if hasattr(count_result, 'count') else 0
        
        # Get unread count
        unread_query = supabase.get_client().table("notifications").select("id", count="exact") \
            .or_(f"user_id.eq.{user_id},user_id.is.null") \
            .eq("read", False)
        unread_result = unread_query.execute()
        unread_count = unread_result.count if hasattr(unread_result, 'count') else 0
        
        # Apply pagination
        offset = (page - 1) * size
        query = query.order("created_at", desc=True).range(offset, offset + size - 1)
        
        result = query.execute()
        items = result.data if hasattr(result, 'data') else []
        
        return {
            "items": items,
            "total": total,
            "unread_count": unread_count,
            "page": page,
            "size": size,
            "has_more": (offset + len(items)) < total
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notifications"
        )

@router.get(
    "/{notification_id}",
    response_model=Notification,
    summary="Get notification by ID"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_notification_by_id(
    request: Request,
    notification_id: str,
    current_user: Dict[str, Any] = Depends(supabase_user_from_bearer)
) -> Dict[str, Any]:
    """Get a specific notification by ID."""
    try:
        user_id = current_user.get("sub") or current_user.get("user_id") or current_user.get("id")
        
        result = supabase.get_by_id("notifications", notification_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Verify user has access to this notification
        if result.get("user_id") and result["user_id"] != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this notification"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching notification {notification_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notification"
        )

@router.post(
    "/",
    response_model=Notification,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_api_token)],
    summary="Create notification"
)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def create_notification(
    request: Request,
    notification: NotificationCreate
) -> Dict[str, Any]:
    """
    Create a new notification (admin only).
    
    If user_id is None, the notification is broadcast to all users.
    """
    try:
        notification_data = notification.model_dump()
        notification_data["id"] = str(uuid4())
        notification_data["read"] = False
        notification_data["created_at"] = datetime.utcnow().isoformat()
        notification_data["updated_at"] = datetime.utcnow().isoformat()
        
        result = supabase.insert("notifications", notification_data)
        return result
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create notification"
        )

@router.put(
    "/{notification_id}/read",
    response_model=Notification,
    summary="Mark notification as read"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def mark_notification_read(
    request: Request,
    notification_id: str,
    current_user: Dict[str, Any] = Depends(supabase_user_from_bearer)
) -> Dict[str, Any]:
    """Mark a notification as read."""
    try:
        user_id = current_user.get("sub") or current_user.get("user_id") or current_user.get("id")
        
        # Get notification to verify ownership
        notification = supabase.get_by_id("notifications", notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Verify user has access
        if notification.get("user_id") and notification["user_id"] != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this notification"
            )
        
        update_data = {
            "read": True,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.update("notifications", notification_id, update_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification {notification_id} as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification"
        )

@router.put(
    "/mark-all-read",
    summary="Mark all notifications as read"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def mark_all_notifications_read(
    request: Request,
    current_user: Dict[str, Any] = Depends(supabase_user_from_bearer)
) -> Dict[str, Any]:
    """Mark all user notifications as read."""
    try:
        user_id = current_user.get("sub") or current_user.get("user_id") or current_user.get("id")
        
        update_data = {
            "read": True,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.get_client().table("notifications") \
            .update(update_data) \
            .eq("user_id", str(user_id)) \
            .eq("read", False) \
            .execute()
        
        count = len(result.data) if hasattr(result, 'data') and result.data else 0
        
        return {
            "message": f"Marked {count} notifications as read",
            "count": count
        }
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notifications"
        )

@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete notification"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def delete_notification(
    request: Request,
    notification_id: str,
    current_user: Dict[str, Any] = Depends(supabase_user_from_bearer)
):
    """Delete a notification."""
    try:
        user_id = current_user.get("sub") or current_user.get("user_id") or current_user.get("id")
        
        # Get notification to verify ownership
        notification = supabase.get_by_id("notifications", notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Verify user has access
        if notification.get("user_id") and notification["user_id"] != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this notification"
            )
        
        supabase.delete("notifications", notification_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification {notification_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete notification"
        )

@router.get(
    "/unread/count",
    summary="Get unread notification count"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_unread_count(
    request: Request,
    current_user: Dict[str, Any] = Depends(supabase_user_from_bearer)
) -> Dict[str, int]:
    """
    Get the count of unread notifications for the current user.
    """
    try:
        user_id = current_user.get("sub") or current_user.get("user_id") or current_user.get("id")
        
        query = supabase.get_client().table("notifications") \
            .select("id", count="exact") \
            .or_(f"user_id.eq.{user_id},user_id.is.null") \
            .eq("read", False)
        
        result = query.execute()
        count = result.count if hasattr(result, 'count') else 0
        
        return {"unread_count": count}
    except Exception as e:
        logger.error(f"Error fetching unread notification count: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch unread count"
        )


"""
Payments router for Stripe integration
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
import logging

from app.core.auth import get_current_active_user, get_current_admin_user
from app.core.supabase import supabase
from app.services.payments import PaymentService
from app.schemas.payments import CreatePaymentSessionRequest

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router with explicit prefix and standardized tags
router = APIRouter(
    prefix="/v1/payments",
    tags=["Payment Integration"],
    responses={404: {"description": "Not found"}},
)

@router.post("/session/create")
async def create_payment_session(
    request: CreatePaymentSessionRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Create payment session for event registration
    """
    try:
        # Get player profile
        player_result = supabase.get_client().table("players").select("*").eq("user_id", current_user["id"]).single().execute()
        
        if not player_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player profile not found"
            )
        
        player = player_result.data
        
        # Create payment session using service
        return await PaymentService.create_checkout_session(
            event_id=request.event_id,
            player_id=player["id"]
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating payment session: {str(e)}"
        )

@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None)
):
    """
    Handle Stripe webhook events
    """
    try:
        if not stripe_signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Stripe signature"
            )
        
        payload = await request.body()
        return await PaymentService.handle_webhook(payload, stripe_signature)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )

@router.post("/refund/{registration_id}")
async def refund_payment(
    registration_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Process refund for event registration (admin only)
    """
    try:
        return await PaymentService.process_refund(registration_id)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing refund: {str(e)}"
        )

@router.get("/session/{session_id}/status")
async def get_payment_status(
    session_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get payment session status
    """
    import stripe
    from app.core.config import settings
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        # Get Stripe session
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Check if user owns this session
        player_result = supabase.get_client().table("players").select("*").eq("user_id", current_user["id"]).single().execute()
        
        if not player_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player profile not found"
            )
        
        player = player_result.data
        
        # Find registration in Supabase
        registration_result = supabase.get_client().table("event_registrations").select("*").eq("stripe_session_id", session_id).eq("player_id", player["id"]).single().execute()
        
        if not registration_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registration not found"
            )
        
        registration = registration_result.data
        
        return {
            'session_id': session_id,
            'status': session.status,
            'payment_status': session.payment_status,
            'registration_status': registration["payment_status"]
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        elif isinstance(e, stripe.error.StripeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving payment status: {str(e)}"
            )
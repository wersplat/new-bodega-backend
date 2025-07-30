"""
Payments router for Stripe integration
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.player import Player
from app.models.event import EventRegistration
from app.services.payments import PaymentService

router = APIRouter()

@router.post("/create-session")
async def create_payment_session(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create Stripe checkout session for event registration
    """
    # Get player profile
    player = db.query(Player).filter(Player.user_id == current_user.id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player profile required for event registration"
        )
    
    return await PaymentService.create_checkout_session(event_id, player.id, db)

@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None)
):
    """
    Handle Stripe webhook events
    """
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature"
        )
    
    payload = await request.body()
    return await PaymentService.handle_webhook(payload, stripe_signature)

@router.get("/session/{session_id}/status")
async def get_payment_status(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get payment session status
    """
    import stripe
    from app.core.config import settings
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Check if user owns this session
        player = db.query(Player).filter(Player.user_id == current_user.id).first()
        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player profile not found"
            )
        
        registration = db.query(EventRegistration).filter(
            EventRegistration.stripe_session_id == session_id,
            EventRegistration.player_id == player.id
        ).first()
        
        if not registration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registration not found"
            )
        
        return {
            'session_id': session_id,
            'status': session.status,
            'payment_status': session.payment_status,
            'registration_status': registration.payment_status
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        ) 
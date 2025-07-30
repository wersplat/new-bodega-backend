"""
Payment service for Stripe integration
"""

import stripe
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.config import settings
from app.models.event import Event, EventRegistration
from app.models.player import Player

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentService:
    @staticmethod
    async def create_checkout_session(
        event_id: int,
        player_id: int,
        db: Session
    ) -> dict:
        """
        Create Stripe checkout session for event registration
        """
        # Get event details
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        # Get player details
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found"
            )
        
        # Check if already registered
        existing_registration = db.query(EventRegistration).filter(
            EventRegistration.event_id == event_id,
            EventRegistration.player_id == player_id
        ).first()
        
        if existing_registration:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already registered for this event"
            )
        
        try:
            # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"Event Registration: {event.name}",
                            'description': f"Registration for {player.gamertag} in {event.name}",
                        },
                        'unit_amount': int(event.entry_fee * 100),  # Convert to cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{settings.CORS_ORIGINS_LIST[0]}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.CORS_ORIGINS_LIST[0]}/payment/cancel",
                metadata={
                    'event_id': str(event_id),
                    'player_id': str(player_id),
                    'gamertag': player.gamertag,
                    'event_name': event.name
                }
            )
            
            # Create pending registration
            registration = EventRegistration(
                event_id=event_id,
                player_id=player_id,
                payment_status='pending',
                stripe_session_id=checkout_session.id
            )
            
            db.add(registration)
            db.commit()
            
            return {
                'session_id': checkout_session.id,
                'checkout_url': checkout_session.url,
                'amount': event.entry_fee
            }
            
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment error: {str(e)}"
            )
    
    @staticmethod
    async def handle_webhook(
        payload: bytes,
        sig_header: str
    ) -> dict:
        """
        Handle Stripe webhook events
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payload"
            )
        except stripe.error.SignatureVerificationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signature"
            )
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            await PaymentService._handle_payment_success(session)
        elif event['type'] == 'checkout.session.expired':
            session = event['data']['object']
            await PaymentService._handle_payment_expired(session)
        
        return {'status': 'success'}
    
    @staticmethod
    async def _handle_payment_success(session: dict):
        """
        Handle successful payment
        """
        from app.core.database import SessionLocal
        
        db = SessionLocal()
        try:
            # Get registration by session ID
            registration = db.query(EventRegistration).filter(
                EventRegistration.stripe_session_id == session['id']
            ).first()
            
            if registration:
                # Update payment status
                registration.payment_status = 'paid'
                registration.is_confirmed = True
                
                # Update event participant count
                event = db.query(Event).filter(Event.id == registration.event_id).first()
                if event:
                    event.current_participants += 1
                
                db.commit()
                
        finally:
            db.close()
    
    @staticmethod
    async def _handle_payment_expired(session: dict):
        """
        Handle expired payment
        """
        from app.core.database import SessionLocal
        
        db = SessionLocal()
        try:
            # Get registration by session ID
            registration = db.query(EventRegistration).filter(
                EventRegistration.stripe_session_id == session['id']
            ).first()
            
            if registration:
                # Remove expired registration
                db.delete(registration)
                db.commit()
                
        finally:
            db.close()
    
    @staticmethod
    async def refund_payment(
        registration_id: int,
        db: Session
    ) -> dict:
        """
        Refund a payment (admin only)
        """
        registration = db.query(EventRegistration).filter(
            EventRegistration.id == registration_id
        ).first()
        
        if not registration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registration not found"
            )
        
        if registration.payment_status != 'paid':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration not paid"
            )
        
        try:
            # Create refund in Stripe
            refund = stripe.Refund.create(
                payment_intent=registration.stripe_session_id
            )
            
            # Update registration status
            registration.payment_status = 'refunded'
            db.commit()
            
            return {
                'refund_id': refund.id,
                'status': 'refunded'
            }
            
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Refund error: {str(e)}"
            ) 
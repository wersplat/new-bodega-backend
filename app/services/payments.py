"""
Payment service for Stripe integration
"""

import stripe
from fastapi import HTTPException, status
from typing import Optional
import uuid
from datetime import datetime

from app.core.config import settings
from app.core.supabase import supabase

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentService:
    @staticmethod
    async def create_checkout_session(
        event_id: str,
        player_id: str
    ) -> dict:
        """
        Create Stripe checkout session for event registration
        """
        # Get event details
        event_result = supabase.get_client().table("events").select("*").eq("id", event_id).single().execute()
        if not event_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        event = event_result.data
        
        # Get player details
        player_result = supabase.get_client().table("players").select("*").eq("id", player_id).single().execute()
        if not player_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found"
            )
        
        player = player_result.data
        
        # Check if already registered
        existing_registration_result = supabase.get_client().table("event_registrations").select("*").eq("event_id", event_id).eq("player_id", player_id).execute()
        
        if existing_registration_result.data and len(existing_registration_result.data) > 0:
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
                            'name': f"Event Registration: {event['name']}",
                            'description': f"Registration for {player['gamertag']} in {event['name']}",
                        },
                        'unit_amount': int(float(event['entry_fee']) * 100),  # Convert to cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{settings.CORS_ORIGINS_LIST[0]}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.CORS_ORIGINS_LIST[0]}/payment/cancel",
                metadata={
                    'event_id': str(event_id),
                    'player_id': str(player_id),
                    'gamertag': player['gamertag'],
                    'event_name': event['name']
                }
            )
            
            # Create pending registration in Supabase
            registration_data = {
                "id": str(uuid.uuid4()),
                "event_id": event_id,
                "player_id": player_id,
                "payment_status": "pending",
                "stripe_session_id": checkout_session.id,
                "is_confirmed": False,
                "created_at": datetime.now().isoformat()
            }
            
            registration_result = supabase.get_client().table("event_registrations").insert(registration_data).execute()
            
            if not registration_result.data:
                # If registration creation fails, we should handle this case
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create registration record"
                )
            
            return {
                'session_id': checkout_session.id,
                'checkout_url': checkout_session.url,
                'amount': event['entry_fee']
            }
            
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment error: {str(e)}"
            )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating checkout session: {str(e)}"
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
        
        try:
            # Handle the event
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                await PaymentService._handle_payment_success(session)
            elif event['type'] == 'checkout.session.expired':
                session = event['data']['object']
                await PaymentService._handle_payment_expired(session)
            
            return {'status': 'success'}
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing webhook: {str(e)}"
            )
    
    @staticmethod
    async def _handle_payment_success(session: dict):
        """
        Handle successful payment
        """
        try:
            session_id = session.get('id')
            event_id = session.get('metadata', {}).get('event_id')
            player_id = session.get('metadata', {}).get('player_id')
            
            if not session_id or not event_id or not player_id:
                # Log error and return
                print(f"Missing data in session: {session}")
                return
            
            # Update registration status in Supabase
            registration_result = supabase.get_client().table("event_registrations").select("*").eq("stripe_session_id", session_id).single().execute()
            
            if not registration_result.data:
                # Log error and return
                print(f"Registration not found for session: {session_id}")
                return
            
            # Update the payment status
            update_result = supabase.get_client().table("event_registrations").update({"payment_status": "paid"}).eq("stripe_session_id", session_id).execute()
            
            if not update_result.data:
                print(f"Failed to update registration payment status for session: {session_id}")
            
            # Update event participant count
            event_result = supabase.get_client().table("events").select("*").eq("id", event_id).single().execute()
            if event_result.data:
                event = event_result.data
                update_result = supabase.get_client().table("events").update({"current_participants": event['current_participants'] + 1}).eq("id", event_id).execute()
                if not update_result.data:
                    print(f"Failed to update event participant count for event: {event_id}")
        except Exception as e:
            print(f"Error handling payment success: {str(e)}")
    
    @staticmethod
    async def _handle_payment_expired(session: dict):
        """
        Handle expired payment session
        """
        try:
            session_id = session.get('id')
            
            if not session_id:
                # Log error and return
                print(f"Missing session ID in expired session: {session}")
                return
            
            # Update registration status in Supabase
            registration_result = supabase.get_client().table("event_registrations").select("*").eq("stripe_session_id", session_id).single().execute()
            
            if not registration_result.data:
                # Log error and return
                print(f"Registration not found for expired session: {session_id}")
                return
            
            # Update the payment status
            update_result = supabase.get_client().table("event_registrations").update({"payment_status": "expired"}).eq("stripe_session_id", session_id).execute()
            
            if not update_result.data:
                print(f"Failed to update registration payment status for expired session: {session_id}")
        except Exception as e:
            print(f"Error handling payment expiration: {str(e)}")
    
    @staticmethod
    async def process_refund(
        registration_id: str
    ) -> dict:
        """
        Process refund for event registration
        """
        try:
            # Get registration from Supabase
            registration_result = supabase.get_client().table("event_registrations").select("*").eq("id", registration_id).single().execute()
            
            if not registration_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Registration not found"
                )
            
            registration = registration_result.data
            
            if registration["payment_status"] != 'paid':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot refund unpaid registration"
                )
            
            # Get event details
            event_result = supabase.get_client().table("events").select("*").eq("id", registration["event_id"]).single().execute()
            if not event_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Event not found"
                )
            
            try:
                # Get payment intent from session
                session = stripe.checkout.Session.retrieve(registration["stripe_session_id"])
                payment_intent = session.payment_intent
                
                # Process refund
                refund = stripe.Refund.create(
                    payment_intent=payment_intent,
                    reason="requested_by_customer"
                )
                
                # Update registration status in Supabase
                update_result = supabase.get_client().table("event_registrations").update({"payment_status": "refunded"}).eq("id", registration_id).execute()
                
                if not update_result.data:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to update registration status"
                    )
                
                return {
                    'status': 'success',
                    'refund_id': refund.id
                }
                
            except stripe.error.StripeError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Refund error: {str(e)}"
                )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing refund: {str(e)}"
            )
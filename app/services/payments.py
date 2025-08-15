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
        tournament_id: str,
        player_id: str
    ) -> dict:
        """
        Temporarily disabled: tournament registration payments are disabled during refactor
        """
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Tournament registration payments temporarily disabled during refactor"
        )
    
    @staticmethod
    async def handle_webhook(
        payload: bytes,
        sig_header: str
    ) -> dict:
        """
        Temporarily disabled: Stripe webhook processing is disabled during refactor
        """
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Stripe webhook processing temporarily disabled during payments refactor"
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
        Temporarily disabled: refunds are disabled during refactor
        """
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Refunds temporarily disabled during payments refactor"
        )
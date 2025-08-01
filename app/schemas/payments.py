"""
Payment schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional

class CreatePaymentSessionRequest(BaseModel):
    """
    Request schema for creating a payment session
    """
    event_id: str = Field(..., description="ID of the event to register for")

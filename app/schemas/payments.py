"""
Payment schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional

class CreatePaymentSessionRequest(BaseModel):
    """
    Request schema for creating a payment session
    """
    tournament_id: str = Field(..., description="ID of the tournament to register for")

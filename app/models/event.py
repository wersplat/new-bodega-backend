"""
Event model for tournament and event management
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class EventType(enum.Enum):
    DRAFT = "draft"
    BYOT = "byot"  # Bring Your Own Team
    TOURNAMENT = "tournament"
    LEAGUE = "league"

class EventStatus(enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    REGISTRATION_CLOSED = "registration_closed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    event_type = Column(Enum(EventType), nullable=False)
    status = Column(Enum(EventStatus), default=EventStatus.DRAFT)
    entry_fee = Column(Float, default=0.0)
    max_participants = Column(Integer)
    current_participants = Column(Integer, default=0)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User")
    registrations = relationship("EventRegistration", back_populates="event")
    results = relationship("EventResult", back_populates="event")
    
    def __repr__(self):
        return f"<Event(id={self.id}, name='{self.name}', status='{self.status}')>"

class EventRegistration(Base):
    __tablename__ = "event_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    payment_status = Column(String(20), default="pending")  # pending, paid, refunded
    stripe_session_id = Column(String(255), nullable=True)
    is_confirmed = Column(Boolean, default=False)
    
    # Relationships
    event = relationship("Event", back_populates="registrations")
    player = relationship("Player", back_populates="event_registrations")
    
    def __repr__(self):
        return f"<EventRegistration(event_id={self.event_id}, player_id={self.player_id})>"

class EventResult(Base):
    __tablename__ = "event_results"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    position = Column(Integer)  # 1st, 2nd, 3rd, etc.
    rp_earned = Column(Float, default=0.0)
    rp_before = Column(Float, nullable=False)
    rp_after = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    event = relationship("Event", back_populates="results")
    player = relationship("Player")
    
    def __repr__(self):
        return f"<EventResult(event_id={self.event_id}, player_id={self.player_id}, position={self.position})>" 
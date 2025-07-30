"""
Player model for NBA 2K player profiles and rankings
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class PlayerTier(enum.Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    PINK_DIAMOND = "pink_diamond"
    GALAXY_OPAL = "galaxy_opal"

class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    gamertag = Column(String(50), unique=True, index=True, nullable=False)
    platform = Column(String(20), nullable=False)  # PS5, Xbox, PC
    current_rp = Column(Float, default=0.0)
    peak_rp = Column(Float, default=0.0)
    tier = Column(Enum(PlayerTier), default=PlayerTier.BRONZE)
    team_name = Column(String(100))
    region = Column(String(50))
    bio = Column(Text)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="player")
    event_registrations = relationship("EventRegistration", back_populates="player")
    rp_history = relationship("RPHistory", back_populates="player")
    badges = relationship("PlayerBadge", back_populates="player")
    
    def __repr__(self):
        return f"<Player(id={self.id}, gamertag='{self.gamertag}', rp={self.current_rp})>"

class RPHistory(Base):
    __tablename__ = "rp_history"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    old_rp = Column(Float, nullable=False)
    new_rp = Column(Float, nullable=False)
    change_reason = Column(String(200))  # Event result, admin update, etc.
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="rp_history")
    event = relationship("Event")
    updater = relationship("User")
    
    def __repr__(self):
        return f"<RPHistory(player_id={self.player_id}, old_rp={self.old_rp}, new_rp={self.new_rp})>" 
"""
Badge model for player achievements and titles
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Badge(Base):
    __tablename__ = "badges"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    icon_url = Column(String(255))
    rarity = Column(String(20), default="common")  # common, rare, epic, legendary
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    player_badges = relationship("PlayerBadge", back_populates="badge")
    
    def __repr__(self):
        return f"<Badge(id={self.id}, name='{self.name}')>"

class PlayerBadge(Base):
    __tablename__ = "player_badges"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False)
    awarded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    awarded_at = Column(DateTime(timezone=True), server_default=func.now())
    is_equipped = Column(Boolean, default=False)
    
    # Relationships
    player = relationship("Player", back_populates="badges")
    badge = relationship("Badge", back_populates="player_badges")
    awarder = relationship("User")
    
    def __repr__(self):
        return f"<PlayerBadge(player_id={self.player_id}, badge_id={self.badge_id})>" 
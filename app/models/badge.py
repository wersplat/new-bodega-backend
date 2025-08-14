"""
Badge model for player achievements and titles
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, BigInteger
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
    
    id = Column(String, primary_key=True, index=True)
    player_wallet = Column(String, nullable=False)
    badge_type = Column(String, nullable=False)
    token_id = Column(BigInteger)
    tx_hash = Column(String)
    ipfs_uri = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    match_id = Column(BigInteger, nullable=False)
    league_id = Column(String, ForeignKey("leagues_info.id"))
    tournament_id = Column(String, ForeignKey("tournaments.id"))
    
    # Relationships
    league = relationship("LeagueInfo", back_populates="player_badges")
    tournament = relationship("Tournament", back_populates="player_badges")
    
    def __repr__(self):
        return f"<PlayerBadge(id={self.id}, player_wallet='{self.player_wallet}', badge_type='{self.badge_type}')>" 
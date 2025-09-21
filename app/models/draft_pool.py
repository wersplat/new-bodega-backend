"""
Draft Pool Model

This module defines the SQLAlchemy model for the draft pool in the system.
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

class DraftStatus(str, Enum):
    AVAILABLE = "available"
    DRAFTED = "drafted"
    WITHDRAWN = "withdrawn"
    INACTIVE = "inactive"

class DraftPool(Base):
    """
    Tracks players available for drafting in different seasons and tournaments.
    """
    __tablename__ = "draft_pool"
    __table_args__ = {
        'comment': 'Tracks players available for drafting in different seasons and tournaments'
    }
    
    # Primary key
    player_id = Column(
        UUID(as_uuid=True), 
        primary_key=True,
        index=True,
        comment='Reference to the player'
    )
    
    # Status and declaration
    declared_at = Column(
        DateTime(timezone=False), 
        server_default=func.now(),
        nullable=True,
        comment='When the player was declared for the draft'
    )
    
    status = Column(
        String, 
        default=DraftStatus.AVAILABLE, 
        nullable=True,
        server_default='available',
        comment='Current status in the draft pool'
    )
    
    # References
    season = Column(
        UUID(as_uuid=True), 
        ForeignKey("season_id.id", onupdate='CASCADE', ondelete='SET NULL'),
        nullable=True,
        comment='Reference to the league season'
    )
    
    tournament_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("tournaments.id", onupdate='CASCADE', ondelete='SET NULL'),
        nullable=True,
        comment='Reference to the tournament if tournament-specific draft'
    )
    
    league_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("leagues_info.id", onupdate='CASCADE', ondelete='SET NULL'),
        nullable=True,
        comment='Reference to the league'
    )
    
    # Draft metadata
    draft_rating = Column(
        Integer,
        nullable=True,
        comment='Rating for the player in this draft'
    )
    
    draft_notes = Column(
        Text,
        nullable=True,
        comment='Any notes about the player in this draft'
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=True,
        comment='When the record was created'
    )
    
    updated_at = Column(
        DateTime(timezone=True), 
        onupdate=func.now(),
        nullable=True,
        server_default=func.now(),
        comment='When the record was last updated'
    )
    
    # Relationships
    player = relationship("Player", back_populates="draft_pool")
    league_season = relationship("LeagueSeason", foreign_keys=[season])
    tournament = relationship("Tournament", foreign_keys=[tournament_id])
    league = relationship("LeagueInfo", foreign_keys=[league_id])
    
    def __repr__(self):
        return f"<DraftPool(player_id={self.player_id}, status='{self.status}')>"
    
    def to_dict(self):
        """Convert model to dictionary for API responses."""
        return {
            "player_id": str(self.player_id) if self.player_id else None,
            "declared_at": self.declared_at.isoformat() if self.declared_at else None,
            "status": self.status,
            "season": str(self.season) if self.season else None,
            "tournament_id": str(self.tournament_id) if self.tournament_id else None,
            "league_id": str(self.league_id) if self.league_id else None,
            "draft_rating": self.draft_rating,
            "draft_notes": self.draft_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
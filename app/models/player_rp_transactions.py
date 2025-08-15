"""
Player RP Transactions Model

This module defines the SQLAlchemy model for tracking player ranking point (RP) transactions.
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, CheckConstraint, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class RPTransactionType(str, enum.Enum):
    """Enumeration of RP transaction types."""
    EVENT = 'event'
    BONUS = 'bonus'
    PENALTY = 'penalty'
    ADJUSTMENT = 'adjustment'
    MATCH = 'match'


class PlayerRPTransaction(Base):
    """
    SQLAlchemy model representing player RP (Ranking Points) transactions.
    
    This model tracks all RP changes for players, including the source of the change
    (match, tournament, manual adjustment, etc.) and the amount changed.
    """
    __tablename__ = 'player_rp_transactions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    player_id = Column(UUID(as_uuid=True), ForeignKey('players.id'), nullable=True, index=True)
    match_id = Column(UUID(as_uuid=True), ForeignKey('matches.id'), nullable=True, index=True)
    amount = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    type = Column(Enum(RPTransactionType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    league_id = Column(UUID(as_uuid=True), ForeignKey('leagues_info.id', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    tournament_id = Column(UUID(as_uuid=True), ForeignKey('tournaments.id', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    
    # Relationships
    player = relationship('Player', back_populates='rp_transactions')
    match = relationship('Match', back_populates='rp_transactions')
    league = relationship('LeagueInfo', back_populates='rp_transactions')
    tournament = relationship('Tournament', back_populates='rp_transactions')
    
    __table_args__ = (
        CheckConstraint(
            "type IN ('event', 'bonus', 'penalty', 'adjustment', 'match')",
            name='player_rp_transactions_type_check'
        ),
    )
    
    def __repr__(self):
        return f"<PlayerRPTransaction(id={self.id}, player_id={self.player_id}, amount={self.amount}, type='{self.type}')>"
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            'id': str(self.id),
            'player_id': str(self.player_id) if self.player_id else None,
            'match_id': str(self.match_id) if self.match_id else None,
            'amount': self.amount,
            'description': self.description,
            'type': self.type.value if self.type else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'league_id': str(self.league_id) if self.league_id else None,
            'tournament_id': str(self.tournament_id) if self.tournament_id else None
        }
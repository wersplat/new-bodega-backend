"""
Player RP Transactions Model

This module defines the SQLAlchemy model for player RP transactions.
"""
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
import uuid

class PlayerRPTransaction(Base):
    """
    SQLAlchemy model representing RP (Ranking Points) transactions for players.
    """
    __tablename__ = "player_rp_transactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    player_id = Column(String, ForeignKey("players.id"), nullable=False)
    league_id = Column(String, ForeignKey("leagues_info.id"), nullable=True)
    tournament_id = Column(String, ForeignKey("tournaments.id"), nullable=True)
    match_id = Column(String, ForeignKey("matches.id"), nullable=True)
    amount = Column(Integer, nullable=False)
    transaction_type = Column(String, nullable=False)  # e.g., 'award', 'penalty', 'adjustment'
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_by = Column(String, nullable=True)  # User ID of who processed this
    
    # Relationships
    player = relationship("Player", back_populates="rp_transactions")
    league = relationship("League", back_populates="player_rp_transactions")
    tournament = relationship("Tournament", back_populates="player_rp_transactions")
    match = relationship("Match")
    
    def __repr__(self):
        return f"<PlayerRPTransaction(id={self.id}, player_id={self.player_id}, amount={self.amount})>"
    
    def to_dict(self):
        """Convert the transaction to a dictionary."""
        return {
            'id': self.id,
            'player_id': self.player_id,
            'league_id': self.league_id,
            'tournament_id': self.tournament_id,
            'match_id': self.match_id,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'processed_by': self.processed_by
        }
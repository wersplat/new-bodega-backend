from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base
from enum import Enum

class AwardType(str, Enum):
    OFFENSIVE_MVP = "Offensive MVP"
    DEFENSIVE_MVP = "Defensive MVP"
    ROOKIE_OF_TOURNAMENT = "Rookie of Tournament"

class AwardsRace(Base):
    """
    Tracks player performance in award races across tournaments and leagues.
    """
    __tablename__ = "awards_race"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    award_type = Column(String, nullable=False)  # Uses AwardType enum
    rank = Column(Integer, nullable=True)  # Current rank in the race
    rp_bonus = Column(Integer, nullable=True)  # RP bonus for this award position
    award_winner = Column(Boolean, default=False)  # Whether this player won the award
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign keys
    player_id = Column(String, ForeignKey("players.id"), nullable=True)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    league_id = Column(String, ForeignKey("leagues_info.id"), nullable=True)
    tournament_id = Column(String, ForeignKey("tournaments.id"), nullable=True)
    
    # Relationships
    player = relationship("Player", back_populates="awards_race")
    team = relationship("Team", back_populates="awards_race")
    league = relationship("LeagueInfo", back_populates="awards_race")
    tournament = relationship("Tournament", back_populates="awards_race")
    
    def __repr__(self):
        return f"<AwardsRace(id={self.id}, type='{self.award_type}', player_id={self.player_id}, rank={self.rank})>"
    
    def to_dict(self):
        """Convert model to dictionary for API responses."""
        return {
            "id": self.id,
            "award_type": self.award_type,
            "rank": self.rank,
            "rp_bonus": self.rp_bonus,
            "award_winner": self.award_winner,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "player_id": self.player_id,
            "team_id": self.team_id,
            "league_id": self.league_id,
            "tournament_id": self.tournament_id
        }
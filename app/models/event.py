"""
Updated Event models for the new schema with leagues and tournaments
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum, Boolean, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class AwardType(enum.Enum):
    OFFENSIVE_MVP = "Offensive MVP"
    DEFENSIVE_MVP = "Defensive MVP"
    ROOKIE_OF_TOURNAMENT = "Rookie of Tournament"

class Stage(enum.Enum):
    REGULAR_SEASON = "Regular Season"
    GROUP_PLAY = "Group Play"
    ROUND_1 = "Round 1"
    ROUND_2 = "Round 2"
    ROUND_3 = "Round 3"
    ROUND_4 = "Round 4"
    SEMI_FINALS = "Semi Finals"
    FINALS = "Finals"
    GRAND_FINALS = "Grand Finals"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"
    L5 = "L5"
    W1 = "W1"
    W2 = "W2"
    W3 = "W3"
    W4 = "W4"
    LF = "LF"
    WF = "WF"

class Status(enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    UNDER_REVIEW = "under_review"
    REVIEWED = "reviewed"
    APPROVED = "approved"

class AwardsRace(Base):
    __tablename__ = "awards_race"
    
    id = Column(String, primary_key=True, index=True)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    player_id = Column(String, ForeignKey("players.id"))
    award_type = Column(Enum(AwardType, name="award_types"))
    rank = Column(Integer)
    rp_bonus = Column(BigInteger)
    award_winner = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    league_id = Column(String, ForeignKey("leagues_info.id"))
    tournament_id = Column(String, ForeignKey("tournaments.id"))
    
    # Relationships
    team = relationship("Team")
    player = relationship("Player")
    league = relationship("LeagueInfo", back_populates="awards_race")
    tournament = relationship("Tournament", back_populates="awards_race")
    
    def __repr__(self):
        return f"<AwardsRace(id={self.id}, team_id='{self.team_id}', award_type='{self.award_type}')>"

class DraftPool(Base):
    __tablename__ = "draft_pool"
    
    player_id = Column(String, ForeignKey("players.id"), primary_key=True)
    declared_at = Column(DateTime, server_default=func.now())
    status = Column(String, default="available")
    season = Column(String)
    draft_rating = Column(Integer)
    draft_notes = Column(Text)
    league_id = Column(String, ForeignKey("leagues_info.id"))
    tournament_id = Column(String, ForeignKey("tournaments.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    player = relationship("Player")
    league = relationship("LeagueInfo", back_populates="draft_pool")
    tournament = relationship("Tournament", back_populates="draft_pool")
    
    def __repr__(self):
        return f"<DraftPool(player_id='{self.player_id}', status='{self.status}')>"

class EventResult(Base):
    __tablename__ = "event_results"
    
    id = Column(String, primary_key=True, index=True)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    placement = Column(Integer)
    rp_awarded = Column(Integer)
    bonus_rp = Column(Integer, default=0)
    total_rp = Column(Integer)  # Computed field: rp_awarded + bonus_rp
    awarded_at = Column(DateTime, server_default=func.date(func.now()))
    prize_amount = Column(Integer)
    winner_banner_url = Column(String)
    league_id = Column(String, ForeignKey("leagues_info.id"))
    tournament_id = Column(String, ForeignKey("tournaments.id"))
    
    # Relationships
    team = relationship("Team")
    league = relationship("LeagueInfo", back_populates="event_results")
    tournament = relationship("Tournament", back_populates="event_results")
    
    def __repr__(self):
        return f"<EventResult(id={self.id}, team_id='{self.team_id}', placement={self.placement})>"

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(String, primary_key=True, index=True)
    team_a_id = Column(String, ForeignKey("teams.id"))
    team_b_id = Column(String, ForeignKey("teams.id"))
    winner_id = Column(String, ForeignKey("teams.id"))
    score_a = Column(Integer)
    score_b = Column(Integer)
    played_at = Column(DateTime, server_default=func.now())
    boxscore_url = Column(String, unique=True)
    team_a_name = Column(String)
    stage = Column(Enum(Stage, name="stage"))
    game_number = Column(Integer)
    team_b_name = Column(String)
    winner_name = Column(String)
    league_id = Column(String, ForeignKey("leagues_info.id"))
    tournament_id = Column(String, ForeignKey("tournaments.id"))
    league_season = Column(String, ForeignKey("league_seasons.id"))
    
    # Relationships
    team_a = relationship("Team", foreign_keys=[team_a_id])
    team_b = relationship("Team", foreign_keys=[team_b_id])
    winner = relationship("Team", foreign_keys=[winner_id])
    league = relationship("LeagueInfo", back_populates="matches")
    tournament = relationship("Tournament", back_populates="matches")
    
    def __repr__(self):
        return f"<Match(id={self.id}, team_a='{self.team_a_name}', team_b='{self.team_b_name}')>"

class PlayerRPTransaction(Base):
    __tablename__ = "player_rp_transactions"
    
    id = Column(String, primary_key=True, index=True)
    player_id = Column(String, ForeignKey("players.id"))
    match_id = Column(String, ForeignKey("matches.id"))
    amount = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    league_id = Column(String, ForeignKey("leagues_info.id"))
    tournament_id = Column(String, ForeignKey("tournaments.id"))
    
    # Relationships
    player = relationship("Player")
    match = relationship("Match")
    league = relationship("LeagueInfo", back_populates="player_rp_transactions")
    tournament = relationship("Tournament", back_populates="player_rp_transactions")
    
    def __repr__(self):
        return f"<PlayerRPTransaction(id={self.id}, player_id='{self.player_id}', amount={self.amount})>"

class RankingPoints(Base):
    __tablename__ = "ranking_points"
    
    id = Column(String, primary_key=True, index=True)
    team_id = Column(String, ForeignKey("teams.id"))
    source = Column(String)
    points = Column(Integer)
    awarded_at = Column(DateTime, server_default=func.date(func.now()))
    expires_at = Column(DateTime)
    league_id = Column(String, ForeignKey("leagues_info.id"))
    tournament_id = Column(String, ForeignKey("tournaments.id"))
    
    # Relationships
    team = relationship("Team")
    league = relationship("LeagueInfo", back_populates="ranking_points")
    tournament = relationship("Tournament", back_populates="ranking_points")
    
    def __repr__(self):
        return f"<RankingPoints(id={self.id}, team_id='{self.team_id}', points={self.points})>"

class RPTransaction(Base):
    __tablename__ = "rp_transactions"
    
    id = Column(String, primary_key=True, index=True)
    team_id = Column(String, ForeignKey("teams.id"))
    amount = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    league_id = Column(String, ForeignKey("leagues_info.id"))
    tournament_id = Column(String, ForeignKey("tournaments.id"))
    
    # Relationships
    team = relationship("Team")
    league = relationship("LeagueInfo", back_populates="rp_transactions")
    tournament = relationship("Tournament", back_populates="rp_transactions")
    
    def __repr__(self):
        return f"<RPTransaction(id={self.id}, team_id='{self.team_id}', amount={self.amount})>"

class TeamRoster(Base):
    __tablename__ = "team_rosters"
    
    id = Column(String, primary_key=True, index=True)
    team_id = Column(String, ForeignKey("teams.id"))
    player_id = Column(String, ForeignKey("players.id"))
    is_captain = Column(Boolean, default=False)
    is_player_coach = Column(Boolean, default=False)
    joined_at = Column(DateTime, server_default=func.now())
    left_at = Column(DateTime)
    league_id = Column(String, ForeignKey("leagues_info.id"))
    tournament_id = Column(String, ForeignKey("tournaments.id"))
    
    # Relationships
    team = relationship("Team")
    player = relationship("Player")
    league = relationship("LeagueInfo", back_populates="team_rosters")
    tournament = relationship("Tournament", back_populates="team_rosters")
    
    def __repr__(self):
        return f"<TeamRoster(id={self.id}, team_id='{self.team_id}', player_id='{self.player_id}')>"

class TeamsPotTracker(Base):
    __tablename__ = "teams_pot_tracker"
    
    id = Column(String, primary_key=True, index=True)
    team_id = Column(String, ForeignKey("teams.id"))
    placement = Column(Integer)
    prize_amount = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    league_id = Column(String, ForeignKey("leagues_info.id"))
    tournament_id = Column(String, ForeignKey("tournaments.id"))
    
    # Relationships
    team = relationship("Team")
    league = relationship("LeagueInfo", back_populates="teams_pot_tracker")
    tournament = relationship("Tournament", back_populates="teams_pot_tracker")
    
    def __repr__(self):
        return f"<TeamsPotTracker(id={self.id}, team_id='{self.team_id}', placement={self.placement})>"

class UpcomingMatch(Base):
    __tablename__ = "upcoming_matches"
    
    id = Column(String, primary_key=True, index=True)
    team_a_id = Column(String, ForeignKey("teams.id"))
    team_b_id = Column(String, ForeignKey("teams.id"))
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    venue = Column(String)
    stream_url = Column(String)
    notes = Column(Text)
    status = Column(String, default="scheduled")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    group_id = Column(String, ForeignKey("event_groups.id"))
    round = Column(Integer)
    match_number = Column(Integer)
    team_a_logo = Column(String)
    team_b_logo = Column(String)
    league_id = Column(String, ForeignKey("leagues_info.id"))
    tournament_id = Column(String, ForeignKey("tournaments.id"))
    
    # Relationships
    team_a = relationship("Team", foreign_keys=[team_a_id])
    team_b = relationship("Team", foreign_keys=[team_b_id])
    event_group = relationship("EventGroup")
    league = relationship("LeagueInfo", back_populates="upcoming_matches")
    tournament = relationship("Tournament", back_populates="upcoming_matches")
    
    def __repr__(self):
        return f"<UpcomingMatch(id={self.id}, team_a='{self.team_a_id}', team_b='{self.team_b_id}')>"

class MatchSubmission(Base):
    __tablename__ = "match_submissions"
    
    id = Column(String, primary_key=True, index=True)
    match_id = Column(String, ForeignKey("matches.id"))
    team_a_id = Column(String, ForeignKey("teams.id"))
    team_a_name = Column(String)
    team_b_id = Column(String, ForeignKey("teams.id"))
    team_b_name = Column(String)
    review_status = Column(String)
    reviewed_by = Column(String)
    reviewed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    review_notes = Column(Text)
    status = Column(String)
    payload = Column(Text)  # JSON field
    league_id = Column(String, ForeignKey("leagues_info.id"))
    tournament_id = Column(String, ForeignKey("tournaments.id"))
    
    # Relationships
    match = relationship("Match")
    team_a = relationship("Team", foreign_keys=[team_a_id])
    team_b = relationship("Team", foreign_keys=[team_b_id])
    league = relationship("LeagueInfo", back_populates="match_submissions")
    tournament = relationship("Tournament", back_populates="match_submissions")
    
    def __repr__(self):
        return f"<MatchSubmission(id={self.id}, match_id='{self.match_id}', status='{self.status}')>"

# Note: PlayerBadge model is defined in badge.py to avoid conflicts 
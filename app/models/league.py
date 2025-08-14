"""
League and Tournament models for the updated schema
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum, Boolean, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class LeagueType(enum.Enum):
    UPA = "UPA"
    UPA_COLLEGE = "UPA College"
    WR = "WR"
    MPBA = "MPBA"
    RISING_STARS = "Rising Stars"
    STATEN_ISLAND_BASKETBALL_ASSOCIATION = "Staten Island Basketball Association"
    HALL_OF_FAME_LEAGUE = "Hall Of Fame League"
    DUNK_LEAGUE = "Dunk League"
    ROAD_TO_25K = "Road to 25K"

class TournamentStatus(enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    UNDER_REVIEW = "under_review"
    REVIEWED = "reviewed"
    APPROVED = "approved"

class EventTier(enum.Enum):
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"
    T4 = "T4"

class Console(enum.Enum):
    CROSS_PLAY = "Cross Play"
    PLAYSTATION = "Playstation"
    XBOX = "Xbox"

class GameYear(enum.Enum):
    K16 = "2K16"
    K17 = "2K17"
    K18 = "2K18"
    K19 = "2K19"
    K20 = "2K20"
    K21 = "2K21"
    K22 = "2K22"
    K23 = "2K23"
    K24 = "2K24"
    K25 = "2K25"
    K26 = "2K26"

class LeagueInfo(Base):
    __tablename__ = "leagues_info"
    
    id = Column(String, primary_key=True, index=True)
    league = Column(Enum(LeagueType, name="leagues"), unique=True, nullable=False)
    lg_logo_url = Column(String)
    lg_url = Column(String)
    lg_discord = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    twitter_id = Column(String)
    twitch_url = Column(String)
    sponsor_info = Column(Text)
    
    # Relationships
    tournaments = relationship("Tournament", back_populates="organizer")
    awards_race = relationship("AwardsRace", back_populates="league")
    draft_pool = relationship("DraftPool", back_populates="league")
    event_results = relationship("EventResult", back_populates="league")
    matches = relationship("Match", back_populates="league")
    player_rp_transactions = relationship("PlayerRPTransaction", back_populates="league")
    ranking_points = relationship("RankingPoints", back_populates="league")
    rp_transactions = relationship("RPTransaction", back_populates="league")
    team_rosters = relationship("TeamRoster", back_populates="league")
    teams_pot_tracker = relationship("TeamsPotTracker", back_populates="league")
    upcoming_matches = relationship("UpcomingMatch", back_populates="league")
    match_submissions = relationship("MatchSubmission", back_populates="league")
    player_badges = relationship("PlayerBadge", back_populates="league")
    past_champions = relationship("PastChampion", back_populates="league")
    
    def __repr__(self):
        return f"<LeagueInfo(id={self.id}, league='{self.league}')>"

class Tournament(Base):
    __tablename__ = "tournaments"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    organizer_id = Column(String, ForeignKey("leagues_info.id"))
    sponsor = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    prize_pool = Column(BigInteger)
    runner_up = Column(String, ForeignKey("teams.id"))
    place = Column(String, ForeignKey("teams.id"))
    organizer_logo_url = Column(String)
    game_year = Column(Enum(GameYear, name="game_year"))
    console = Column(Enum(Console, name="console"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    banner_url = Column(String)
    rules_url = Column(String)
    status = Column(Enum(TournamentStatus, name="status"))
    tier = Column(Enum(EventTier, name="event_tier"))
    max_rp = Column(Integer)
    description = Column(Text)
    decay_days = Column(Integer)
    champion = Column(String, ForeignKey("teams.id"))
    sponsor_logo = Column(String)
    processed_at = Column(DateTime(timezone=True))
    
    # Relationships
    organizer = relationship("LeagueInfo", back_populates="tournaments")
    champion_team = relationship("Team", foreign_keys=[champion])
    runner_up_team = relationship("Team", foreign_keys=[runner_up])
    place_team = relationship("Team", foreign_keys=[place])
    awards_race = relationship("AwardsRace", back_populates="tournament")
    draft_pool = relationship("DraftPool", back_populates="tournament")
    event_results = relationship("EventResult", back_populates="tournament")
    matches = relationship("Match", back_populates="tournament")
    player_rp_transactions = relationship("PlayerRPTransaction", back_populates="tournament")
    ranking_points = relationship("RankingPoints", back_populates="tournament")
    rp_transactions = relationship("RPTransaction", back_populates="tournament")
    team_rosters = relationship("TeamRoster", back_populates="tournament")
    teams_pot_tracker = relationship("TeamsPotTracker", back_populates="tournament")
    upcoming_matches = relationship("UpcomingMatch", back_populates="tournament")
    match_submissions = relationship("MatchSubmission", back_populates="tournament")
    player_badges = relationship("PlayerBadge", back_populates="tournament")
    past_champions = relationship("PastChampion", back_populates="tournament")
    
    def __repr__(self):
        return f"<Tournament(id={self.id}, name='{self.name}', status='{self.status}')>"

class PastChampion(Base):
    __tablename__ = "past_champions"
    
    id = Column(String, primary_key=True, index=True)
    season = Column(Integer)
    team_id = Column(String, ForeignKey("teams.id"))
    team_name = Column(String)
    event_tier = Column(Enum(EventTier, name="event_tier"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    champion_logo = Column(String)
    lg_logo = Column(String)
    console = Column(Enum(Console, name="console"))
    league_name = Column(Enum(LeagueType, name="leagues"))
    year = Column(Enum(GameYear, name="game_year"))
    is_tournament = Column(Boolean, default=False)
    tournament_id = Column(String, ForeignKey("tournaments.id"))
    league_id = Column(String, ForeignKey("leagues_info.id"))
    tournament_date = Column(DateTime)
    
    # Relationships
    team = relationship("Team")
    tournament = relationship("Tournament", back_populates="past_champions")
    league = relationship("LeagueInfo", back_populates="past_champions")
    
    def __repr__(self):
        return f"<PastChampion(id={self.id}, team_name='{self.team_name}', season={self.season})>"

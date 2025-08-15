"""
Team model for NBA 2K teams
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from .league import LeagueSeason

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    logo_url = Column(String, unique=True)
    current_rp = Column(Integer, default=0)
    elo_rating = Column(Float, default=1500.0)
    global_rank = Column(Integer)
    leaderboard_tier = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    player_rank_score = Column(Float)
    money_won = Column(Integer)
    
    # Relationships
    players = relationship("Player", foreign_keys="Player.current_team_id")
    team_rosters = relationship("TeamRoster", back_populates="team")
    player_stats = relationship("PlayerStats", back_populates="team")
    matches_as_team_a = relationship("Match", foreign_keys="Match.team_a_id")
    matches_as_team_b = relationship("Match", foreign_keys="Match.team_b_id")
    matches_as_winner = relationship("Match", foreign_keys="Match.winner_id", back_populates="winner")
    upcoming_matches_as_team_a = relationship("UpcomingMatch", foreign_keys="UpcomingMatch.team_a_id", back_populates="team_a")
    upcoming_matches_as_team_b = relationship("UpcomingMatch", foreign_keys="UpcomingMatch.team_b_id", back_populates="team_b")
    event_results = relationship("TournamentResult", back_populates="team")
    ranking_points = relationship("RankingPoints", back_populates="team")
    rp_transactions = relationship("RPTransaction", back_populates="team")
    teams_pot_tracker = relationship("TeamsPotTracker", back_populates="team")
    awards_race = relationship("AwardsRace", back_populates="team")
    match_submissions_as_team_a = relationship("MatchSubmission", foreign_keys="MatchSubmission.team_a_id")
    match_submissions_as_team_b = relationship("MatchSubmission", foreign_keys="MatchSubmission.team_b_id")
    team_match_stats = relationship("TeamMatchStats", back_populates="team")
    match_points = relationship("MatchPoints", back_populates="team")
    tournament_groups_members = relationship("TournamentGroupMember", back_populates="team")
    group_standings = relationship("GroupStanding", back_populates="team")
    past_champions = relationship("PastChampion", back_populates="team")
    tournaments_as_champion = relationship("Tournament", foreign_keys="Tournament.champion")
    tournaments_as_runner_up = relationship("Tournament", foreign_keys="Tournament.runner_up")
    tournaments_as_place = relationship("Tournament", foreign_keys="Tournament.place")
    
    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}', rp={self.current_rp})>"

class TeamMatchStats(Base):
    __tablename__ = "team_match_stats"
    
    id = Column(String, primary_key=True, index=True)
    match_id = Column(String, ForeignKey("matches.id"), nullable=False)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    points = Column(Integer, nullable=False)
    rebounds = Column(Integer, nullable=False)
    assists = Column(Integer, nullable=False)
    steals = Column(Integer, nullable=False)
    blocks = Column(Integer, nullable=False)
    turnovers = Column(Integer, nullable=False)
    field_goals_made = Column(Integer, nullable=False)
    field_goals_attempted = Column(Integer, nullable=False)
    three_points_made = Column(Integer, nullable=False)
    three_points_attempted = Column(Integer, nullable=False)
    free_throws_made = Column(Integer, nullable=False)
    free_throws_attempted = Column(Integer, nullable=False)
    fouls = Column(Integer)
    plus_minus = Column(Integer)
    
    # Relationships
    match = relationship("Match")
    team = relationship("Team", back_populates="team_match_stats")
    
    def __repr__(self):
        return f"<TeamMatchStats(id={self.id}, team_id='{self.team_id}', points={self.points})>"

class MatchPoints(Base):
    __tablename__ = "match_points"
    
    id = Column(String, primary_key=True, index=True)
    match_id = Column(String, ForeignKey("matches.id"), nullable=False)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    group_id = Column(String, ForeignKey("tournament_groups.id"))
    points_earned = Column(Integer, nullable=False)
    point_type = Column(String, nullable=False)  # win_by_20_plus, regular_win, loss, forfeit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    match = relationship("Match")
    team = relationship("Team", back_populates="match_points")
    group = relationship("TournamentGroup", back_populates="match_points")
    
    def __repr__(self):
        return f"<MatchPoints(id={self.id}, team_id='{self.team_id}', points_earned={self.points_earned})>"

class TournamentGroup(Base):
    __tablename__ = "tournament_groups"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    max_teams = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(String, default="active")
    advancement_count = Column(Integer, default=2)
    sort_order = Column(Integer)
    tournament_id = Column(String, ForeignKey("tournaments.id"))
    league_season_id = Column(String, ForeignKey("league_seasons.id"))
    
    # Relationships
    tournament = relationship("Tournament", back_populates="tournament_groups")
    league_season = relationship(
        "LeagueSeason", 
        back_populates="tournament_groups",
        foreign_keys=[league_season_id]
    )
    members = relationship(
        "TournamentGroupMember", 
        back_populates="group",
        cascade="all, delete-orphan"
    )
    matches = relationship(
        "GroupMatch", 
        back_populates="group",
        cascade="all, delete-orphan"
    )
    standings = relationship(
        "GroupStanding", 
        back_populates="group",
        cascade="all, delete-orphan"
    )
    upcoming_matches = relationship("UpcomingMatch", back_populates="tournament_group")
    match_points = relationship("MatchPoints", back_populates="group")
    
    def __repr__(self):
        return f"<TournamentGroup(id={self.id}, name='{self.name}')>"

class TournamentGroupMember(Base):
    __tablename__ = "tournament_groups_members"
    
    id = Column(String, primary_key=True, index=True)
    group_id = Column(String, ForeignKey("tournament_groups.id"), nullable=False)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    seed = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    group = relationship("TournamentGroup", back_populates="members")
    team = relationship("Team", back_populates="tournament_groups_members")
    
    def __repr__(self):
        return f"<TournamentGroupMember(id={self.id}, group_id='{self.group_id}', team_id='{self.team_id}')>"

class GroupMatch(Base):
    __tablename__ = "group_matches"
    
    id = Column(String, primary_key=True, index=True)
    group_id = Column(String, ForeignKey("tournament_groups.id"), nullable=False)
    match_id = Column(String, ForeignKey("matches.id"), nullable=False)
    round = Column(Integer, nullable=False)
    match_number = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    group = relationship("TournamentGroup", back_populates="matches")
    match = relationship("Match")
    
    def __repr__(self):
        return f"<GroupMatch(id={self.id}, group_id='{self.group_id}', match_id='{self.match_id}')>"

class GroupStanding(Base):
    __tablename__ = "group_standings"
    
    id = Column(String, primary_key=True, index=True)
    group_id = Column(String, ForeignKey("tournament_groups.id"), nullable=False)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    matches_played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    points_for = Column(Integer, default=0)
    points_against = Column(Integer, default=0)
    point_differential = Column(Integer)  # Computed field
    position = Column(Integer)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    group = relationship("TournamentGroup", back_populates="standings")
    team = relationship("Team", back_populates="group_standings")
    
    def __repr__(self):
        return f"<GroupStanding(id={self.id}, group_id='{self.group_id}', team_id='{self.team_id}')>"

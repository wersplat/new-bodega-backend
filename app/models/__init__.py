"""
Models Package

This package contains all SQLAlchemy models for the application.
"""
from app.models.match import Match, MatchStatus
from app.models.match_mvp import MatchMVP
from app.models.match_stats import MatchStats
from app.models.matchSubmission import MatchSubmission
from app.models.player import Player
from app.models.team import Team
from app.models.teamPlayer import TeamPlayer
from app.models.league import League, LeagueStatus
from app.models.leagueTeam import LeagueTeam
from app.models.league import Tournament, TournamentStatus, TournamentTier
from app.models.team import TournamentGroup, TournamentGroupMember, GroupMatch, GroupStanding

from app.models.tournament_result import TournamentResult
from app.models.teamsPotTracker import TeamsPotTracker
from app.models.upcomingMatch import UpcomingMatch
from app.models.awardRace import AwardsRace
from app.models.badge import Badge
from app.core.database import Base

# Re-export all models for easier imports
__all__ = [
    'Base',
    'Match',
    'MatchStatus',
    'MatchMVP',
    'MatchStats',
    'MatchSubmission',
    'Player',
    'Team',
    'TeamPlayer',
    'League',
    'LeagueStatus',
    'LeagueTeam',
    'Tournament',
    'TournamentStatus',
    'TournamentTier',
    'TournamentGroup',
    'TournamentGroupMember',
    'GroupMatch',
    'GroupStanding',
    'TournamentResult',
    'TeamsPotTracker',
    'UpcomingMatch',
    'AwardsRace',
    'Badge'
]
"""
Models Package

This package contains all SQLAlchemy models for the application.
"""
from app.models.match import Match, MatchStatus
from app.models.match_mvp import MatchMVP
from app.models.match_stats import MatchStats
from app.models.matchSubmission import MatchSubmission
from app.models.player import Player, PlayerStatus
from app.models.team import Team, TeamStatus
from app.models.teamPlayer import TeamPlayer
from app.models.league import League, LeagueStatus, LeagueVisibility
from app.models.leagueTeam import LeagueTeam
from app.models.tournament import Tournament, TournamentStatus, TournamentTier
from app.models.tournament_group import TournamentGroup, GroupStageType, GroupTiebreaker
from app.models.tournament_group_member import TournamentGroupMember
from app.models.tournament_result import TournamentResult
from app.models.teamsPotTracker import TeamsPotTracker
from app.models.upcomingMatch import UpcomingMatch
from app.models.awardRace import AwardRace
from app.models.badge import Badge, BadgeType, BadgeTier
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
    'PlayerStatus',
    'Team',
    'TeamStatus',
    'TeamPlayer',
    'League',
    'LeagueStatus',
    'LeagueVisibility',
    'LeagueTeam',
    'Tournament',
    'TournamentStatus',
    'TournamentTier',
    'TournamentGroup',
    'GroupStageType',
    'GroupTiebreaker',
    'TournamentGroupMember',
    'TournamentResult',
    'TeamsPotTracker',
    'UpcomingMatch',
    'AwardRace',
    'Badge',
    'BadgeType',
    'BadgeTier'
]
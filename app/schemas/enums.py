"""
Database Enums

Enums matching the Supabase database schema types.
These should be kept in sync with the TypeScript types.
"""

from enum import Enum

class GameYear(str, Enum):
    """Game year enum matching database"""
    _2K16 = "2K16"
    _2K17 = "2K17"
    _2K18 = "2K18"
    _2K19 = "2K19"
    _2K20 = "2K20"
    _2K21 = "2K21"
    _2K22 = "2K22"
    _2K23 = "2K23"
    _2K24 = "2K24"
    _2K25 = "2K25"
    _2K26 = "2K26"

class EventTier(str, Enum):
    """Event tier enum matching database"""
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"
    T4 = "T4"
    T5 = "T5"

class AchievementTier(str, Enum):
    """Achievement tier enum matching database"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    COMMON = "common"
    RARE = "rare"
    LEGENDARY = "legendary"
    EPIC = "epic"

class AchievementScope(str, Enum):
    """Achievement scope enum matching database"""
    PER_GAME = "per_game"
    SEASON = "season"
    CAREER = "career"
    STREAK = "streak"
    EVENT = "event"

class AchievementCategory(str, Enum):
    """Achievement category enum matching database"""
    SCORING = "Scoring"
    ASSISTS = "Assists"
    DEFENSE = "Defense"
    REBOUNDING = "Rebounding"
    MIXED_STATS = "Mixed Stats"
    STREAK_LONGEVITY = "Streak & Longevity"
    LEGENDARY = "Legendary"

class AchievementRarity(str, Enum):
    """Achievement rarity enum matching database"""
    COMMON = "Common"
    RARE = "Rare"
    EPIC = "Epic"
    LEGENDARY = "Legendary"

class AchievementType(str, Enum):
    """Achievement type enum matching database"""
    CAREER_POINTS_MILESTONE = "Career Points Milestone"
    SINGLE_GAME = "Single Game"
    EFFICIENCY = "Efficiency"
    SEASON = "Season"
    CAREER_MILESTONES = "Career Milestones"
    BLOCKS = "Blocks"
    STEALS = "Steals"
    LOCKDOWN = "Lockdown"
    STREAK = "Streak"
    LONGEVITY = "Longevity"
    MIXED_STATS = "Mixed Stats"

class EventType(str, Enum):
    """Event type enum matching database"""
    LEAGUE = "League"
    TOURNAMENT = "Tournament"
    MATCH_EVENT = "match_event"
    PLAYER_STAT_EVENT = "player_stat_event"

class Status(str, Enum):
    """Status enum matching database"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in progress"
    COMPLETED = "completed"
    UNDER_REVIEW = "under review"
    REVIEWED = "reviewed"
    APPROVED = "approved"

class Stage(str, Enum):
    """Match/tournament stage enum matching database"""
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
    PLAYOFFS = "Playoffs"
    OPEN = "Open"

class PlayerPosition(str, Enum):
    """Player position enum matching database"""
    POINT_GUARD = "Point Guard"
    SHOOTING_GUARD = "Shooting Guard"
    LOCK = "Lock"
    POWER_FORWARD = "Power Forward"
    CENTER = "Center"

class SalaryTier(str, Enum):
    """Salary tier enum matching database"""
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"

class Console(str, Enum):
    """Console enum matching database"""
    CROSS_PLAY = "Cross Play"
    PLAYSTATION = "Playstation"
    XBOX = "Xbox"

class Leagues(str, Enum):
    """Leagues enum matching database"""
    UPA = "Unified Pro Am Association"
    UPA_COLLEGE = "UPA College"
    WR = "WR"
    MPBA = "MPBA"
    RISING_STARS = "Rising Stars"
    SIBA = "Staten Island Basketball Association"
    HOF = "Hall Of Fame League"
    DUNK_LEAGUE = "Dunk League"
    ROAD_TO_25K = "Road to 25K"
    ASSOCIATION = "Association"
    USA_BASKETBALL = "USA Basketball"
    HOF_EU = "HOF EU"
    UPA_EU = "UPA EU"

class QueueSlotStatus(str, Enum):
    """Queue slot status enum matching database"""
    WAITING = "waiting"
    MATCHED = "matched"
    LEFT = "left"

class TeamQueueSlotStatus(str, Enum):
    """Team queue slot status enum matching database"""
    WAITING = "waiting"
    PENDING_LINEUP = "pending_lineup"
    READY = "ready"
    MATCHED = "matched"
    LEFT = "left"

class MatchSnapshotStatus(str, Enum):
    """Match snapshot status enum matching database"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MatchReportStatus(str, Enum):
    """Match report status enum matching database"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    VERIFIED = "verified"
    DISPUTED = "disputed"

class RosterSourceType(str, Enum):
    """Roster source type enum matching database"""
    LEAGUE = "league"
    CURRENT = "current"

class AppRole(str, Enum):
    """Application role enum matching database"""
    ADMIN = "admin"
    LEAGUE_STAFF = "league_staff"
    USER = "user"
    EDITOR = "editor"
    ANALYST = "analyst"
    TEAM_STAFF = "team_staff"
    PLAYER = "player"

class AwardTypes(str, Enum):
    """Award types enum matching database"""
    OFFENSIVE_MVP = "Offensive MVP"
    DEFENSIVE_MVP = "Defensive MVP"
    ROOKIE_OF_TOURNAMENT = "Rookie of Tournament"

class CounterScope(str, Enum):
    """Counter scope enum matching database"""
    CAREER = "career"
    SEASON = "season"
    ROLLING10 = "rolling10"
    GAME = "game"

class TournamentFormat(str, Enum):
    """Tournament format enum matching database"""
    SINGLE_ELIMINATION = "single-elimination"
    DOUBLE_ELIMINATION = "double-elimination"
    SWISS = "swiss"
    ROUND_ROBIN = "round-robin"

class QueueStatus(str, Enum):
    """Event queue status enum matching database"""
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    ERROR = "error"


Need to install the following packages:
supabase@2.34.3
Ok to proceed? (y) 
export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "12.2.12 (cd3cf9e)"
  }
  public: {
    Tables: {
      alembic_version: {
        Row: {
          version_num: string
        }
        Insert: {
          version_num: string
        }
        Update: {
          version_num?: string
        }
        Relationships: []
      }
      awards_race: {
        Row: {
          award_type: Database["public"]["Enums"]["award_types"] | null
          award_winner: boolean | null
          created_at: string
          id: string
          league_id: string | null
          player_id: string | null
          rank: number | null
          rp_bonus: number | null
          team_id: string
          tournament_id: string | null
        }
        Insert: {
          award_type?: Database["public"]["Enums"]["award_types"] | null
          award_winner?: boolean | null
          created_at?: string
          id?: string
          league_id?: string | null
          player_id?: string | null
          rank?: number | null
          rp_bonus?: number | null
          team_id: string
          tournament_id?: string | null
        }
        Update: {
          award_type?: Database["public"]["Enums"]["award_types"] | null
          award_winner?: boolean | null
          created_at?: string
          id?: string
          league_id?: string | null
          player_id?: string | null
          rank?: number | null
          rp_bonus?: number | null
          team_id?: string
          tournament_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "awards_race_league_id_fkey"
            columns: ["league_id"]
            isOneToOne: false
            referencedRelation: "leagues_info"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "awards_race_player_id_fkey"
            columns: ["player_id"]
            isOneToOne: false
            referencedRelation: "player_performance_view"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "awards_race_player_id_fkey"
            columns: ["player_id"]
            isOneToOne: false
            referencedRelation: "players"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "awards_race_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "awards_race_tournament_id_fkey"
            columns: ["tournament_id"]
            isOneToOne: false
            referencedRelation: "tournaments"
            referencedColumns: ["id"]
          },
        ]
      }
      draft_pool: {
        Row: {
          created_at: string | null
          declared_at: string | null
          draft_notes: string | null
          draft_rating: number | null
          league_id: string | null
          player_id: string
          season: string | null
          status: string | null
          tournament_id: string | null
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          declared_at?: string | null
          draft_notes?: string | null
          draft_rating?: number | null
          league_id?: string | null
          player_id: string
          season?: string | null
          status?: string | null
          tournament_id?: string | null
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          declared_at?: string | null
          draft_notes?: string | null
          draft_rating?: number | null
          league_id?: string | null
          player_id?: string
          season?: string | null
          status?: string | null
          tournament_id?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "draft_pool_league_id_fkey"
            columns: ["league_id"]
            isOneToOne: false
            referencedRelation: "leagues_info"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "draft_pool_player_id_fkey"
            columns: ["player_id"]
            isOneToOne: true
            referencedRelation: "player_performance_view"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "draft_pool_player_id_fkey"
            columns: ["player_id"]
            isOneToOne: true
            referencedRelation: "players"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "draft_pool_season_fkey"
            columns: ["season"]
            isOneToOne: false
            referencedRelation: "season_id"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "draft_pool_tournament_id_fkey"
            columns: ["tournament_id"]
            isOneToOne: false
            referencedRelation: "tournaments"
            referencedColumns: ["id"]
          },
        ]
      }
      tournament_groups_members: {
        Row: {
          created_at: string | null
          group_id: string
          id: string
          seed: number | null
          team_id: string
        }
        Insert: {
          created_at?: string | null
          group_id: string
          id?: string
          seed?: number | null
          team_id: string
        }
        Update: {
          created_at?: string | null
          group_id?: string
          id?: string
          seed?: number | null
          team_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "tournament_groups_members_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "tournament_groupss"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "tournament_groups_members_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      tournament_groupss: {
        Row: {
          advancement_count: number | null
          created_at: string | null
          description: string | null
          id: string
          league_season_id: string | null
          max_teams: number | null
          name: string
          sort_order: number | null
          status: string | null
          tournament_id: string | null
          updated_at: string | null
        }
        Insert: {
          advancement_count?: number | null
          created_at?: string | null
          description?: string | null
          id?: string
          league_season_id?: string | null
          max_teams?: number | null
          name: string
          sort_order?: number | null
          status?: string | null
          tournament_id?: string | null
          updated_at?: string | null
        }
        Update: {
          advancement_count?: number | null
          created_at?: string | null
          description?: string | null
          id?: string
          league_season_id?: string | null
          max_teams?: number | null
          name?: string
          sort_order?: number | null
          status?: string | null
          tournament_id?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "tournament_groupss_league_season_id_fkey"
            columns: ["league_season_id"]
            isOneToOne: false
            referencedRelation: "season_id"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "tournament_groupss_tournament_id_fkey"
            columns: ["tournament_id"]
            isOneToOne: false
            referencedRelation: "tournaments"
            referencedColumns: ["id"]
          },
        ]
      }
      event_results: {
        Row: {
          awarded_at: string | null
          bonus_rp: number | null
          id: string
          league_id: string | null
          placement: number | null
          prize_amount: number | null
          rp_awarded: number | null
          team_id: string
          total_rp: number | null
          tournament_id: string | null
          winner_banner_url: string | null
        }
        Insert: {
          awarded_at?: string | null
          bonus_rp?: number | null
          id?: string
          league_id?: string | null
          placement?: number | null
          prize_amount?: number | null
          rp_awarded?: number | null
          team_id: string
          total_rp?: number | null
          tournament_id?: string | null
          winner_banner_url?: string | null
        }
        Update: {
          awarded_at?: string | null
          bonus_rp?: number | null
          id?: string
          league_id?: string | null
          placement?: number | null
          prize_amount?: number | null
          rp_awarded?: number | null
          team_id?: string
          total_rp?: number | null
          tournament_id?: string | null
          winner_banner_url?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "event_results_league_id_fkey"
            columns: ["league_id"]
            isOneToOne: false
            referencedRelation: "leagues_info"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "event_results_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "event_results_tournament_id_fkey"
            columns: ["tournament_id"]
            isOneToOne: false
            referencedRelation: "tournaments"
            referencedColumns: ["id"]
          },
        ]
      }
      group_matches: {
        Row: {
          created_at: string | null
          group_id: string
          id: string
          match_id: string
          match_number: number
          round: number
        }
        Insert: {
          created_at?: string | null
          group_id: string
          id?: string
          match_id: string
          match_number: number
          round: number
        }
        Update: {
          created_at?: string | null
          group_id?: string
          id?: string
          match_id?: string
          match_number?: number
          round?: number
        }
        Relationships: [
          {
            foreignKeyName: "group_matches_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "tournament_groupss"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "group_matches_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "matches"
            referencedColumns: ["id"]
          },
        ]
      }
      group_standings: {
        Row: {
          group_id: string
          id: string
          losses: number | null
          matches_played: number | null
          point_differential: number | null
          points_against: number | null
          points_for: number | null
          position: number | null
          team_id: string
          updated_at: string | null
          wins: number | null
        }
        Insert: {
          group_id: string
          id?: string
          losses?: number | null
          matches_played?: number | null
          point_differential?: number | null
          points_against?: number | null
          points_for?: number | null
          position?: number | null
          team_id: string
          updated_at?: string | null
          wins?: number | null
        }
        Update: {
          group_id?: string
          id?: string
          losses?: number | null
          matches_played?: number | null
          point_differential?: number | null
          points_against?: number | null
          points_for?: number | null
          position?: number | null
          team_id?: string
          updated_at?: string | null
          wins?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "group_standings_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "tournament_groupss"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "group_standings_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      kv_store_10f5458b: {
        Row: {
          key: string
          value: Json
        }
        Insert: {
          key: string
          value: Json
        }
        Update: {
          key?: string
          value?: Json
        }
        Relationships: []
      }
      season_id: {
        Row: {
          created_at: string
          end_date: string
          id: string
          is_active: boolean | null
          league_id: string | null
          league_name: Database["public"]["Enums"]["leagues"]
          season_number: number
          start_date: string
          updated_at: string
          year: Database["public"]["Enums"]["game_year"] | null
        }
        Insert: {
          created_at?: string
          end_date: string
          id?: string
          is_active?: boolean | null
          league_id?: string | null
          league_name: Database["public"]["Enums"]["leagues"]
          season_number: number
          start_date: string
          updated_at?: string
          year?: Database["public"]["Enums"]["game_year"] | null
        }
        Update: {
          created_at?: string
          end_date?: string
          id?: string
          is_active?: boolean | null
          league_id?: string | null
          league_name?: Database["public"]["Enums"]["leagues"]
          season_number?: number
          start_date?: string
          updated_at?: string
          year?: Database["public"]["Enums"]["game_year"] | null
        }
        Relationships: [
          {
            foreignKeyName: "season_id_league_id_fkey"
            columns: ["league_id"]
            isOneToOne: false
            referencedRelation: "leagues_info"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "season_id_league_name_fkey"
            columns: ["league_name"]
            isOneToOne: true
            referencedRelation: "leagues_info"
            referencedColumns: ["league"]
          },
        ]
      }
      leagues_info: {
        Row: {
          created_at: string
          id: string
          league: Database["public"]["Enums"]["leagues"] | null
          lg_discord: string | null
          lg_logo_url: string | null
          lg_url: string | null
          sponsor_info: string | null
          twitch_url: string | null
          twitter_id: string | null
        }
        Insert: {
          created_at?: string
          id?: string
          league?: Database["public"]["Enums"]["leagues"] | null
          lg_discord?: string | null
          lg_logo_url?: string | null
          lg_url?: string | null
          sponsor_info?: string | null
          twitch_url?: string | null
          twitter_id?: string | null
        }
        Update: {
          created_at?: string
          id?: string
          league?: Database["public"]["Enums"]["leagues"] | null
          lg_discord?: string | null
          lg_logo_url?: string | null
          lg_url?: string | null
          sponsor_info?: string | null
          twitch_url?: string | null
          twitter_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "leagues_info_sponsor_info_fkey"
            columns: ["sponsor_info"]
            isOneToOne: false
            referencedRelation: "sponsor_info"
            referencedColumns: ["sponsor_name"]
          },
        ]
      }
      match_mvp: {
        Row: {
          match_id: string
          player_id: string
        }
        Insert: {
          match_id: string
          player_id: string
        }
        Update: {
          match_id?: string
          player_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "match_mvp_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: true
            referencedRelation: "matches"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "match_mvp_player_id_fkey"
            columns: ["player_id"]
            isOneToOne: false
            referencedRelation: "player_performance_view"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "match_mvp_player_id_fkey"
            columns: ["player_id"]
            isOneToOne: false
            referencedRelation: "players"
            referencedColumns: ["id"]
          },
        ]
      }
      match_points: {
        Row: {
          created_at: string | null
          group_id: string | null
          id: string
          match_id: string
          point_type: string
          points_earned: number
          team_id: string
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          group_id?: string | null
          id?: string
          match_id: string
          point_type: string
          points_earned: number
          team_id: string
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          group_id?: string | null
          id?: string
          match_id?: string
          point_type?: string
          points_earned?: number
          team_id?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "match_points_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "tournament_groupss"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "match_points_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "matches"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "match_points_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      match_submissions: {
        Row: {
          created_at: string
          id: string
          league_id: string | null
          match_id: string | null
          payload: Json | null
          review_notes: string | null
          review_status: string | null
          reviewed_at: string | null
          reviewed_by: string | null
          status: string | null
          team_a_id: string | null
          team_a_name: string | null
          team_b_id: string | null
          team_b_name: string | null
          tournament_id: string | null
        }
        Insert: {
          created_at?: string
          id?: string
          league_id?: string | null
          match_id?: string | null
          payload?: Json | null
          review_notes?: string | null
          review_status?: string | null
          reviewed_at?: string | null
          reviewed_by?: string | null
          status?: string | null
          team_a_id?: string | null
          team_a_name?: string | null
          team_b_id?: string | null
          team_b_name?: string | null
          tournament_id?: string | null
        }
        Update: {
          created_at?: string
          id?: string
          league_id?: string | null
          match_id?: string | null
          payload?: Json | null
          review_notes?: string | null
          review_status?: string | null
          reviewed_at?: string | null
          reviewed_by?: string | null
          status?: string | null
          team_a_id?: string | null
          team_a_name?: string | null
          team_b_id?: string | null
          team_b_name?: string | null
          tournament_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "match_submissions_league_id_fkey"
            columns: ["league_id"]
            isOneToOne: false
            referencedRelation: "leagues_info"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "match_submissions_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "matches"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "match_submissions_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "match_submissions_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "player_performance_view"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "match_submissions_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "team_roster_current"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "match_submissions_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["name"]
          },
          {
            foreignKeyName: "match_submissions_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "match_submissions_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "player_performance_view"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "match_submissions_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "team_roster_current"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "match_submissions_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["name"]
          },
          {
            foreignKeyName: "match_submissions_tournament_id_fkey"
            columns: ["tournament_id"]
            isOneToOne: false
            referencedRelation: "tournaments"
            referencedColumns: ["id"]
          },
        ]
      }
      matches: {
        Row: {
          boxscore_url: string | null
          game_number: number | null
          id: string
          league_id: string | null
          league_season: string | null
          played_at: string | null
          score_a: number | null
          score_b: number | null
          stage: Database["public"]["Enums"]["stage"] | null
          team_a_id: string | null
          team_a_name: string | null
          team_b_id: string | null
          tournament_id: string | null
          winner_id: string | null
        }
        Insert: {
          boxscore_url?: string | null
          game_number?: number | null
          id?: string
          league_id?: string | null
          league_season?: string | null
          played_at?: string | null
          score_a?: number | null
          score_b?: number | null
          stage?: Database["public"]["Enums"]["stage"] | null
          team_a_id?: string | null
          team_a_name?: string | null
          team_b_id?: string | null
          tournament_id?: string | null
          winner_id?: string | null
        }
        Update: {
          boxscore_url?: string | null
          game_number?: number | null
          id?: string
          league_id?: string | null
          league_season?: string | null
          played_at?: string | null
          score_a?: number | null
          score_b?: number | null
          stage?: Database["public"]["Enums"]["stage"] | null
          team_a_id?: string | null
          team_a_name?: string | null
          team_b_id?: string | null
          tournament_id?: string | null
          winner_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "matches_league_id_fkey"
            columns: ["league_id"]
            isOneToOne: false
            referencedRelation: "leagues_info"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_league_season_fkey"
            columns: ["league_season"]
            isOneToOne: false
            referencedRelation: "season_id"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "player_performance_view"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "team_roster_current"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["name"]
          },
          {
            foreignKeyName: "matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_tournament_id_fkey"
            columns: ["tournament_id"]
            isOneToOne: false
            referencedRelation: "tournaments"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_winner_id_fkey"
            columns: ["winner_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      notifications: {
        Row: {
          created_at: string
          id: string
          message: string
          read: boolean
          title: string
          type: string
          updated_at: string
          user_id: string | null
        }
        Insert: {
          created_at?: string
          id?: string
          message: string
          read?: boolean
          title: string
          type?: string
          updated_at?: string
          user_id?: string | null
        }
        Update: {
          created_at?: string
          id?: string
          message?: string
          read?: boolean
          title?: string
          type?: string
          updated_at?: string
          user_id?: string | null
        }
        Relationships: []
      }
      past_champions: {
        Row: {
          champion_logo: string | null
          console: Database["public"]["Enums"]["console"] | null
          created_at: string
          event_tier: Database["public"]["Enums"]["event_tier"] | null
          id: string
          is_tournament: boolean
          league_id: string | null
          league_name: Database["public"]["Enums"]["leagues"] | null
          lg_logo: string | null
          season: number | null
          team_id: string | null
          team_name: string | null
          tournament_date: string | null
          tournament_id: string | null
          year: Database["public"]["Enums"]["game_year"] | null
        }
        Insert: {
          champion_logo?: string | null
          console?: Database["public"]["Enums"]["console"] | null
          created_at?: string
          event_tier?: Database["public"]["Enums"]["event_tier"] | null
          id?: string
          is_tournament?: boolean
          league_id?: string | null
          league_name?: Database["public"]["Enums"]["leagues"] | null
          lg_logo?: string | null
          season?: number | null
          team_id?: string | null
          team_name?: string | null
          tournament_date?: string | null
          tournament_id?: string | null
          year?: Database["public"]["Enums"]["game_year"] | null
        }
        Update: {
          champion_logo?: string | null
          console?: Database["public"]["Enums"]["console"] | null
          created_at?: string
          event_tier?: Database["public"]["Enums"]["event_tier"] | null
          id?: string
          is_tournament?: boolean
          league_id?: string | null
          league_name?: Database["public"]["Enums"]["leagues"] | null
          lg_logo?: string | null
          season?: number | null
          team_id?: string | null
          team_name?: string | null
          tournament_date?: string | null
          tournament_id?: string | null
          year?: Database["public"]["Enums"]["game_year"] | null
        }
        Relationships: [
          {
            foreignKeyName: "past_champions_champion_logo_fkey"
            columns: ["champion_logo"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["logo_url"]
          },
          {
            foreignKeyName: "past_champions_league_id_fkey"
            columns: ["league_id"]
            isOneToOne: false
            referencedRelation: "leagues_info"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "past_champions_lg_logo_fkey"
            columns: ["lg_logo"]
            isOneToOne: false
            referencedRelation: "leagues_info"
            referencedColumns: ["lg_logo_url"]
          },
          {
            foreignKeyName: "past_champions_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "past_champions_team_name_fkey"
            columns: ["team_name"]
            isOneToOne: false
            referencedRelation: "player_performance_view"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "past_champions_team_name_fkey"
            columns: ["team_name"]
            isOneToOne: false
            referencedRelation: "team_roster_current"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "past_champions_team_name_fkey"
            columns: ["team_name"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["name"]
          },
          {
            foreignKeyName: "past_champions_tournament_id_fkey"
            columns: ["tournament_id"]
            isOneToOne: false
            referencedRelation: "tournaments"
            referencedColumns: ["id"]
          },
        ]
      }
      player_badges: {
        Row: {
          badge_type: string
          created_at: string
          id: string
          ipfs_uri: string | null
          league_id: string | null
          match_id: number
          player_wallet: string
          token_id: number | null
          tournament_id: string | null
          tx_hash: string | null
        }
        Insert: {
          badge_type: string
          created_at?: string
          id?: string
          ipfs_uri?: string | null
          league_id?: string | null
          match_id: number
          player_wallet: string
          token_id?: number | null
          tournament_id?: string | null
          tx_hash?: string | null
        }
        Update: {
          badge_type?: string
          created_at?: string
          id?: string
          ipfs_uri?: string | null
          league_id?: string | null
          match_id?: number
          player_wallet?: string
          token_id?: number | null
          tournament_id?: string | null
          tx_hash?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "player_badges_league_id_fkey"
            columns: ["league_id"]
            isOneToOne: false
            referencedRelation: "leagues_info"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "player_badges_tournament_id_fkey"
            columns: ["tournament_id"]
            isOneToOne: false
            referencedRelation: "tournaments"
            referencedColumns: ["id"]
          },
        ]
      }
      player_rp_transactions: {
        Row: {
          amount: number
          created_at: string
          description: string
          id: string
          league_id: string | null
          match_id: string | null
          player_id: string | null
          tournament_id: string | null
          type: string
          updated_at: string
        }
        Insert: {
          amount: number
          created_at?: string
          description: string
          id?: string
          league_id?: string | null
          match_id?: string | null
          player_id?: string | null
          tournament_id?: string | null
          type: string
          updated_at?: string
        }
        Update: {
          amount?: number
          created_at?: string
          description?: string
          id?: string
          league_id?: string | null
          match_id?: string | null
          player_id?: string | null
          tournament_id?: string | null
          type?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "player_rp_transactions_league_id_fkey"
            columns: ["league_id"]
            isOneToOne: false
            referencedRelation: "leagues_info"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "player_rp_transactions_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "matches"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "player_rp_transactions_player_id_fkey"
            columns: ["player_id"]
            isOneToOne: false
            referencedRelation: "player_performance_view"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "player_rp_transactions_player_id_fkey"
            columns: ["player_id"]
            isOneToOne: false
            referencedRelation: "players"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "player_rp_transactions_tournament_id_fkey"
            columns: ["tournament_id"]
            isOneToOne: false
            referencedRelation: "tournaments"
            referencedColumns: ["id"]
          },
        ]
      }
      player_salary_tiers: {
        Row: {
          id: number
          max_value: number | null
          min_value: number | null
          multiplier: number
          tier_name: string
        }
        Insert: {
          id?: number
          max_value?: number | null
          min_value?: number | null
          multiplier: number
          tier_name: string
        }
        Update: {
          id?: number
          max_value?: number | null
          min_value?: number | null
          multiplier?: number
          tier_name?: string
        }
        Relationships: []
      }
      player_stats: {
        Row: {
          assists: number | null
          blocks: number | null
          created_at: string | null
          fga: number | null
          fgm: number | null
          fouls: number | null
          fta: number | null
          ftm: number | null
          id: string
          match_id: string
          player_id: string
          player_name: string | null
          plus_minus: number | null
          points: number | null
          ps: number | null
          rebounds: number | null
          steals: number | null
          team_id: string
          three_points_attempted: number | null
          three_points_made: number | null
          turnovers: number | null
          updated_at: string | null
        }
        Insert: {
          assists?: number | null
          blocks?: number | null
          created_at?: string | null
          fga?: number | null
          fgm?: number | null
          fouls?: number | null
          fta?: number | null
          ftm?: number | null
          id?: string
          match_id: string
          player_id: string
          player_name?: string | null
          plus_minus?: number | null
          points?: number | null
          ps?: number | null
          rebounds?: number | null
          steals?: number | null
          team_id: string
          three_points_attempted?: number | null
          three_points_made?: number | null
          turnovers?: number | null
          updated_at?: string | null
        }
        Update: {
          assists?: number | null
          blocks?: number | null
          created_at?: string | null
          fga?: number | null
          fgm?: number | null
          fouls?: number | null
          fta?: number | null
          ftm?: number | null
          id?: string
          match_id?: string
          player_id?: string
          player_name?: string | null
          plus_minus?: number | null
          points?: number | null
          ps?: number | null
          rebounds?: number | null
          steals?: number | null
          team_id?: string
          three_points_attempted?: number | null
          three_points_made?: number | null
          turnovers?: number | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "player_stats_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "matches"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "player_stats_player_id_fkey"
            columns: ["player_id"]
            isOneToOne: false
            referencedRelation: "player_performance_view"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "player_stats_player_id_fkey"
            columns: ["player_id"]
            isOneToOne: false
            referencedRelation: "players"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "player_stats_player_name_fkey"
            columns: ["player_name"]
            isOneToOne: false
            referencedRelation: "player_performance_view"
            referencedColumns: ["gamertag"]
          },
          {
            foreignKeyName: "player_stats_player_name_fkey"
            columns: ["player_name"]
            isOneToOne: false
            referencedRelation: "players"
            referencedColumns: ["gamertag"]
          },
          {
            foreignKeyName: "player_stats_player_name_fkey"
            columns: ["player_name"]
            isOneToOne: false
            referencedRelation: "team_roster_current"
            referencedColumns: ["gamertag"]
          },
          {
            foreignKeyName: "player_stats_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      players: {
        Row: {
          alternate_gamertag: string | null
          created_at: string | null
          current_team_id: string | null
          discord_id: string | null
          gamertag: string
          id: string
          is_rookie: boolean | null
          monthly_value: number | null
          performance_score: number | null
          player_rank_score: number | null
          player_rp: number | null
          position: Database["public"]["Enums"]["player_position"] | null
          salary_tier: Database["public"]["Enums"]["salary_tier"] | null
          twitter_id: string | null
        }
        Insert: {
          alternate_gamertag?: string | null
          created_at?: string | null
          current_team_id?: string | null
          discord_id?: string | null
          gamertag: string
          id?: string
          is_rookie?: boolean | null
          monthly_value?: number | null
          performance_score?: number | null
          player_rank_score?: number | null
          player_rp?: number | null
          position?: Database["public"]["Enums"]["player_position"] | null
          salary_tier?: Database["public"]["Enums"]["salary_tier"] | null
          twitter_id?: string | null
        }
        Update: {
          alternate_gamertag?: string | null
          created_at?: string | null
          current_team_id?: string | null
          discord_id?: string | null
          gamertag?: string
          id?: string
          is_rookie?: boolean | null
          monthly_value?: number | null
          performance_score?: number | null
          player_rank_score?: number | null
          player_rp?: number | null
          position?: Database["public"]["Enums"]["player_position"] | null
          salary_tier?: Database["public"]["Enums"]["salary_tier"] | null
          twitter_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "players_current_team_id_fkey"
            columns: ["current_team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      profiles: {
        Row: {
          app_role: Database["public"]["Enums"]["app_role"] | null
          created_at: string | null
          email: string | null
          id: string
          role: string
          updated_at: string | null
        }
        Insert: {
          app_role?: Database["public"]["Enums"]["app_role"] | null
          created_at?: string | null
          email?: string | null
          id: string
          role?: string
          updated_at?: string | null
        }
        Update: {
          app_role?: Database["public"]["Enums"]["app_role"] | null
          created_at?: string | null
          email?: string | null
          id?: string
          role?: string
          updated_at?: string | null
        }
        Relationships: []
      }
      ranking_points: {
        Row: {
          awarded_at: string | null
          expires_at: string | null
          id: string
          league_id: string | null
          points: number | null
          source: string | null
          team_id: string | null
          tournament_id: string | null
        }
        Insert: {
          awarded_at?: string | null
          expires_at?: string | null
          id?: string
          league_id?: string | null
          points?: number | null
          source?: string | null
          team_id?: string | null
          tournament_id?: string | null
        }
        Update: {
          awarded_at?: string | null
          expires_at?: string | null
          id?: string
          league_id?: string | null
          points?: number | null
          source?: string | null
          team_id?: string | null
          tournament_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "ranking_points_league_id_fkey"
            columns: ["league_id"]
            isOneToOne: false
            referencedRelation: "leagues_info"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "ranking_points_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "ranking_points_tournament_id_fkey"
            columns: ["tournament_id"]
            isOneToOne: false
            referencedRelation: "tournaments"
            referencedColumns: ["id"]
          },
        ]
      }
      regions: {
        Row: {
          id: string
          name: string
        }
        Insert: {
          id?: string
          name: string
        }
        Update: {
          id?: string
          name?: string
        }
        Relationships: []
      }
      role_permissions: {
        Row: {
          id: number
          permission: string
          role: Database["public"]["Enums"]["app_role"] | null
        }
        Insert: {
          id?: never
          permission: string
          role?: Database["public"]["Enums"]["app_role"] | null
        }
        Update: {
          id?: never
          permission?: string
          role?: Database["public"]["Enums"]["app_role"] | null
        }
        Relationships: []
      }
      rp_transactions: {
        Row: {
          amount: number
          created_at: string
          description: string | null
          id: string
          league_id: string | null
          team_id: string | null
          tournament_id: string | null
          type: string
          updated_at: string
        }
        Insert: {
          amount: number
          created_at?: string
          description?: string | null
          id?: string
          league_id?: string | null
          team_id?: string | null
          tournament_id?: string | null
          type: string
          updated_at?: string
        }
        Update: {
          amount?: number
          created_at?: string
          description?: string | null
          id?: string
          league_id?: string | null
          team_id?: string | null
          tournament_id?: string | null
          type?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "rp_transactions_league_id_fkey"
            columns: ["league_id"]
            isOneToOne: false
            referencedRelation: "leagues_info"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "rp_transactions_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "rp_transactions_tournament_id_fkey"
            columns: ["tournament_id"]
            isOneToOne: false
            referencedRelation: "tournaments"
            referencedColumns: ["id"]
          },
        ]
      }
      salary_tiers: {
        Row: {
          description: string | null
          id: number
          label: string | null
          max_rating: number | null
          min_rating: number | null
          multiplier: number
          salary_tier: Database["public"]["Enums"]["salary_tier"]
        }
        Insert: {
          description?: string | null
          id?: never
          label?: string | null
          max_rating?: number | null
          min_rating?: number | null
          multiplier: number
          salary_tier: Database["public"]["Enums"]["salary_tier"]
        }
        Update: {
          description?: string | null
          id?: never
          label?: string | null
          max_rating?: number | null
          min_rating?: number | null
          multiplier?: number
          salary_tier?: Database["public"]["Enums"]["salary_tier"]
        }
        Relationships: []
      }
      sponsor_info: {
        Row: {
          created_at: string
          id: string
          sponsor_logo: string | null
          sponsor_name: string | null
          sponsor_url: string | null
        }
        Insert: {
          created_at?: string
          id?: string
          sponsor_logo?: string | null
          sponsor_name?: string | null
          sponsor_url?: string | null
        }
        Update: {
          created_at?: string
          id?: string
          sponsor_logo?: string | null
          sponsor_name?: string | null
          sponsor_url?: string | null
        }
        Relationships: []
      }
      team_match_stats: {
        Row: {
          assists: number
          blocks: number
          field_goals_attempted: number
          field_goals_made: number
          fouls: number | null
          free_throws_attempted: number
          free_throws_made: number
          id: string
          match_id: string
          plus_minus: number | null
          points: number
          rebounds: number
          steals: number
          team_id: string
          three_points_attempted: number
          three_points_made: number
          turnovers: number
        }
        Insert: {
          assists: number
          blocks: number
          field_goals_attempted: number
          field_goals_made: number
          fouls?: number | null
          free_throws_attempted: number
          free_throws_made: number
          id?: string
          match_id: string
          plus_minus?: number | null
          points: number
          rebounds: number
          steals: number
          team_id: string
          three_points_attempted: number
          three_points_made: number
          turnovers: number
        }
        Update: {
          assists?: number
          blocks?: number
          field_goals_attempted?: number
          field_goals_made?: number
          fouls?: number | null
          free_throws_attempted?: number
          free_throws_made?: number
          id?: string
          match_id?: string
          plus_minus?: number | null
          points?: number
          rebounds?: number
          steals?: number
          team_id?: string
          three_points_attempted?: number
          three_points_made?: number
          turnovers?: number
        }
        Relationships: [
          {
            foreignKeyName: "team_match_stats_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "matches"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "team_match_stats_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      team_rosters: {
        Row: {
          id: string
          is_captain: boolean | null
          is_player_coach: boolean | null
          joined_at: string | null
          league_id: string | null
          left_at: string | null
          player_id: string | null
          team_id: string | null
          tournament_id: string | null
        }
        Insert: {
          id?: string
          is_captain?: boolean | null
          is_player_coach?: boolean | null
          joined_at?: string | null
          league_id?: string | null
          left_at?: string | null
          player_id?: string | null
          team_id?: string | null
          tournament_id?: string | null
        }
        Update: {
          id?: string
          is_captain?: boolean | null
          is_player_coach?: boolean | null
          joined_at?: string | null
          league_id?: string | null
          left_at?: string | null
          player_id?: string | null
          team_id?: string | null
          tournament_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "team_rosters_league_id_fkey"
            columns: ["league_id"]
            isOneToOne: false
            referencedRelation: "leagues_info"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "team_rosters_player_id_fkey"
            columns: ["player_id"]
            isOneToOne: false
            referencedRelation: "player_performance_view"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "team_rosters_player_id_fkey"
            columns: ["player_id"]
            isOneToOne: false
            referencedRelation: "players"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "team_rosters_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "team_rosters_tournament_id_fkey"
            columns: ["tournament_id"]
            isOneToOne: false
            referencedRelation: "tournaments"
            referencedColumns: ["id"]
          },
        ]
      }
      teams: {
        Row: {
          created_at: string | null
          current_rp: number | null
          elo_rating: number | null
          global_rank: number | null
          id: string
          leaderboard_tier: string | null
          logo_url: string | null
          money_won: number | null
          name: string
          player_rank_score: number | null
        }
        Insert: {
          created_at?: string | null
          current_rp?: number | null
          elo_rating?: number | null
          global_rank?: number | null
          id?: string
          leaderboard_tier?: string | null
          logo_url?: string | null
          money_won?: number | null
          name: string
          player_rank_score?: number | null
        }
        Update: {
          created_at?: string | null
          current_rp?: number | null
          elo_rating?: number | null
          global_rank?: number | null
          id?: string
          leaderboard_tier?: string | null
          logo_url?: string | null
          money_won?: number | null
          name?: string
          player_rank_score?: number | null
        }
        Relationships: []
      }
      teams_pot_tracker: {
        Row: {
          created_at: string
          id: string
          league_id: string | null
          placement: number | null
          prize_amount: number | null
          team_id: string | null
          tournament_id: string | null
        }
        Insert: {
          created_at?: string
          id?: string
          league_id?: string | null
          placement?: number | null
          prize_amount?: number | null
          team_id?: string | null
          tournament_id?: string | null
        }
        Update: {
          created_at?: string
          id?: string
          league_id?: string | null
          placement?: number | null
          prize_amount?: number | null
          team_id?: string | null
          tournament_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "teams_pot_tracker_league_id_fkey"
            columns: ["league_id"]
            isOneToOne: false
            referencedRelation: "leagues_info"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "teams_pot_tracker_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "teams_pot_tracker_tournament_id_fkey"
            columns: ["tournament_id"]
            isOneToOne: false
            referencedRelation: "tournaments"
            referencedColumns: ["id"]
          },
        ]
      }
      tournaments: {
        Row: {
          banner_url: string | null
          champion: string | null
          console: Database["public"]["Enums"]["console"] | null
          created_at: string
          decay_days: number | null
          description: string | null
          end_date: string | null
          game_year: Database["public"]["Enums"]["game_year"] | null
          id: string
          max_rp: number | null
          name: string | null
          organizer_id: string | null
          organizer_logo_url: string | null
          place: string | null
          prize_pool: number | null
          processed_at: string | null
          rules_url: string | null
          runner_up: string | null
          sponsor: string | null
          sponsor_logo: string | null
          start_date: string | null
          status: Database["public"]["Enums"]["status"] | null
          tier: Database["public"]["Enums"]["event_tier"] | null
        }
        Insert: {
          banner_url?: string | null
          champion?: string | null
          console?: Database["public"]["Enums"]["console"] | null
          created_at?: string
          decay_days?: number | null
          description?: string | null
          end_date?: string | null
          game_year?: Database["public"]["Enums"]["game_year"] | null
          id?: string
          max_rp?: number | null
          name?: string | null
          organizer_id?: string | null
          organizer_logo_url?: string | null
          place?: string | null
          prize_pool?: number | null
          processed_at?: string | null
          rules_url?: string | null
          runner_up?: string | null
          sponsor?: string | null
          sponsor_logo?: string | null
          start_date?: string | null
          status?: Database["public"]["Enums"]["status"] | null
          tier?: Database["public"]["Enums"]["event_tier"] | null
        }
        Update: {
          banner_url?: string | null
          champion?: string | null
          console?: Database["public"]["Enums"]["console"] | null
          created_at?: string
          decay_days?: number | null
          description?: string | null
          end_date?: string | null
          game_year?: Database["public"]["Enums"]["game_year"] | null
          id?: string
          max_rp?: number | null
          name?: string | null
          organizer_id?: string | null
          organizer_logo_url?: string | null
          place?: string | null
          prize_pool?: number | null
          processed_at?: string | null
          rules_url?: string | null
          runner_up?: string | null
          sponsor?: string | null
          sponsor_logo?: string | null
          start_date?: string | null
          status?: Database["public"]["Enums"]["status"] | null
          tier?: Database["public"]["Enums"]["event_tier"] | null
        }
        Relationships: [
          {
            foreignKeyName: "tournaments_champion_fkey"
            columns: ["champion"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "tournaments_organizer_id_fkey"
            columns: ["organizer_id"]
            isOneToOne: false
            referencedRelation: "leagues_info"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "tournaments_organizer_logo_url_fkey"
            columns: ["organizer_logo_url"]
            isOneToOne: false
            referencedRelation: "leagues_info"
            referencedColumns: ["lg_logo_url"]
          },
          {
            foreignKeyName: "tournaments_place_fkey"
            columns: ["place"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "tournaments_runner_up_fkey"
            columns: ["runner_up"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "tournaments_sponsor_fkey"
            columns: ["sponsor"]
            isOneToOne: false
            referencedRelation: "sponsor_info"
            referencedColumns: ["sponsor_name"]
          },
          {
            foreignKeyName: "tournaments_sponsor_logo_fkey"
            columns: ["sponsor_logo"]
            isOneToOne: false
            referencedRelation: "sponsor_info"
            referencedColumns: ["sponsor_logo"]
          },
        ]
      }
      upcoming_matches: {
        Row: {
          created_at: string | null
          group_id: string | null
          id: string
          league_id: string | null
          match_number: number | null
          notes: string | null
          round: number | null
          scheduled_at: string
          status: string | null
          stream_url: string | null
          team_a_id: string | null
          team_b_id: string | null
          tournament_id: string | null
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          group_id?: string | null
          id?: string
          league_id?: string | null
          match_number?: number | null
          notes?: string | null
          round?: number | null
          scheduled_at: string
          status?: string | null
          stream_url?: string | null
          team_a_id?: string | null
          team_b_id?: string | null
          tournament_id?: string | null
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          group_id?: string | null
          id?: string
          league_id?: string | null
          match_number?: number | null
          notes?: string | null
          round?: number | null
          scheduled_at?: string
          status?: string | null
          stream_url?: string | null
          team_a_id?: string | null
          team_b_id?: string | null
          tournament_id?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "upcoming_matches_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "tournament_groupss"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "upcoming_matches_league_id_fkey"
            columns: ["league_id"]
            isOneToOne: false
            referencedRelation: "leagues_info"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "upcoming_matches_tournament_id_fkey"
            columns: ["tournament_id"]
            isOneToOne: false
            referencedRelation: "tournaments"
            referencedColumns: ["id"]
          },
        ]
      }
      update_race: {
        Row: {
          id: number
          new_rank: number | null
          previous_rank: number | null
          race_id: string | null
          update_details: Json | null
          update_type: string
          updated_at: string
          updated_by: string | null
        }
        Insert: {
          id?: never
          new_rank?: number | null
          previous_rank?: number | null
          race_id?: string | null
          update_details?: Json | null
          update_type: string
          updated_at?: string
          updated_by?: string | null
        }
        Update: {
          id?: never
          new_rank?: number | null
          previous_rank?: number | null
          race_id?: string | null
          update_details?: Json | null
          update_type?: string
          updated_at?: string
          updated_by?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "update_race_race_id_fkey"
            columns: ["race_id"]
            isOneToOne: false
            referencedRelation: "awards_race"
            referencedColumns: ["id"]
          },
        ]
      }
      user_roles: {
        Row: {
          created_at: string
          id: number
          role: Database["public"]["Enums"]["app_role"] | null
          role_name: string | null
          user_id: string
        }
        Insert: {
          created_at?: string
          id?: never
          role?: Database["public"]["Enums"]["app_role"] | null
          role_name?: string | null
          user_id: string
        }
        Update: {
          created_at?: string
          id?: never
          role?: Database["public"]["Enums"]["app_role"] | null
          role_name?: string | null
          user_id?: string
        }
        Relationships: []
      }
    }
    Views: {
      player_performance_view: {
        Row: {
          avg_assists: number | null
          avg_blocks: number | null
          avg_performance_score: number | null
          avg_points: number | null
          avg_rebounds: number | null
          avg_steals: number | null
          current_team_id: string | null
          gamertag: string | null
          games_played: number | null
          id: string | null
          monthly_value: number | null
          player_rank_score: number | null
          player_rp: number | null
          position: Database["public"]["Enums"]["player_position"] | null
          salary_tier: Database["public"]["Enums"]["salary_tier"] | null
          team_name: string | null
        }
        Relationships: [
          {
            foreignKeyName: "players_current_team_id_fkey"
            columns: ["current_team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      team_roster_current: {
        Row: {
          gamertag: string | null
          is_captain: boolean | null
          is_player_coach: boolean | null
          joined_at: string | null
          monthly_value: number | null
          player_id: string | null
          position: Database["public"]["Enums"]["player_position"] | null
          salary_tier: Database["public"]["Enums"]["salary_tier"] | null
          team_id: string | null
          team_name: string | null
        }
        Relationships: [
          {
            foreignKeyName: "team_rosters_player_id_fkey"
            columns: ["player_id"]
            isOneToOne: false
            referencedRelation: "player_performance_view"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "team_rosters_player_id_fkey"
            columns: ["player_id"]
            isOneToOne: false
            referencedRelation: "players"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "team_rosters_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Functions: {
      add_event_placement_bonus_rp_to_players: {
        Args: {
          p_bonus_amount: number
          p_description?: string
          p_event_id: string
          p_team_id: string
        }
        Returns: {
          bonus_rp: number
          new_total_rp: number
          player_name: string
        }[]
      }
      add_mvp_bonus_rp: {
        Args: {
          p_description?: string
          p_event_id: string
          p_mvp_bonus?: number
        }
        Returns: {
          bonus_rp: number
          new_total_rp: number
          player_name: string
        }[]
      }
      add_player_to_team_roster: {
        Args: {
          in_event_id: string
          in_joined_at?: string
          in_player_id: string
          in_remove_from_draft_pool?: boolean
          in_team_id: string
        }
        Returns: undefined
      }
      adjust_team_rp: {
        Args: {
          amount: number
          event_id_param?: string
          reason: string
          team_id_param: string
        }
        Returns: undefined
      }
      analyze_elo_distribution: {
        Args: Record<PropertyKey, never>
        Returns: {
          elo_range: string
          percentage: number
          team_count: number
        }[]
      }
      apply_rp_decay: {
        Args: Record<PropertyKey, never>
        Returns: undefined
      }
      assign_placement_bonus_rp_to_players: {
        Args: {
          p_event_id: string
          p_first_place_bonus?: number
          p_second_place_bonus?: number
          p_third_place_bonus?: number
          p_top8_bonus?: number
        }
        Returns: {
          bonus_rp: number
          new_total_rp: number
          placement: number
          player_name: string
          team_name: string
        }[]
      }
      assign_role: {
        Args: { role_to_assign: string; target_user_id: string }
        Returns: boolean
      }
      assign_role_to_user: {
        Args: {
          p_role: Database["public"]["Enums"]["app_role"]
          p_user_id: string
        }
        Returns: boolean
      }
      calculate_all_player_salaries: {
        Args: Record<PropertyKey, never>
        Returns: {
          monthly_value: number
          player_name: string
          player_uuid: string
          raw_score: number
          tier_name: string
        }[]
      }
      calculate_defensive_mvp_score: {
        Args: { event_uuid: string; player_uuid: string }
        Returns: number
      }
      calculate_hybrid_score: {
        Args: { team_id_param: string }
        Returns: number
      }
      calculate_normalized_elo: {
        Args: { team_id_param: string }
        Returns: number
      }
      calculate_normalized_rp: {
        Args: { team_id_param: string }
        Returns: number
      }
      calculate_offensive_mvp_score: {
        Args: { event_uuid: string; player_uuid: string }
        Returns: number
      }
      calculate_player_salary: {
        Args: { player_uuid: string }
        Returns: {
          monthly_value: number
          player_name: string
          raw_score: number
          tier_name: string
        }[]
      }
      calculate_rookie_score: {
        Args: { event_uuid: string; player_uuid: string }
        Returns: number
      }
      calculate_team_standings: {
        Args: { event_id_param: string }
        Returns: {
          losses: number
          matches_played: number
          point_differential: number
          points_against: number
          points_for: number
          team_id: string
          team_name: string
          wins: number
        }[]
      }
      calculate_team_total_money_won: {
        Args: { team_uuid: string }
        Returns: number
      }
      complete_upcoming_match: {
        Args: {
          p_score_a: number
          p_score_b: number
          p_upcoming_match_id: string
          p_winner_id?: string
        }
        Returns: string
      }
      custom_jwt: {
        Args: Record<PropertyKey, never>
        Returns: Json
      }
      generate_award_nominees: {
        Args: { award_type_param: string; event_uuid: string; top_n?: number }
        Returns: {
          player_id: string
          player_name: string
          rank: number
          score: number
          team_id: string
          team_name: string
        }[]
      }
      generate_bracket_matches: {
        Args: {
          p_bracket_start_time: string
          p_event_id: string
          p_match_duration_minutes?: number
        }
        Returns: undefined
      }
      generate_bracket_seeding: {
        Args: { p_event_id: string }
        Returns: {
          group_position: number
          original_group_id: string
          original_group_name: string
          seed_position: number
          team_id: string
          team_name: string
        }[]
      }
      generate_group_matches: {
        Args: { p_group_id: string }
        Returns: undefined
      }
      get_elo_bounds: {
        Args: Record<PropertyKey, never>
        Returns: {
          max_bound: number
          min_bound: number
          normalized_starting: number
          starting_elo: number
        }[]
      }
      get_my_permissions: {
        Args: Record<PropertyKey, never>
        Returns: {
          permission: string
        }[]
      }
      get_user_roles: {
        Args: { user_id_param?: string }
        Returns: {
          role: string
        }[]
      }
      has_permission: {
        Args: { required_permission: string }
        Returns: boolean
      }
      has_role: {
        Args: { required_role: string }
        Returns: boolean
      }
      initialize_new_season: {
        Args: { season_name: string }
        Returns: undefined
      }
      initialize_user_roles: {
        Args: Record<PropertyKey, never>
        Returns: undefined
      }
      is_league_admin: {
        Args: Record<PropertyKey, never>
        Returns: boolean
      }
      promote_to_league_admin: {
        Args: { target_user_id: string }
        Returns: boolean
      }
      recalculate_all_rankings: {
        Args: Record<PropertyKey, never>
        Returns: undefined
      }
      recent_games_for_player: {
        Args: { player_id_param: string }
        Returns: {
          assists: number
          blocks: number
          fg_pct: number
          fga: number
          fgm: number
          ft_pct: number
          fta: number
          ftm: number
          location: string
          match_id: string
          opponent_logo: string
          opponent_name: string
          opponent_team_id: string
          pf: number
          played_at: string
          points: number
          rebounds: number
          result: string
          score_a: number
          score_b: number
          steals: number
          three_points_attempted: number
          three_points_made: number
          three_pt_pct: number
          turnovers: number
        }[]
      }
      record_match_forfeit: {
        Args: { p_forfeiting_team_id: string; p_match_id: string }
        Returns: undefined
      }
      remove_role: {
        Args: { role_to_remove: string; target_user_id: string }
        Returns: boolean
      }
      remove_role_from_user: {
        Args: {
          p_role: Database["public"]["Enums"]["app_role"]
          p_user_id: string
        }
        Returns: boolean
      }
      schedule_rp_decay: {
        Args: Record<PropertyKey, never>
        Returns: undefined
      }
      select_award_winner: {
        Args: {
          award_type_param: string
          event_uuid: string
          winner_player_id: string
        }
        Returns: undefined
      }
      sync_user_roles_for_user: {
        Args: { p_user_id: string }
        Returns: undefined
      }
      update_all_teams_money_won: {
        Args: Record<PropertyKey, never>
        Returns: undefined
      }
      update_awards_race: {
        Args: { award_type_param: string; event_uuid: string; top_n?: number }
        Returns: undefined
      }
      update_elo_after_match: {
        Args: {
          k_factor?: number
          loser_id_param: string
          winner_id_param: string
        }
        Returns: undefined
      }
      update_event_players_rp: {
        Args:
          | {
              bonus_amount?: number
              description_param?: string
              event_id_param: string
              performance_score_param?: number
              rating_param?: number
            }
          | {
              bonus_rp: number
              description_param: string
              event_id_param: string
            }
        Returns: {
          amount: number
          player_id: string
          player_name: string
          transaction_id: string
        }[]
      }
      update_event_players_rp_hybrid: {
        Args: {
          base_rp?: number
          bonus_amount?: number
          description_param?: string
          event_id_param: string
        }
        Returns: {
          amount: number
          hybrid_score: number
          player_id: string
          player_name: string
          transaction_id: string
        }[]
      }
      update_existing_draft_pool_records: {
        Args: Record<PropertyKey, never>
        Returns: undefined
      }
      update_group_standings: {
        Args: { p_group_id: string }
        Returns: undefined
      }
      update_player_ps: {
        Args: Record<PropertyKey, never>
        Returns: undefined
      }
      update_player_rank_score: {
        Args: Record<PropertyKey, never>
        Returns: undefined
      }
      update_player_rankings: {
        Args: Record<PropertyKey, never>
        Returns: undefined
      }
      update_team_money_won: {
        Args: { team_uuid: string }
        Returns: undefined
      }
      update_team_rankings: {
        Args: Record<PropertyKey, never>
        Returns: undefined
      }
      update_user_claims: {
        Args: { p_user_id: string }
        Returns: boolean
      }
    }
    Enums: {
      app_role:
        | "admin"
        | "league_staff"
        | "user"
        | "editor"
        | "analyst"
        | "team_staff"
        | "player"
      award_types: "Offensive MVP" | "Defensive MVP" | "Rookie of Tournament"
      console: "Cross Play" | "Playstation" | "Xbox"
      event_tier: "T1" | "T2" | "T3" | "T4"
      event_type: "League" | "Tournament"
      game_year:
        | "2K16"
        | "2K17"
        | "2K18"
        | "2K19"
        | "2K20"
        | "2K21"
        | "2K22"
        | "2K23"
        | "2K24"
        | "2K25"
        | "2K26"
      leagues:
        | "Unified Pro Am Association"
        | "UPA College"
        | "WR"
        | "MPBA"
        | "Rising Stars"
        | "Staten Island Basketball Association"
        | "Hall Of Fame League"
        | "Dunk League"
        | "Road to 25K"
      player_position:
        | "Point Guard"
        | "Shooting Guard"
        | "Lock"
        | "Power Forward"
        | "Center"
      salary_tier: "S" | "A" | "B" | "C" | "D"
      stage:
        | "Regular Season"
        | "Group Play"
        | "Round 1"
        | "Round 2"
        | "Round 3"
        | "Round 4"
        | "Semi Finals"
        | "Finals"
        | "Grand Finals"
        | "L1"
        | "L2"
        | "L3"
        | "L4"
        | "L5"
        | "W1"
        | "W2"
        | "W3"
        | "W4"
        | "LF"
        | "WF"
      status:
        | "scheduled"
        | "in progress"
        | "completed"
        | "under review"
        | "reviewed"
        | "approved"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {
      app_role: [
        "admin",
        "league_staff",
        "user",
        "editor",
        "analyst",
        "team_staff",
        "player",
      ],
      award_types: ["Offensive MVP", "Defensive MVP", "Rookie of Tournament"],
      console: ["Cross Play", "Playstation", "Xbox"],
      event_tier: ["T1", "T2", "T3", "T4"],
      event_type: ["League", "Tournament"],
      game_year: [
        "2K16",
        "2K17",
        "2K18",
        "2K19",
        "2K20",
        "2K21",
        "2K22",
        "2K23",
        "2K24",
        "2K25",
        "2K26",
      ],
      leagues: [
        "Unified Pro Am Association",
        "UPA College",
        "WR",
        "MPBA",
        "Rising Stars",
        "Staten Island Basketball Association",
        "Hall Of Fame League",
        "Dunk League",
        "Road to 25K",
      ],
      player_position: [
        "Point Guard",
        "Shooting Guard",
        "Lock",
        "Power Forward",
        "Center",
      ],
      salary_tier: ["S", "A", "B", "C", "D"],
      stage: [
        "Regular Season",
        "Group Play",
        "Round 1",
        "Round 2",
        "Round 3",
        "Round 4",
        "Semi Finals",
        "Finals",
        "Grand Finals",
        "L1",
        "L2",
        "L3",
        "L4",
        "L5",
        "W1",
        "W2",
        "W3",
        "W4",
        "LF",
        "WF",
      ],
      status: [
        "scheduled",
        "in progress",
        "completed",
        "under review",
        "reviewed",
        "approved",
      ],
    },
  },
} as const

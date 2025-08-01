export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instanciate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "12.2.12 (cd3cf9e)"
  }
  graphql_public: {
    Tables: {
      [_ in never]: never
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      graphql: {
        Args: {
          operationName?: string
          query?: string
          variables?: Json
          extensions?: Json
        }
        Returns: Json
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
  public: {
    Tables: {
      awards_race: {
        Row: {
          award_type: Database["public"]["Enums"]["award_types"] | null
          award_winner: boolean | null
          created_at: string
          event_id: string | null
          id: string
          player_id: string | null
          rank: number | null
          rp_bonus: number | null
          team_id: string
        }
        Insert: {
          award_type?: Database["public"]["Enums"]["award_types"] | null
          award_winner?: boolean | null
          created_at?: string
          event_id?: string | null
          id?: string
          player_id?: string | null
          rank?: number | null
          rp_bonus?: number | null
          team_id: string
        }
        Update: {
          award_type?: Database["public"]["Enums"]["award_types"] | null
          award_winner?: boolean | null
          created_at?: string
          event_id?: string | null
          id?: string
          player_id?: string | null
          rank?: number | null
          rp_bonus?: number | null
          team_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "awards_race_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "event_standings"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "awards_race_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "awards_race_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "awards_race_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "awards_race_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "upcoming_events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "awards_race_player_id_fkey"
            columns: ["player_id"]
            isOneToOne: false
            referencedRelation: "player_performance_summary"
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
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "awards_race_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "awards_race_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "awards_race_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "awards_race_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "awards_race_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "awards_race_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      draft_pool: {
        Row: {
          declared_at: string | null
          draft_notes: string | null
          draft_rating: number | null
          event_id: string | null
          player_id: string
          season: string | null
          status: string | null
        }
        Insert: {
          declared_at?: string | null
          draft_notes?: string | null
          draft_rating?: number | null
          event_id?: string | null
          player_id: string
          season?: string | null
          status?: string | null
        }
        Update: {
          declared_at?: string | null
          draft_notes?: string | null
          draft_rating?: number | null
          event_id?: string | null
          player_id?: string
          season?: string | null
          status?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "draft_pool_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "event_standings"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "draft_pool_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "draft_pool_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "draft_pool_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "draft_pool_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "upcoming_events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "draft_pool_player_id_fkey"
            columns: ["player_id"]
            isOneToOne: true
            referencedRelation: "player_performance_summary"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "draft_pool_player_id_fkey"
            columns: ["player_id"]
            isOneToOne: true
            referencedRelation: "players"
            referencedColumns: ["id"]
          },
        ]
      }
      event_group_members: {
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
            foreignKeyName: "event_group_members_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "event_groups"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "event_group_members_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["group_id"]
          },
          {
            foreignKeyName: "event_group_members_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["group_id"]
          },
          {
            foreignKeyName: "event_group_members_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "event_group_members_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "event_group_members_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "event_group_members_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "event_group_members_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "event_group_members_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "event_group_members_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      event_groups: {
        Row: {
          advancement_count: number | null
          created_at: string | null
          description: string | null
          event_id: string
          id: string
          max_teams: number | null
          name: string
          sort_order: number | null
          status: string | null
          updated_at: string | null
        }
        Insert: {
          advancement_count?: number | null
          created_at?: string | null
          description?: string | null
          event_id: string
          id?: string
          max_teams?: number | null
          name: string
          sort_order?: number | null
          status?: string | null
          updated_at?: string | null
        }
        Update: {
          advancement_count?: number | null
          created_at?: string | null
          description?: string | null
          event_id?: string
          id?: string
          max_teams?: number | null
          name?: string
          sort_order?: number | null
          status?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "event_groups_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "event_standings"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "event_groups_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "event_groups_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "event_groups_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "event_groups_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "upcoming_events"
            referencedColumns: ["id"]
          },
        ]
      }
      event_results: {
        Row: {
          awarded_at: string | null
          bonus_rp: number | null
          event_id: string
          id: string
          placement: number | null
          prize_amount: number | null
          rp_awarded: number | null
          team_id: string
          total_rp: number | null
          winner_banner_url: string | null
        }
        Insert: {
          awarded_at?: string | null
          bonus_rp?: number | null
          event_id: string
          id?: string
          placement?: number | null
          prize_amount?: number | null
          rp_awarded?: number | null
          team_id: string
          total_rp?: number | null
          winner_banner_url?: string | null
        }
        Update: {
          awarded_at?: string | null
          bonus_rp?: number | null
          event_id?: string
          id?: string
          placement?: number | null
          prize_amount?: number | null
          rp_awarded?: number | null
          team_id?: string
          total_rp?: number | null
          winner_banner_url?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "event_results_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "event_standings"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "event_results_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "event_results_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "event_results_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "event_results_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "upcoming_events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "event_results_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "event_results_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "event_results_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "event_results_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "event_results_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "event_results_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "event_results_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      events: {
        Row: {
          banner_url: string | null
          decay_days: number | null
          description: string | null
          end_date: string | null
          id: string
          is_global: boolean | null
          max_rp: number | null
          name: string
          prize_pool: number | null
          processed: boolean | null
          processed_at: string | null
          region_id: string | null
          rules_url: string | null
          season_number: number | null
          start_date: string | null
          status: string | null
          tier: Database["public"]["Enums"]["event_tier"] | null
          type: string | null
        }
        Insert: {
          banner_url?: string | null
          decay_days?: number | null
          description?: string | null
          end_date?: string | null
          id?: string
          is_global?: boolean | null
          max_rp?: number | null
          name: string
          prize_pool?: number | null
          processed?: boolean | null
          processed_at?: string | null
          region_id?: string | null
          rules_url?: string | null
          season_number?: number | null
          start_date?: string | null
          status?: string | null
          tier?: Database["public"]["Enums"]["event_tier"] | null
          type?: string | null
        }
        Update: {
          banner_url?: string | null
          decay_days?: number | null
          description?: string | null
          end_date?: string | null
          id?: string
          is_global?: boolean | null
          max_rp?: number | null
          name?: string
          prize_pool?: number | null
          processed?: boolean | null
          processed_at?: string | null
          region_id?: string | null
          rules_url?: string | null
          season_number?: number | null
          start_date?: string | null
          status?: string | null
          tier?: Database["public"]["Enums"]["event_tier"] | null
          type?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "events_region_id_fkey"
            columns: ["region_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["region_id"]
          },
          {
            foreignKeyName: "events_region_id_fkey"
            columns: ["region_id"]
            isOneToOne: false
            referencedRelation: "regions"
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
            referencedRelation: "event_groups"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "group_matches_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["group_id"]
          },
          {
            foreignKeyName: "group_matches_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["group_id"]
          },
          {
            foreignKeyName: "group_matches_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["match_id"]
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
            referencedRelation: "event_groups"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "group_standings_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["group_id"]
          },
          {
            foreignKeyName: "group_standings_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["group_id"]
          },
          {
            foreignKeyName: "group_standings_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "group_standings_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "group_standings_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "group_standings_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "group_standings_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "group_standings_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
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
      league_seasons: {
        Row: {
          created_at: string
          end_date: string
          event: string | null
          id: number
          is_active: boolean | null
          league_name: Database["public"]["Enums"]["leagues"]
          season_number: number
          start_date: string
          updated_at: string
        }
        Insert: {
          created_at?: string
          end_date: string
          event?: string | null
          id?: never
          is_active?: boolean | null
          league_name: Database["public"]["Enums"]["leagues"]
          season_number: number
          start_date: string
          updated_at?: string
        }
        Update: {
          created_at?: string
          end_date?: string
          event?: string | null
          id?: never
          is_active?: boolean | null
          league_name?: Database["public"]["Enums"]["leagues"]
          season_number?: number
          start_date?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "league_seasons_event_fkey"
            columns: ["event"]
            isOneToOne: false
            referencedRelation: "event_standings"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "league_seasons_event_fkey"
            columns: ["event"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "league_seasons_event_fkey"
            columns: ["event"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "league_seasons_event_fkey"
            columns: ["event"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "league_seasons_event_fkey"
            columns: ["event"]
            isOneToOne: false
            referencedRelation: "upcoming_events"
            referencedColumns: ["id"]
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
            referencedRelation: "match_details"
            referencedColumns: ["match_id"]
          },
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
            referencedRelation: "player_performance_summary"
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
            referencedRelation: "event_groups"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "match_points_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["group_id"]
          },
          {
            foreignKeyName: "match_points_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["group_id"]
          },
          {
            foreignKeyName: "match_points_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["match_id"]
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
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "match_points_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "match_points_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "match_points_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "match_points_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "match_points_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
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
          event_id: string | null
          id: string
          match_id: string | null
          review_status: string | null
          reviewed_at: string | null
          reviewed_by: string | null
          team_a_id: string | null
          team_a_name: string | null
          team_b_id: string | null
          team_b_name: string | null
        }
        Insert: {
          created_at?: string
          event_id?: string | null
          id?: string
          match_id?: string | null
          review_status?: string | null
          reviewed_at?: string | null
          reviewed_by?: string | null
          team_a_id?: string | null
          team_a_name?: string | null
          team_b_id?: string | null
          team_b_name?: string | null
        }
        Update: {
          created_at?: string
          event_id?: string | null
          id?: string
          match_id?: string | null
          review_status?: string | null
          reviewed_at?: string | null
          reviewed_by?: string | null
          team_a_id?: string | null
          team_a_name?: string | null
          team_b_id?: string | null
          team_b_name?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "match_submissions_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "event_standings"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "match_submissions_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "match_submissions_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "match_submissions_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "match_submissions_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "upcoming_events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "match_submissions_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["match_id"]
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
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "match_submissions_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "match_submissions_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "match_submissions_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "match_submissions_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "match_submissions_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
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
            referencedRelation: "event_standings"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "match_submissions_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "group_matches_view"
            referencedColumns: ["team_a_name"]
          },
          {
            foreignKeyName: "match_submissions_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "group_matches_view"
            referencedColumns: ["team_b_name"]
          },
          {
            foreignKeyName: "match_submissions_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "match_submissions_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "group_standings_view"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "match_submissions_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_name"]
          },
          {
            foreignKeyName: "match_submissions_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_name"]
          },
          {
            foreignKeyName: "match_submissions_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_name"]
          },
          {
            foreignKeyName: "match_submissions_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "match_submissions_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "player_performance_summary"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "match_submissions_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "match_submissions_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["name"]
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
            foreignKeyName: "match_submissions_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["team_a_name"]
          },
          {
            foreignKeyName: "match_submissions_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["team_b_name"]
          },
          {
            foreignKeyName: "match_submissions_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "upcoming_matches_view"
            referencedColumns: ["team_a_name"]
          },
          {
            foreignKeyName: "match_submissions_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "upcoming_matches_view"
            referencedColumns: ["team_b_name"]
          },
          {
            foreignKeyName: "match_submissions_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "match_submissions_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "match_submissions_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "match_submissions_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "match_submissions_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "match_submissions_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["id"]
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
            referencedRelation: "event_standings"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "match_submissions_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "group_matches_view"
            referencedColumns: ["team_a_name"]
          },
          {
            foreignKeyName: "match_submissions_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "group_matches_view"
            referencedColumns: ["team_b_name"]
          },
          {
            foreignKeyName: "match_submissions_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "match_submissions_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "group_standings_view"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "match_submissions_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_name"]
          },
          {
            foreignKeyName: "match_submissions_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_name"]
          },
          {
            foreignKeyName: "match_submissions_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_name"]
          },
          {
            foreignKeyName: "match_submissions_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "match_submissions_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "player_performance_summary"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "match_submissions_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "match_submissions_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["name"]
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
            foreignKeyName: "match_submissions_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["team_a_name"]
          },
          {
            foreignKeyName: "match_submissions_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["team_b_name"]
          },
          {
            foreignKeyName: "match_submissions_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "upcoming_matches_view"
            referencedColumns: ["team_a_name"]
          },
          {
            foreignKeyName: "match_submissions_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "upcoming_matches_view"
            referencedColumns: ["team_b_name"]
          },
        ]
      }
      matches: {
        Row: {
          boxscore_url: string | null
          event_id: string
          game_number: number | null
          id: string
          played_at: string | null
          score_a: number | null
          score_b: number | null
          stage: Database["public"]["Enums"]["stage"] | null
          team_a_id: string | null
          team_a_name: string | null
          team_b_id: string | null
          team_b_name: string | null
          winner_id: string | null
          winner_name: string | null
        }
        Insert: {
          boxscore_url?: string | null
          event_id: string
          game_number?: number | null
          id?: string
          played_at?: string | null
          score_a?: number | null
          score_b?: number | null
          stage?: Database["public"]["Enums"]["stage"] | null
          team_a_id?: string | null
          team_a_name?: string | null
          team_b_id?: string | null
          team_b_name?: string | null
          winner_id?: string | null
          winner_name?: string | null
        }
        Update: {
          boxscore_url?: string | null
          event_id?: string
          game_number?: number | null
          id?: string
          played_at?: string | null
          score_a?: number | null
          score_b?: number | null
          stage?: Database["public"]["Enums"]["stage"] | null
          team_a_id?: string | null
          team_a_name?: string | null
          team_b_id?: string | null
          team_b_name?: string | null
          winner_id?: string | null
          winner_name?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "matches_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "event_standings"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "matches_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "matches_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "matches_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "upcoming_events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
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
            referencedRelation: "event_standings"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "group_matches_view"
            referencedColumns: ["team_a_name"]
          },
          {
            foreignKeyName: "matches_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "group_matches_view"
            referencedColumns: ["team_b_name"]
          },
          {
            foreignKeyName: "matches_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "group_standings_view"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_name"]
          },
          {
            foreignKeyName: "matches_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_name"]
          },
          {
            foreignKeyName: "matches_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_name"]
          },
          {
            foreignKeyName: "matches_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "player_performance_summary"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["name"]
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
            foreignKeyName: "matches_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["team_a_name"]
          },
          {
            foreignKeyName: "matches_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["team_b_name"]
          },
          {
            foreignKeyName: "matches_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "upcoming_matches_view"
            referencedColumns: ["team_a_name"]
          },
          {
            foreignKeyName: "matches_team_a_name_fkey"
            columns: ["team_a_name"]
            isOneToOne: false
            referencedRelation: "upcoming_matches_view"
            referencedColumns: ["team_b_name"]
          },
          {
            foreignKeyName: "matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "event_standings"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "group_matches_view"
            referencedColumns: ["team_a_name"]
          },
          {
            foreignKeyName: "matches_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "group_matches_view"
            referencedColumns: ["team_b_name"]
          },
          {
            foreignKeyName: "matches_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "group_standings_view"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_name"]
          },
          {
            foreignKeyName: "matches_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_name"]
          },
          {
            foreignKeyName: "matches_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_name"]
          },
          {
            foreignKeyName: "matches_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "player_performance_summary"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["name"]
          },
          {
            foreignKeyName: "matches_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "team_roster_current"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["name"]
          },
          {
            foreignKeyName: "matches_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["team_a_name"]
          },
          {
            foreignKeyName: "matches_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["team_b_name"]
          },
          {
            foreignKeyName: "matches_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "upcoming_matches_view"
            referencedColumns: ["team_a_name"]
          },
          {
            foreignKeyName: "matches_team_b_name_fkey"
            columns: ["team_b_name"]
            isOneToOne: false
            referencedRelation: "upcoming_matches_view"
            referencedColumns: ["team_b_name"]
          },
          {
            foreignKeyName: "matches_winner_id_fkey"
            columns: ["winner_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "matches_winner_id_fkey"
            columns: ["winner_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "matches_winner_id_fkey"
            columns: ["winner_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "matches_winner_id_fkey"
            columns: ["winner_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "matches_winner_id_fkey"
            columns: ["winner_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "matches_winner_id_fkey"
            columns: ["winner_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_winner_id_fkey"
            columns: ["winner_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_winner_name_fkey"
            columns: ["winner_name"]
            isOneToOne: false
            referencedRelation: "event_standings"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_winner_name_fkey"
            columns: ["winner_name"]
            isOneToOne: false
            referencedRelation: "group_matches_view"
            referencedColumns: ["team_a_name"]
          },
          {
            foreignKeyName: "matches_winner_name_fkey"
            columns: ["winner_name"]
            isOneToOne: false
            referencedRelation: "group_matches_view"
            referencedColumns: ["team_b_name"]
          },
          {
            foreignKeyName: "matches_winner_name_fkey"
            columns: ["winner_name"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_winner_name_fkey"
            columns: ["winner_name"]
            isOneToOne: false
            referencedRelation: "group_standings_view"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_winner_name_fkey"
            columns: ["winner_name"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_name"]
          },
          {
            foreignKeyName: "matches_winner_name_fkey"
            columns: ["winner_name"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_name"]
          },
          {
            foreignKeyName: "matches_winner_name_fkey"
            columns: ["winner_name"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_name"]
          },
          {
            foreignKeyName: "matches_winner_name_fkey"
            columns: ["winner_name"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_winner_name_fkey"
            columns: ["winner_name"]
            isOneToOne: false
            referencedRelation: "player_performance_summary"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_winner_name_fkey"
            columns: ["winner_name"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_winner_name_fkey"
            columns: ["winner_name"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["name"]
          },
          {
            foreignKeyName: "matches_winner_name_fkey"
            columns: ["winner_name"]
            isOneToOne: false
            referencedRelation: "team_roster_current"
            referencedColumns: ["team_name"]
          },
          {
            foreignKeyName: "matches_winner_name_fkey"
            columns: ["winner_name"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["name"]
          },
          {
            foreignKeyName: "matches_winner_name_fkey"
            columns: ["winner_name"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["team_a_name"]
          },
          {
            foreignKeyName: "matches_winner_name_fkey"
            columns: ["winner_name"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["team_b_name"]
          },
          {
            foreignKeyName: "matches_winner_name_fkey"
            columns: ["winner_name"]
            isOneToOne: false
            referencedRelation: "upcoming_matches_view"
            referencedColumns: ["team_a_name"]
          },
          {
            foreignKeyName: "matches_winner_name_fkey"
            columns: ["winner_name"]
            isOneToOne: false
            referencedRelation: "upcoming_matches_view"
            referencedColumns: ["team_b_name"]
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
      player_rp_transactions: {
        Row: {
          amount: number
          created_at: string
          description: string
          event_id: string | null
          id: string
          match_id: string | null
          player_id: string | null
          type: string
          updated_at: string
        }
        Insert: {
          amount: number
          created_at?: string
          description: string
          event_id?: string | null
          id?: string
          match_id?: string | null
          player_id?: string | null
          type: string
          updated_at?: string
        }
        Update: {
          amount?: number
          created_at?: string
          description?: string
          event_id?: string | null
          id?: string
          match_id?: string | null
          player_id?: string | null
          type?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "player_rp_transactions_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "event_standings"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "player_rp_transactions_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "player_rp_transactions_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "player_rp_transactions_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "player_rp_transactions_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "upcoming_events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "player_rp_transactions_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["match_id"]
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
            referencedRelation: "player_performance_summary"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "player_rp_transactions_player_id_fkey"
            columns: ["player_id"]
            isOneToOne: false
            referencedRelation: "players"
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
        }
        Relationships: [
          {
            foreignKeyName: "player_stats_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["match_id"]
          },
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
            referencedRelation: "player_performance_summary"
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
            referencedRelation: "match_details"
            referencedColumns: ["mvp_player_name"]
          },
          {
            foreignKeyName: "player_stats_player_name_fkey"
            columns: ["player_name"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["gamertag"]
          },
          {
            foreignKeyName: "player_stats_player_name_fkey"
            columns: ["player_name"]
            isOneToOne: false
            referencedRelation: "player_performance_summary"
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
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "player_stats_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "player_stats_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "player_stats_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "player_stats_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "player_stats_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["id"]
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
          region_id: string | null
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
          region_id?: string | null
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
          region_id?: string | null
          salary_tier?: Database["public"]["Enums"]["salary_tier"] | null
          twitter_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "players_current_team_id_fkey"
            columns: ["current_team_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "players_current_team_id_fkey"
            columns: ["current_team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "players_current_team_id_fkey"
            columns: ["current_team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "players_current_team_id_fkey"
            columns: ["current_team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "players_current_team_id_fkey"
            columns: ["current_team_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "players_current_team_id_fkey"
            columns: ["current_team_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "players_current_team_id_fkey"
            columns: ["current_team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "players_region_id_fkey"
            columns: ["region_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["region_id"]
          },
          {
            foreignKeyName: "players_region_id_fkey"
            columns: ["region_id"]
            isOneToOne: false
            referencedRelation: "regions"
            referencedColumns: ["id"]
          },
        ]
      }
      profiles: {
        Row: {
          created_at: string | null
          email: string | null
          id: string
          role: string
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          email?: string | null
          id: string
          role?: string
          updated_at?: string | null
        }
        Update: {
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
          event_id: string | null
          expires_at: string | null
          id: string
          points: number | null
          source: string | null
          team_id: string | null
        }
        Insert: {
          awarded_at?: string | null
          event_id?: string | null
          expires_at?: string | null
          id?: string
          points?: number | null
          source?: string | null
          team_id?: string | null
        }
        Update: {
          awarded_at?: string | null
          event_id?: string | null
          expires_at?: string | null
          id?: string
          points?: number | null
          source?: string | null
          team_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "ranking_points_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "event_standings"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "ranking_points_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "ranking_points_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "ranking_points_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "ranking_points_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "upcoming_events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "ranking_points_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "ranking_points_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "ranking_points_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "ranking_points_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "ranking_points_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "ranking_points_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "ranking_points_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
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
      rp_transactions: {
        Row: {
          amount: number
          created_at: string
          description: string
          event_id: string | null
          id: string
          team_id: string | null
          type: string
          updated_at: string
        }
        Insert: {
          amount: number
          created_at?: string
          description: string
          event_id?: string | null
          id?: string
          team_id?: string | null
          type: string
          updated_at?: string
        }
        Update: {
          amount?: number
          created_at?: string
          description?: string
          event_id?: string | null
          id?: string
          team_id?: string | null
          type?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "rp_transactions_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "event_standings"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "rp_transactions_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "rp_transactions_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "rp_transactions_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "rp_transactions_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "upcoming_events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "rp_transactions_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "rp_transactions_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "rp_transactions_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "rp_transactions_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "rp_transactions_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "rp_transactions_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "rp_transactions_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
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
            referencedRelation: "match_details"
            referencedColumns: ["match_id"]
          },
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
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "team_match_stats_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "team_match_stats_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "team_match_stats_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "team_match_stats_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "team_match_stats_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
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
          event_id: string | null
          id: string
          is_captain: boolean | null
          is_player_coach: boolean | null
          joined_at: string | null
          left_at: string | null
          player_id: string | null
          team_id: string | null
        }
        Insert: {
          event_id?: string | null
          id?: string
          is_captain?: boolean | null
          is_player_coach?: boolean | null
          joined_at?: string | null
          left_at?: string | null
          player_id?: string | null
          team_id?: string | null
        }
        Update: {
          event_id?: string | null
          id?: string
          is_captain?: boolean | null
          is_player_coach?: boolean | null
          joined_at?: string | null
          left_at?: string | null
          player_id?: string | null
          team_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "team_rosters_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "event_standings"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "team_rosters_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "team_rosters_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "team_rosters_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "team_rosters_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "upcoming_events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "team_rosters_player_id_fkey"
            columns: ["player_id"]
            isOneToOne: false
            referencedRelation: "player_performance_summary"
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
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "team_rosters_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "team_rosters_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "team_rosters_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "team_rosters_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "team_rosters_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
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
          region_id: string | null
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
          region_id?: string | null
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
          region_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "teams_region_id_fkey"
            columns: ["region_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["region_id"]
          },
          {
            foreignKeyName: "teams_region_id_fkey"
            columns: ["region_id"]
            isOneToOne: false
            referencedRelation: "regions"
            referencedColumns: ["id"]
          },
        ]
      }
      teams_pot_tracker: {
        Row: {
          created_at: string
          event_id: string | null
          id: string
          placement: number | null
          prize_amount: number | null
          team_id: string | null
        }
        Insert: {
          created_at?: string
          event_id?: string | null
          id?: string
          placement?: number | null
          prize_amount?: number | null
          team_id?: string | null
        }
        Update: {
          created_at?: string
          event_id?: string | null
          id?: string
          placement?: number | null
          prize_amount?: number | null
          team_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "teams_pot_tracker_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "event_standings"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "teams_pot_tracker_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "teams_pot_tracker_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "teams_pot_tracker_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "teams_pot_tracker_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "upcoming_events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "teams_pot_tracker_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "teams_pot_tracker_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "teams_pot_tracker_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "teams_pot_tracker_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "teams_pot_tracker_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "teams_pot_tracker_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "teams_pot_tracker_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      upcoming_matches: {
        Row: {
          created_at: string | null
          event_id: string
          group_id: string | null
          id: string
          match_number: number | null
          notes: string | null
          round: number | null
          scheduled_at: string
          status: string | null
          stream_url: string | null
          team_a_id: string | null
          team_a_logo: string | null
          team_b_id: string | null
          team_b_logo: string | null
          updated_at: string | null
          venue: string | null
        }
        Insert: {
          created_at?: string | null
          event_id: string
          group_id?: string | null
          id?: string
          match_number?: number | null
          notes?: string | null
          round?: number | null
          scheduled_at: string
          status?: string | null
          stream_url?: string | null
          team_a_id?: string | null
          team_a_logo?: string | null
          team_b_id?: string | null
          team_b_logo?: string | null
          updated_at?: string | null
          venue?: string | null
        }
        Update: {
          created_at?: string | null
          event_id?: string
          group_id?: string | null
          id?: string
          match_number?: number | null
          notes?: string | null
          round?: number | null
          scheduled_at?: string
          status?: string | null
          stream_url?: string | null
          team_a_id?: string | null
          team_a_logo?: string | null
          team_b_id?: string | null
          team_b_logo?: string | null
          updated_at?: string | null
          venue?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "upcoming_matches_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "event_standings"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "upcoming_matches_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "upcoming_matches_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "upcoming_matches_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "upcoming_matches_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "upcoming_events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "upcoming_matches_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "event_groups"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "upcoming_matches_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["group_id"]
          },
          {
            foreignKeyName: "upcoming_matches_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["group_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
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
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      upcoming_matches_backup: {
        Row: {
          created_at: string | null
          event_id: string | null
          group_id: string | null
          id: string | null
          match_number: number | null
          notes: string | null
          round: number | null
          scheduled_at: string | null
          status: string | null
          stream_url: string | null
          team_a_id: string | null
          team_b_id: string | null
          updated_at: string | null
          venue: string | null
        }
        Insert: {
          created_at?: string | null
          event_id?: string | null
          group_id?: string | null
          id?: string | null
          match_number?: number | null
          notes?: string | null
          round?: number | null
          scheduled_at?: string | null
          status?: string | null
          stream_url?: string | null
          team_a_id?: string | null
          team_b_id?: string | null
          updated_at?: string | null
          venue?: string | null
        }
        Update: {
          created_at?: string | null
          event_id?: string | null
          group_id?: string | null
          id?: string | null
          match_number?: number | null
          notes?: string | null
          round?: number | null
          scheduled_at?: string | null
          status?: string | null
          stream_url?: string | null
          team_a_id?: string | null
          team_b_id?: string | null
          updated_at?: string | null
          venue?: string | null
        }
        Relationships: []
      }
      upcoming_matches_timezone_backup: {
        Row: {
          created_at: string | null
          event_id: string | null
          group_id: string | null
          id: string | null
          match_number: number | null
          notes: string | null
          round: number | null
          scheduled_at: string | null
          status: string | null
          stream_url: string | null
          team_a_id: string | null
          team_b_id: string | null
          updated_at: string | null
          venue: string | null
        }
        Insert: {
          created_at?: string | null
          event_id?: string | null
          group_id?: string | null
          id?: string | null
          match_number?: number | null
          notes?: string | null
          round?: number | null
          scheduled_at?: string | null
          status?: string | null
          stream_url?: string | null
          team_a_id?: string | null
          team_b_id?: string | null
          updated_at?: string | null
          venue?: string | null
        }
        Update: {
          created_at?: string | null
          event_id?: string | null
          group_id?: string | null
          id?: string | null
          match_number?: number | null
          notes?: string | null
          round?: number | null
          scheduled_at?: string | null
          status?: string | null
          stream_url?: string | null
          team_a_id?: string | null
          team_b_id?: string | null
          updated_at?: string | null
          venue?: string | null
        }
        Relationships: []
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
    }
    Views: {
      event_standings: {
        Row: {
          bonus_rp: number | null
          event_id: string | null
          event_name: string | null
          event_tier: Database["public"]["Enums"]["event_tier"] | null
          event_type: string | null
          matches_lost: number | null
          matches_played: number | null
          matches_won: number | null
          placement: number | null
          region_name: string | null
          rp_awarded: number | null
          status: string | null
          team_id: string | null
          team_name: string | null
          total_rp: number | null
        }
        Relationships: [
          {
            foreignKeyName: "event_results_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "event_results_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "event_results_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "event_results_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "event_results_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "event_results_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "event_results_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      group_matches_view: {
        Row: {
          event_id: string | null
          event_name: string | null
          group_id: string | null
          group_name: string | null
          id: string | null
          match_id: string | null
          match_number: number | null
          played_at: string | null
          round: number | null
          score_a: number | null
          score_b: number | null
          team_a_id: string | null
          team_a_name: string | null
          team_b_id: string | null
          team_b_name: string | null
          winner_id: string | null
          winner_name: string | null
        }
        Relationships: [
          {
            foreignKeyName: "event_groups_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "event_standings"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "event_groups_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "event_groups_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "event_groups_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "event_groups_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "upcoming_events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "group_matches_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "event_groups"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "group_matches_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["group_id"]
          },
          {
            foreignKeyName: "group_matches_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["group_id"]
          },
          {
            foreignKeyName: "group_matches_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["match_id"]
          },
          {
            foreignKeyName: "group_matches_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "matches"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
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
            foreignKeyName: "matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_winner_id_fkey"
            columns: ["winner_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "matches_winner_id_fkey"
            columns: ["winner_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "matches_winner_id_fkey"
            columns: ["winner_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "matches_winner_id_fkey"
            columns: ["winner_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "matches_winner_id_fkey"
            columns: ["winner_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "matches_winner_id_fkey"
            columns: ["winner_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
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
      group_points_standings: {
        Row: {
          event_id: string | null
          event_name: string | null
          forfeits: number | null
          group_id: string | null
          group_name: string | null
          losses: number | null
          matches_played: number | null
          point_differential: number | null
          points_against: number | null
          points_for: number | null
          position: number | null
          regular_wins: number | null
          team_id: string | null
          team_name: string | null
          total_points: number | null
          updated_at: string | null
          wins: number | null
          wins_by_20_plus: number | null
        }
        Relationships: [
          {
            foreignKeyName: "event_groups_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "event_standings"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "event_groups_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "event_groups_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "event_groups_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "event_groups_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "upcoming_events"
            referencedColumns: ["id"]
          },
        ]
      }
      group_standings_view: {
        Row: {
          event_id: string | null
          event_name: string | null
          group_id: string | null
          group_name: string | null
          id: string | null
          logo_url: string | null
          losses: number | null
          matches_played: number | null
          point_differential: number | null
          points_against: number | null
          points_for: number | null
          position: number | null
          team_id: string | null
          team_name: string | null
          updated_at: string | null
          wins: number | null
        }
        Relationships: [
          {
            foreignKeyName: "event_groups_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "event_standings"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "event_groups_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "event_groups_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "event_groups_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "event_groups_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "upcoming_events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "group_standings_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "event_groups"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "group_standings_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["group_id"]
          },
          {
            foreignKeyName: "group_standings_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["group_id"]
          },
          {
            foreignKeyName: "group_standings_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "group_standings_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "group_standings_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "group_standings_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "group_standings_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "group_standings_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
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
      match_details: {
        Row: {
          event_id: string | null
          event_name: string | null
          group_id: string | null
          group_name: string | null
          match_id: string | null
          match_number: number | null
          mvp_player_id: string | null
          mvp_player_name: string | null
          played_at: string | null
          round: number | null
          score_a: number | null
          score_b: number | null
          team_a_id: string | null
          team_a_name: string | null
          team_b_id: string | null
          team_b_name: string | null
          winner_id: string | null
          winner_name: string | null
        }
        Relationships: [
          {
            foreignKeyName: "match_mvp_player_id_fkey"
            columns: ["mvp_player_id"]
            isOneToOne: false
            referencedRelation: "player_performance_summary"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "match_mvp_player_id_fkey"
            columns: ["mvp_player_id"]
            isOneToOne: false
            referencedRelation: "players"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "event_standings"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "matches_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "matches_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "matches_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "upcoming_events"
            referencedColumns: ["id"]
          },
        ]
      }
      player_match_history: {
        Row: {
          assists: number | null
          blocks: number | null
          event_id: string | null
          event_name: string | null
          fg_percentage: number | null
          fga: number | null
          fgm: number | null
          fouls: number | null
          ft_percentage: number | null
          fta: number | null
          ftm: number | null
          gamertag: string | null
          is_mvp: boolean | null
          is_winner: boolean | null
          match_id: string | null
          performance_score: number | null
          played_at: string | null
          player_id: string | null
          plus_minus: number | null
          points: number | null
          rebounds: number | null
          steals: number | null
          team_id: string | null
          team_name: string | null
          three_point_percentage: number | null
          three_points_attempted: number | null
          three_points_made: number | null
          turnovers: number | null
        }
        Relationships: [
          {
            foreignKeyName: "player_stats_match_id_fkey"
            columns: ["match_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["match_id"]
          },
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
            referencedRelation: "player_performance_summary"
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
            foreignKeyName: "player_stats_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "player_stats_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "player_stats_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "player_stats_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "player_stats_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "player_stats_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["id"]
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
      player_performance_summary: {
        Row: {
          avg_assists: number | null
          avg_blocks: number | null
          avg_performance_score: number | null
          avg_points: number | null
          avg_rebounds: number | null
          avg_steals: number | null
          current_team_id: string | null
          gamertag: string | null
          id: string | null
          matches_played: number | null
          monthly_value: number | null
          mvp_count: number | null
          player_rank_score: number | null
          player_rp: number | null
          position: Database["public"]["Enums"]["player_position"] | null
          region_name: string | null
          salary_tier: Database["public"]["Enums"]["salary_tier"] | null
          team_name: string | null
        }
        Relationships: [
          {
            foreignKeyName: "players_current_team_id_fkey"
            columns: ["current_team_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "players_current_team_id_fkey"
            columns: ["current_team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "players_current_team_id_fkey"
            columns: ["current_team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "players_current_team_id_fkey"
            columns: ["current_team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "players_current_team_id_fkey"
            columns: ["current_team_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "players_current_team_id_fkey"
            columns: ["current_team_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "players_current_team_id_fkey"
            columns: ["current_team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      regional_team_rankings: {
        Row: {
          current_rp: number | null
          elo_rating: number | null
          leaderboard_tier: string | null
          player_rank_score: number | null
          region_id: string | null
          region_name: string | null
          regional_rank: number | null
          team_id: string | null
          team_name: string | null
        }
        Relationships: []
      }
      team_performance_summary: {
        Row: {
          current_rp: number | null
          elo_rating: number | null
          global_rank: number | null
          id: string | null
          leaderboard_tier: string | null
          matches_lost: number | null
          matches_won: number | null
          name: string | null
          region_id: string | null
          region_name: string | null
          total_matches: number | null
          win_percentage: number | null
        }
        Relationships: [
          {
            foreignKeyName: "teams_region_id_fkey"
            columns: ["region_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["region_id"]
          },
          {
            foreignKeyName: "teams_region_id_fkey"
            columns: ["region_id"]
            isOneToOne: false
            referencedRelation: "regions"
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
            referencedRelation: "player_performance_summary"
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
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "team_rosters_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "team_rosters_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "team_rosters_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "team_rosters_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "team_rosters_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
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
      tournament_schedule: {
        Row: {
          end_time: string | null
          end_time_formatted: string | null
          event_id: string | null
          event_name: string | null
          group_name: string | null
          start_date: string | null
          start_time: string | null
          start_time_formatted: string | null
          status: string | null
          team_a_logo: string | null
          team_a_name: string | null
          team_b_logo: string | null
          team_b_name: string | null
          venue: string | null
        }
        Relationships: []
      }
      upcoming_events: {
        Row: {
          banner_url: string | null
          description: string | null
          draft_pool_count: number | null
          end_date: string | null
          id: string | null
          is_global: boolean | null
          max_rp: number | null
          name: string | null
          region_name: string | null
          registered_teams_count: number | null
          rules_url: string | null
          start_date: string | null
          tier: Database["public"]["Enums"]["event_tier"] | null
          type: string | null
        }
        Relationships: []
      }
      upcoming_matches_view: {
        Row: {
          event_banner_url: string | null
          event_id: string | null
          event_name: string | null
          group_id: string | null
          group_name: string | null
          id: string | null
          match_number: number | null
          notes: string | null
          region_name: string | null
          round: number | null
          scheduled_at: string | null
          status: string | null
          stream_url: string | null
          team_a_id: string | null
          team_a_logo: string | null
          team_a_name: string | null
          team_b_id: string | null
          team_b_logo: string | null
          team_b_name: string | null
          venue: string | null
        }
        Relationships: [
          {
            foreignKeyName: "upcoming_matches_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "event_standings"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "upcoming_matches_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "upcoming_matches_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "player_match_history"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "upcoming_matches_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "tournament_schedule"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "upcoming_matches_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "upcoming_events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "upcoming_matches_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "event_groups"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "upcoming_matches_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["group_id"]
          },
          {
            foreignKeyName: "upcoming_matches_group_id_fkey"
            columns: ["group_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["group_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_a_id_fkey"
            columns: ["team_a_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
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
            referencedRelation: "group_points_standings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_a_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["team_b_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "match_details"
            referencedColumns: ["winner_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "regional_team_rankings"
            referencedColumns: ["team_id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_b_id_fkey"
            columns: ["team_b_id"]
            isOneToOne: false
            referencedRelation: "team_performance_summary"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "upcoming_matches_team_b_id_fkey"
            columns: ["team_b_id"]
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
          p_event_id: string
          p_team_id: string
          p_bonus_amount: number
          p_description?: string
        }
        Returns: {
          player_name: string
          bonus_rp: number
          new_total_rp: number
        }[]
      }
      add_mvp_bonus_rp: {
        Args: {
          p_event_id: string
          p_mvp_bonus?: number
          p_description?: string
        }
        Returns: {
          player_name: string
          bonus_rp: number
          new_total_rp: number
        }[]
      }
      add_player_to_team_roster: {
        Args: {
          in_event_id: string
          in_team_id: string
          in_player_id: string
          in_joined_at?: string
          in_remove_from_draft_pool?: boolean
        }
        Returns: undefined
      }
      adjust_team_rp: {
        Args: {
          team_id_param: string
          amount: number
          reason: string
          event_id_param?: string
        }
        Returns: undefined
      }
      analyze_elo_distribution: {
        Args: Record<PropertyKey, never>
        Returns: {
          elo_range: string
          team_count: number
          percentage: number
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
          team_name: string
          placement: number
          player_name: string
          bonus_rp: number
          new_total_rp: number
        }[]
      }
      calculate_all_player_salaries: {
        Args: Record<PropertyKey, never>
        Returns: {
          player_uuid: string
          player_name: string
          raw_score: number
          tier_name: string
          monthly_value: number
        }[]
      }
      calculate_defensive_mvp_score: {
        Args: { player_uuid: string; event_uuid: string }
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
        Args: { player_uuid: string; event_uuid: string }
        Returns: number
      }
      calculate_player_salary: {
        Args: { player_uuid: string }
        Returns: {
          player_name: string
          raw_score: number
          tier_name: string
          monthly_value: number
        }[]
      }
      calculate_rookie_score: {
        Args: { player_uuid: string; event_uuid: string }
        Returns: number
      }
      calculate_team_total_money_won: {
        Args: { team_uuid: string }
        Returns: number
      }
      complete_upcoming_match: {
        Args: {
          p_upcoming_match_id: string
          p_score_a: number
          p_score_b: number
          p_winner_id?: string
        }
        Returns: string
      }
      generate_award_nominees: {
        Args: { event_uuid: string; award_type_param: string; top_n?: number }
        Returns: {
          player_id: string
          player_name: string
          team_id: string
          team_name: string
          score: number
          rank: number
        }[]
      }
      generate_bracket_matches: {
        Args: {
          p_event_id: string
          p_bracket_start_time: string
          p_match_duration_minutes?: number
        }
        Returns: undefined
      }
      generate_bracket_seeding: {
        Args: { p_event_id: string }
        Returns: {
          seed_position: number
          team_id: string
          team_name: string
          original_group_id: string
          original_group_name: string
          group_position: number
        }[]
      }
      generate_group_matches: {
        Args: { p_group_id: string }
        Returns: undefined
      }
      get_elo_bounds: {
        Args: Record<PropertyKey, never>
        Returns: {
          min_bound: number
          max_bound: number
          starting_elo: number
          normalized_starting: number
        }[]
      }
      initialize_new_season: {
        Args: { season_name: string }
        Returns: undefined
      }
      recalculate_all_rankings: {
        Args: Record<PropertyKey, never>
        Returns: undefined
      }
      recent_games_for_player: {
        Args: { player_id_param: string }
        Returns: {
          match_id: string
          played_at: string
          points: number
          rebounds: number
          assists: number
          steals: number
          blocks: number
          turnovers: number
          pf: number
          fgm: number
          fga: number
          three_points_made: number
          three_points_attempted: number
          ftm: number
          fta: number
          fg_pct: number
          three_pt_pct: number
          ft_pct: number
          opponent_team_id: string
          opponent_name: string
          opponent_logo: string
          location: string
          result: string
          score_a: number
          score_b: number
        }[]
      }
      record_match_forfeit: {
        Args: { p_match_id: string; p_forfeiting_team_id: string }
        Returns: undefined
      }
      schedule_rp_decay: {
        Args: Record<PropertyKey, never>
        Returns: undefined
      }
      select_award_winner: {
        Args: {
          event_uuid: string
          award_type_param: string
          winner_player_id: string
        }
        Returns: undefined
      }
      update_all_teams_money_won: {
        Args: Record<PropertyKey, never>
        Returns: undefined
      }
      update_awards_race: {
        Args: { event_uuid: string; award_type_param: string; top_n?: number }
        Returns: undefined
      }
      update_elo_after_match: {
        Args: {
          winner_id_param: string
          loser_id_param: string
          k_factor?: number
        }
        Returns: undefined
      }
      update_event_players_rp: {
        Args:
          | {
              event_id_param: string
              bonus_rp: number
              description_param: string
            }
          | {
              event_id_param: string
              rating_param?: number
              bonus_amount?: number
              description_param?: string
              performance_score_param?: number
            }
        Returns: {
          player_id: string
          player_name: string
          transaction_id: string
          amount: number
        }[]
      }
      update_event_players_rp_hybrid: {
        Args: {
          event_id_param: string
          base_rp?: number
          bonus_amount?: number
          description_param?: string
        }
        Returns: {
          player_id: string
          player_name: string
          transaction_id: string
          amount: number
          hybrid_score: number
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
      update_team_money_won: {
        Args: { team_uuid: string }
        Returns: undefined
      }
      update_team_rankings: {
        Args: Record<PropertyKey, never>
        Returns: undefined
      }
    }
    Enums: {
      award_types: "Offensive MVP" | "Defensive MVP" | "Rookie of Tournament"
      event_tier: "T1" | "T2" | "T3" | "T4"
      event_type: "League" | "Tournament"
      leagues:
        | "UPA"
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
  graphql_public: {
    Enums: {},
  },
  public: {
    Enums: {
      award_types: ["Offensive MVP", "Defensive MVP", "Rookie of Tournament"],
      event_tier: ["T1", "T2", "T3", "T4"],
      event_type: ["League", "Tournament"],
      leagues: [
        "UPA",
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
    },
  },
} as const
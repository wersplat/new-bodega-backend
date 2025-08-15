-- Migration Script for Backend Updates

-- 1. Enable Row Level Security on tables that don't have it
ALTER TABLE public.matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.match_mvp ENABLE ROW LEVEL SECURITY;

-- 2. Add missing indexes for foreign keys to improve query performance
-- Tournaments table foreign keys
CREATE INDEX IF NOT EXISTS idx_tournaments_region_id ON public.tournaments (region_id);

-- Matches table foreign keys
CREATE INDEX IF NOT EXISTS idx_matches_tournament_id ON public.matches (tournament_id);
CREATE INDEX IF NOT EXISTS idx_matches_team_a_id ON public.matches (team_a_id);
CREATE INDEX IF NOT EXISTS idx_matches_team_b_id ON public.matches (team_b_id);
CREATE INDEX IF NOT EXISTS idx_matches_winner_id ON public.matches (winner_id);
CREATE INDEX IF NOT EXISTS idx_matches_team_a_name ON public.matches (team_a_name);
CREATE INDEX IF NOT EXISTS idx_matches_team_b_name ON public.matches (team_b_name);
CREATE INDEX IF NOT EXISTS idx_matches_winner_name ON public.matches (winner_name);

-- Player stats foreign keys
CREATE INDEX IF NOT EXISTS idx_player_stats_player_id ON public.player_stats (player_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_match_id ON public.player_stats (match_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_team_id ON public.player_stats (team_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_player_name ON public.player_stats (player_name);

-- Players table foreign keys
CREATE INDEX IF NOT EXISTS idx_players_region_id ON public.players (region_id);
CREATE INDEX IF NOT EXISTS idx_players_current_team_id ON public.players (current_team_id);

-- Team rosters foreign keys
CREATE INDEX IF NOT EXISTS idx_team_rosters_team_id ON public.team_rosters (team_id);
CREATE INDEX IF NOT EXISTS idx_team_rosters_player_id ON public.team_rosters (player_id);
CREATE INDEX IF NOT EXISTS idx_team_rosters_tournament_id ON public.team_rosters (tournament_id);

-- 3. Add updated_at trigger to tables that need it
CREATE OR REPLACE FUNCTION public.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = now(); 
   RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Add updated_at column and trigger to tables that don't have it
ALTER TABLE public.draft_pool 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT now();

CREATE TRIGGER update_draft_pool_timestamp
BEFORE UPDATE ON public.draft_pool
FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();

ALTER TABLE public.player_stats 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT now();

CREATE TRIGGER update_player_stats_timestamp
BEFORE UPDATE ON public.player_stats
FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();

-- 4. Clean up backup tables that are no longer needed
-- Comment these out if you still need these tables
DROP TABLE IF EXISTS public.upcoming_matches_backup;
DROP TABLE IF EXISTS public.upcoming_matches_timezone_backup;

-- 5. Add RLS policies for security

-- Matches table RLS policies
CREATE POLICY "Enable read access for all users" ON public.matches
    FOR SELECT USING (true);
    
CREATE POLICY "Enable insert for authenticated users only" ON public.matches
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');
    
CREATE POLICY "Enable update for authenticated users only" ON public.matches
    FOR UPDATE USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

-- Match MVP table RLS policies
CREATE POLICY "Enable read access for all users" ON public.match_mvp
    FOR SELECT USING (true);
    
CREATE POLICY "Enable insert for authenticated users only" ON public.match_mvp
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');
    
CREATE POLICY "Enable update for authenticated users only" ON public.match_mvp
    FOR UPDATE USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

-- 6. Add missing constraints for data integrity
ALTER TABLE public.match_submissions 
ADD CONSTRAINT match_submissions_review_status_check 
CHECK (review_status IN ('pending', 'approved', 'rejected'));

-- 7. Create a view for easier access to player performance data
CREATE OR REPLACE VIEW public.player_performance_view AS
SELECT 
    p.id,
    p.gamertag,
    p.position,
    p.current_team_id,
    t.name AS team_name,
    p.player_rp,
    p.player_rank_score,
    p.salary_tier,
    p.monthly_value,
    COUNT(ps.id) AS games_played,
    COALESCE(AVG(ps.points), 0) AS avg_points,
    COALESCE(AVG(ps.assists), 0) AS avg_assists,
    COALESCE(AVG(ps.rebounds), 0) AS avg_rebounds,
    COALESCE(AVG(ps.steals), 0) AS avg_steals,
    COALESCE(AVG(ps.blocks), 0) AS avg_blocks,
    COALESCE(AVG(ps.ps), 0) AS avg_performance_score
FROM 
    public.players p
LEFT JOIN 
    public.teams t ON p.current_team_id = t.id
LEFT JOIN 
    public.player_stats ps ON p.id = ps.player_id
GROUP BY 
    p.id, p.gamertag, p.position, p.current_team_id, t.name, p.player_rp, p.player_rank_score, p.salary_tier, p.monthly_value;

-- Add security to the view
ALTER VIEW public.player_performance_view SET (security_invoker = on);

-- 8. Create a function to calculate team standings
CREATE OR REPLACE FUNCTION public.calculate_team_standings(tournament_id_param UUID)
RETURNS TABLE (
    team_id UUID,
    team_name TEXT,
    games_played INT,
    wins INT,
    losses INT,
    points_for INT,
    points_against INT,
    point_differential INT,
    win_percentage FLOAT
) AS $$
BEGIN
    RETURN QUERY
    WITH team_a_stats AS (
        SELECT 
            m.team_a_id as team_id,
            t.name as team_name,
            COUNT(*) as games_played,
            SUM(CASE WHEN m.winner_id = m.team_a_id THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN m.winner_id IS NOT NULL AND m.winner_id != m.team_a_id THEN 1 ELSE 0 END) as losses,
            SUM(m.team_a_score) as points_for,
            SUM(m.team_b_score) as points_against,
            SUM(m.team_a_score - m.team_b_score) as point_differential
        FROM 
            public.matches m
        JOIN 
            public.teams t ON m.team_a_id = t.id
        WHERE 
            m.tournament_id = tournament_id_param
        GROUP BY 
            m.team_a_id, t.name
            
        UNION ALL
        
        SELECT 
            m.team_b_id as team_id,
            t.name as team_name,
            COUNT(*) as games_played,
            SUM(CASE WHEN m.winner_id = m.team_b_id THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN m.winner_id IS NOT NULL AND m.winner_id != m.team_b_id THEN 1 ELSE 0 END) as losses,
            SUM(m.team_b_score) as points_for,
            SUM(m.team_a_score) as points_against,
            SUM(m.team_b_score - m.team_a_score) as point_differential
        FROM 
            public.matches m
        JOIN 
            public.teams t ON m.team_b_id = t.id
        WHERE 
            m.tournament_id = tournament_id_param
        GROUP BY 
            m.team_b_id, t.name
    )
    SELECT 
        team_id,
        team_name,
        SUM(games_played) as total_games_played,
        SUM(wins) as total_wins,
        SUM(losses) as total_losses,
        SUM(points_for) as total_points_for,
        SUM(points_against) as total_points_against,
        SUM(point_differential) as total_point_differential,
        CASE 
            WHEN SUM(games_played) > 0 THEN ROUND(SUM(wins)::numeric / SUM(games_played)::numeric, 3)
            ELSE 0 
        END as win_percentage
    FROM 
        team_a_stats
    GROUP BY 
        team_id, team_name
    ORDER BY 
        win_percentage DESC,
        total_point_differential DESC,
        total_points_for DESC;
END;
$$ LANGUAGE plpgsql;

-- 9. Add a notification trigger for new match submissions
CREATE OR REPLACE FUNCTION public.notify_match_submission()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.notifications (
        title, 
        message, 
        type
    ) VALUES (
        'New Match Submission',
        'A new match has been submitted for review between ' || 
        (SELECT name FROM public.teams WHERE id = NEW.team_a_id) || ' and ' || 
        (SELECT name FROM public.teams WHERE id = NEW.team_b_id),
        'info'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER match_submission_notification
AFTER INSERT ON public.match_submissions
FOR EACH ROW EXECUTE FUNCTION public.notify_match_submission();

-- 10. Add a function to update player rankings based on performance
CREATE OR REPLACE FUNCTION public.update_player_rankings()
RETURNS void AS $$
BEGIN
    -- Update player_rank_score based on recent performance
    UPDATE public.players p
    SET player_rank_score = (
        SELECT 
            COALESCE(AVG(ps.ps) * 0.7, 0) + 
            COALESCE(p.player_rp * 0.3, 0)
        FROM 
            public.player_stats ps
        WHERE 
            ps.player_id = p.id AND
            ps.created_at > (CURRENT_DATE - INTERVAL '30 days')
    );
    
    -- Update salary tier based on player_rank_score
    UPDATE public.players p
    SET salary_tier = (
        SELECT 
            CASE 
                WHEN p.player_rank_score >= 25 THEN 'S'::salary_tier
                WHEN p.player_rank_score >= 20 THEN 'A'::salary_tier
                WHEN p.player_rank_score >= 15 THEN 'B'::salary_tier
                WHEN p.player_rank_score >= 10 THEN 'C'::salary_tier
                ELSE 'D'::salary_tier
            END
    );
    
    -- Update monthly_value based on salary_tier
    UPDATE public.players p
    SET monthly_value = (
        SELECT 
            CASE p.salary_tier
                WHEN 'S' THEN 5000
                WHEN 'A' THEN 4000
                WHEN 'B' THEN 3000
                WHEN 'C' THEN 2000
                WHEN 'D' THEN 1000
                ELSE 0
            END
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 11. Rename event_groups to tournament_groups
ALTER TABLE event_groups RENAME TO tournament_groups;

-- 12. Rename event_group_members to tournament_group_members
ALTER TABLE event_group_members RENAME TO tournament_group_members;

-- 13. Rename event_results to tournament_results
ALTER TABLE event_results RENAME TO tournament_results;

-- 14. Update foreign key constraints
ALTER TABLE tournament_group_members 
  RENAME CONSTRAINT event_group_members_group_id_fkey TO tournament_group_members_group_id_fkey;

ALTER TABLE tournament_group_members
  RENAME CONSTRAINT event_group_members_team_id_fkey TO tournament_group_members_team_id_fkey;

ALTER TABLE tournament_groups
  RENAME CONSTRAINT event_groups_league_season_id_fkey TO tournament_groups_league_season_id_fkey;

ALTER TABLE tournament_groups
  RENAME CONSTRAINT event_groups_tournament_id_fkey TO tournament_groups_tournament_id_fkey;

ALTER TABLE tournament_results
  RENAME CONSTRAINT event_results_league_id_fkey TO tournament_results_league_id_fkey;

ALTER TABLE tournament_results
  RENAME CONSTRAINT event_results_team_id_fkey TO tournament_results_team_id_fkey;

ALTER TABLE tournament_results
  RENAME CONSTRAINT event_results_tournament_id_fkey TO tournament_results_tournament_id_fkey;

-- 15. Update function parameters to use tournament_id
CREATE OR REPLACE FUNCTION public.add_tournament_placement_bonus_rp_to_players(
  p_bonus_amount numeric,
  p_description text DEFAULT NULL::text,
  p_tournament_id uuid,
  p_team_id uuid
)
RETURNS void
LANGUAGE plpgsql
AS $function$
-- Implementation here
$function$;

CREATE OR REPLACE FUNCTION public.add_mvp_bonus_rp(
  p_description text DEFAULT NULL::text,
  p_tournament_id uuid,
  p_mvp_bonus numeric DEFAULT 0
)
RETURNS void
LANGUAGE plpgsql
AS $function$
-- Implementation here
$function$;

-- 16. Update other functions to use tournament_id
CREATE OR REPLACE FUNCTION public.calculate_defensive_mvp_score(
  tournament_uuid uuid,
  player_uuid uuid
)
RETURNS numeric
LANGUAGE plpgsql
AS $function$
-- Implementation here
$function$;

-- Repeat for other functions like calculate_offensive_mvp_score, calculate_rookie_score, etc.

-- 17. Update view and function dependencies
ALTER VIEW public.group_matches 
  ALTER COLUMN group_id SET DATA TYPE uuid USING group_id::uuid,
  ALTER COLUMN group_id SET NOT NULL;

ALTER VIEW public.group_standings 
  ALTER COLUMN group_id SET DATA TYPE uuid USING group_id::uuid,
  ALTER COLUMN group_id SET NOT NULL;

-- 18. Drop old functions that are no longer needed
DROP FUNCTION IF EXISTS public.add_event_placement_bonus_rp_to_players(
  numeric, text, uuid, uuid
);

DROP FUNCTION IF EXISTS public.add_mvp_bonus_rp(text, uuid, numeric);
DROP FUNCTION IF EXISTS public.calculate_defensive_mvp_score(uuid, uuid);
-- Drop other old functions

-- 19. Update any remaining references in triggers or other database objects
-- (Add specific updates based on your schema)

-- 20. Update any materialized views or other database objects
-- (Add specific updates based on your schema)
-- Migration Script for Backend Updates

-- 1. Enable Row Level Security on tables that don't have it
ALTER TABLE public.matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.match_mvp ENABLE ROW LEVEL SECURITY;

-- 2. Add missing indexes for foreign keys to improve query performance
-- Events table foreign keys
CREATE INDEX IF NOT EXISTS idx_events_region_id ON public.events (region_id);

-- Matches table foreign keys
CREATE INDEX IF NOT EXISTS idx_matches_event_id ON public.matches (event_id);
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
CREATE INDEX IF NOT EXISTS idx_team_rosters_event_id ON public.team_rosters (event_id);

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
CREATE OR REPLACE FUNCTION public.calculate_team_standings(event_id_param UUID)
RETURNS TABLE (
    team_id UUID,
    team_name TEXT,
    matches_played INTEGER,
    wins INTEGER,
    losses INTEGER,
    points_for INTEGER,
    points_against INTEGER,
    point_differential INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH team_matches AS (
        -- Team A matches
        SELECT 
            m.team_a_id AS team_id,
            t.name AS team_name,
            COUNT(*) AS matches_played,
            COUNT(*) FILTER (WHERE m.winner_id = m.team_a_id) AS wins,
            COUNT(*) FILTER (WHERE m.winner_id != m.team_a_id AND m.winner_id IS NOT NULL) AS losses,
            SUM(m.score_a) AS points_for,
            SUM(m.score_b) AS points_against
        FROM 
            public.matches m
        JOIN 
            public.teams t ON m.team_a_id = t.id
        WHERE 
            m.event_id = event_id_param
        GROUP BY 
            m.team_a_id, t.name
            
        UNION ALL
        
        -- Team B matches
        SELECT 
            m.team_b_id AS team_id,
            t.name AS team_name,
            COUNT(*) AS matches_played,
            COUNT(*) FILTER (WHERE m.winner_id = m.team_b_id) AS wins,
            COUNT(*) FILTER (WHERE m.winner_id != m.team_b_id AND m.winner_id IS NOT NULL) AS losses,
            SUM(m.score_b) AS points_for,
            SUM(m.score_a) AS points_against
        FROM 
            public.matches m
        JOIN 
            public.teams t ON m.team_b_id = t.id
        WHERE 
            m.event_id = event_id_param
        GROUP BY 
            m.team_b_id, t.name
    )
    SELECT 
        tm.team_id,
        tm.team_name,
        SUM(tm.matches_played)::INTEGER AS matches_played,
        SUM(tm.wins)::INTEGER AS wins,
        SUM(tm.losses)::INTEGER AS losses,
        SUM(tm.points_for)::INTEGER AS points_for,
        SUM(tm.points_against)::INTEGER AS points_against,
        (SUM(tm.points_for) - SUM(tm.points_against))::INTEGER AS point_differential
    FROM 
        team_matches tm
    GROUP BY 
        tm.team_id, tm.team_name
    ORDER BY 
        wins DESC, point_differential DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

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
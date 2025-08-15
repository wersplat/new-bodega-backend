-- Migration to rename event-related tables to use tournament terminology

-- 1. Rename tables
ALTER TABLE event_groups RENAME TO tournament_groups;
ALTER TABLE event_group_members RENAME TO tournament_group_members;


-- 2. Rename constraints
-- For tournament_groups
ALTER TABLE tournament_groups 
  RENAME CONSTRAINT event_groups_pkey TO tournament_groups_pkey;
ALTER TABLE tournament_groups
  RENAME CONSTRAINT event_groups_league_season_id_fkey TO tournament_groups_league_season_id_fkey;
ALTER TABLE tournament_groups
  RENAME CONSTRAINT event_groups_tournament_id_fkey TO tournament_groups_tournament_id_fkey;

-- For tournament_group_members
ALTER TABLE tournament_group_members
  RENAME CONSTRAINT event_group_members_pkey TO tournament_group_members_pkey;
ALTER TABLE tournament_group_members
  RENAME CONSTRAINT event_group_members_group_id_fkey TO tournament_group_members_group_id_fkey;
ALTER TABLE tournament_group_members
  RENAME CONSTRAINT event_group_members_team_id_fkey TO tournament_group_members_team_id_fkey;


-- 3. Update indexes
ALTER INDEX IF EXISTS idx_event_groups_tournament_id RENAME TO idx_tournament_groups_tournament_id;
ALTER INDEX IF EXISTS idx_event_group_members_group_id RENAME TO idx_tournament_group_members_group_id;
ALTER INDEX IF EXISTS idx_event_group_members_team_id RENAME TO idx_tournament_group_members_team_id;

-- 4. Update views to reference new table names
CREATE OR REPLACE VIEW public.group_matches AS
  SELECT gm.*
  FROM group_matches gm
  JOIN tournament_groups tg ON gm.group_id = tg.id;

CREATE OR REPLACE VIEW public.group_standings AS
  SELECT gs.*
  FROM group_standings gs
  JOIN tournament_groups tg ON gs.group_id = tg.id;

-- 5. Update functions to use new table names and parameters
CREATE OR REPLACE FUNCTION public.calculate_team_standings(tournament_id_param UUID)
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
    -- Implementation using tournament_groups instead of event_groups
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
            matches m
        JOIN 
            teams t ON m.team_a_id = t.id
        JOIN
            tournament_groups tg ON m.tournament_id = tg.tournament_id
        WHERE 
            m.tournament_id = tournament_id_param
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
            matches m
        JOIN 
            teams t ON m.team_b_id = t.id
        JOIN
            tournament_groups tg ON m.tournament_id = tg.tournament_id
        WHERE 
            m.tournament_id = tournament_id_param
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
$$ LANGUAGE plpgsql;

-- 6. Update any triggers or other database objects that reference the old table names
-- (Add specific updates based on your schema)

-- 7. Drop old views and functions that are no longer needed
-- (Add specific DROP statements for any objects that were replaced)

-- 8. Update any materialized views or other database objects
-- (Add specific updates based on your schema)

-- 9. Add any new indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tournament_groups_league_season_id ON public.tournament_groups(league_season_id);

-- 10. Add comments to document the changes
COMMENT ON TABLE public.tournament_groups IS 'Stores tournament groups, previously named event_groups';
COMMENT ON TABLE public.tournament_group_members IS 'Stores tournament group members, previously named event_group_members';

-- 11. Update any RLS (Row Level Security) policies if needed
-- (Add specific policy updates based on your security requirements)

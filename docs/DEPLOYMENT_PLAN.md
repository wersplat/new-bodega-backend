# Database Migration Deployment Plan: Event to Tournament Terminology

## Overview
This document outlines the steps required to migrate the database from event-related to tournament-related terminology in the production environment. The migration includes renaming tables, updating constraints, and ensuring data consistency.

## Pre-Deployment Checklist

### 1. Backup Production Database
- [ ] Create a full backup of the production database
- [ ] Verify backup integrity
- [ ] Document the backup location and credentials

### 2. Notify Stakeholders
- [ ] Notify all teams about the scheduled maintenance window
- [ ] Update status page to reflect upcoming maintenance
- [ ] Send email notification to all users about the scheduled downtime

### 3. Prepare Rollback Plan
- [ ] Document steps to restore from backup if needed
- [ ] Prepare rollback SQL scripts
- [ ] Test rollback procedure in staging environment

## Migration Steps

### 1. Maintenance Mode
- [ ] Enable maintenance mode on the application
- [ ] Verify no active database connections
- [ ] Disable any scheduled jobs or cron tasks

### 2. Execute Database Migration
Run the following migration script in the specified order:

1. **Rename Tables**
   ```sql
   ALTER TABLE tournament_groupss RENAME TO tournament_groups;
   ALTER TABLE tournament_groups_members RENAME TO tournament_group_members;
   ```

2. **Rename Constraints**
   ```sql
   -- For tournament_groups
   ALTER TABLE tournament_groups 
     RENAME CONSTRAINT tournament_groupss_pkey TO tournament_groups_pkey;
   
   -- For tournament_group_members
   ALTER TABLE tournament_group_members
     RENAME CONSTRAINT tournament_groups_members_pkey TO tournament_group_members_pkey;
   ```

3. **Update Indexes**
   ```sql
   ALTER INDEX IF EXISTS idx_tournament_groupss_tournament_id RENAME TO idx_tournament_groups_tournament_id;
   ALTER INDEX IF EXISTS idx_tournament_groups_members_group_id RENAME TO idx_tournament_group_members_group_id;
   ALTER INDEX IF EXISTS idx_tournament_groups_members_team_id RENAME TO idx_tournament_group_members_team_id;
   ```

4. **Update Views and Functions**
   - [ ] Deploy updated views from `20250201000000_rename_event_to_tournament.sql`
   - [ ] Verify all functions are using the new table names

### 3. Deploy Application Changes
- [ ] Deploy updated application code with tournament terminology
- [ ] Verify all database queries use the new table names
- [ ] Update any environment variables if needed

### 4. Verification
- [ ] Run smoke tests to verify basic functionality
- [ ] Verify tournament creation and management
- [ ] Check group assignments and team registrations
- [ ] Validate leaderboard calculations
- [ ] Test API endpoints with the new tournament terminology

### 5. Monitoring
- [ ] Monitor error logs for any issues
- [ ] Check application performance metrics
- [ ] Verify database query performance

## Post-Deployment Tasks

### 1. Update API Documentation
- [ ] Update API documentation to reflect the new endpoints
- [ ] Update any client libraries or SDKs
- [ ] Notify API consumers about the changes

### 2. Cleanup (After Verification Period)
- [ ] Remove deprecated event-related code
- [ ] Clean up any temporary migration files
- [ ] Update database backup procedures

### 3. Communication
- [ ] Notify stakeholders about successful deployment
- [ ] Update status page
- [ ] Send deployment summary to the team

## Rollback Procedure

If critical issues are encountered:

1. Enable maintenance mode
2. Stop all application instances
3. Restore database from backup
4. Revert application code to previous version
5. Disable maintenance mode
6. Notify stakeholders about rollback

## Timeline

| Task | Duration | Owner |
|------|----------|-------|
| Pre-deployment backup | 30 min | DBA |
| Application maintenance mode | 5 min | DevOps |
| Database migration | 15 min | DBA |
| Application deployment | 10 min | DevOps |
| Verification testing | 30 min | QA |
| Monitoring period | 2 hours | Ops |
| Documentation updates | 1 hour | Tech Writer |

## Contacts

- **Primary DBA**: [Name] - [Phone] - [Email]
- **Backup DBA**: [Name] - [Phone] - [Email]
- **DevOps Lead**: [Name] - [Phone] - [Email]
- **On-call Engineer**: [Name] - [Phone] - [Email]

## Post-Mortem

After the migration is complete, schedule a post-mortem meeting to:
- Review the deployment process
- Document any issues encountered
- Identify areas for improvement
- Update runbooks and documentation

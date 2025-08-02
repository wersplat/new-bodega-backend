#!/usr/bin/env python3
"""
Script to apply database migrations to Supabase
"""
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def apply_migration(migration_file):
    """Apply a single migration file to the database"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get database connection details from environment
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL environment variable not set")
            
        # Extract the migration SQL
        with open(migration_file, 'r') as f:
            sql = f.read()
            
        logger.info(f"Applying migration: {migration_file}")
        
        # Use psql to apply the migration
        # Note: This requires psql to be installed and in the PATH
        cmd = f'psql "{db_url}" -v ON_ERROR_STOP=1 -f "{migration_file}"'
        logger.info(f"Executing: {cmd}")
        
        # Execute the command
        result = os.system(cmd)
        
        if result != 0:
            raise Exception(f"Migration failed with exit code {result}")
            
        logger.info("Migration applied successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error applying migration: {str(e)}", exc_info=True)
        return False

def find_migrations():
    """Find all migration files in the migrations directory"""
    migrations_dir = Path(__file__).parent.parent / "migrations"
    if not migrations_dir.exists():
        logger.error(f"Migrations directory not found: {migrations_dir}")
        return []
        
    # Get all .sql files and sort them by name
    migration_files = sorted(migrations_dir.glob("*.sql"))
    return migration_files

def main():
    """Main function to apply all pending migrations"""
    try:
        # Check if a specific migration file was provided
        if len(sys.argv) > 1:
            migration_file = Path(sys.argv[1]).absolute()
            if not migration_file.exists():
                logger.error(f"Migration file not found: {migration_file}")
                return 1
                
            success = apply_migration(migration_file)
            return 0 if success else 1
        
        # Otherwise, find and apply all migrations
        migration_files = find_migrations()
        if not migration_files:
            logger.warning("No migration files found")
            return 0
            
        logger.info(f"Found {len(migration_files)} migration(s) to apply")
        
        for migration_file in migration_files:
            logger.info(f"\n--- Applying {migration_file.name} ---")
            if not apply_migration(migration_file):
                logger.error(f"Failed to apply migration: {migration_file.name}")
                return 1
                
        logger.info("\nAll migrations applied successfully")
        return 0
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())

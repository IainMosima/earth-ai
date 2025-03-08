import logging
import argparse
import sys
import os
import subprocess
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = Path("/Users/apple/Desktop/earth-ai")
ALEMBIC_DIR = PROJECT_ROOT / "migrations"

def migrate_up():
    """
    Create all necessary database tables using Alembic
    """
    try:
        logger.info("Running migrations to create database tables...")
        
        # Run Alembic upgrade
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Alembic migration failed: {result.stderr}")
            return False
            
        logger.info(f"Migration output: {result.stdout}")
        logger.info("All database tables have been created successfully.")
        return True
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        return False

def migrate_down():
    """
    Remove all database tables using Alembic
    """
    try:
        logger.info("Dropping all database tables...")
        
        # Run Alembic downgrade to base (removes all migrations)
        result = subprocess.run(
            ["alembic", "downgrade", "base"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Alembic downgrade failed: {result.stderr}")
            return False
            
        logger.info(f"Downgrade output: {result.stdout}")
        logger.info("All database tables have been dropped successfully.")
        return True
    except Exception as e:
        logger.error(f"Error dropping database tables: {str(e)}")
        return False

def main():
    """
    Command line interface for the migration manager
    """
    parser = argparse.ArgumentParser(description='Database Migration Manager')
    parser.add_argument('direction', choices=['up', 'down'], help='Migration direction: "up" to create tables, "down" to remove them')
    
    args = parser.parse_args()
    
    if args.direction == 'up':
        success = migrate_up()
    else:
        success = migrate_down()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

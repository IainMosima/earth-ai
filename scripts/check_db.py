#!/usr/bin/env python3
"""
Database connectivity check script
Run this script to verify database connection
"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, wait_for_db

if __name__ == "__main__":
    print("Checking database connectivity...")
    success = wait_for_db(retries=5, delay=2)
    
    if success:
        print("✅ Database connection successful!")
        sys.exit(0)
    else:
        print("❌ Database connection failed!")
        print("\nTroubleshooting tips:")
        print("1. Ensure your database container is running:")
        print("   docker ps | grep postgres")
        print("2. Check your database credentials in .env file")
        print("3. Verify that port 5432 is accessible")
        print("4. If running locally, ensure the correct host is specified")
        sys.exit(1)

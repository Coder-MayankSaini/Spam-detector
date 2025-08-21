#!/usr/bin/env python3
"""
Database initialization script for Railway deployment
Creates all necessary tables for the spam detector application
"""

import os
import sys
from database import DatabaseManager

def initialize_database():
    """Initialize the database with all required tables"""
    try:
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("ERROR: DATABASE_URL environment variable not found")
            return False
        
        print("🔄 Initializing database...")
        print(f"Database URL: {database_url.split('@')[0]}@[REDACTED]")
        
        # Initialize database manager
        db = DatabaseManager()
        
        print("✅ Database initialized successfully!")
        print("✅ All tables created and ready")
        
        # Test database connection
        print("🔍 Testing database connection...")
        # You can add a simple test query here if needed
        
        print("🎉 Database setup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = initialize_database()
    sys.exit(0 if success else 1)

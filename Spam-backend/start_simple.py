#!/usr/bin/env python3
"""
Simple startup script for Spam Detector Backend
Uses simplified in-memory database to avoid PostgreSQL dependency issues
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_basic_env():
    """Create a basic .env file if it doesn't exist"""
    env_file = Path('.env')
    if not env_file.exists():
        logger.info("Creating basic .env file...")
        basic_env = """DEBUG=true
JWT_SECRET_KEY=dev-secret-key-change-in-production
CORS_ORIGINS=http://localhost:3000,https://spamwall.vercel.app
FRONTEND_URL=https://spamwall.vercel.app
HOST=0.0.0.0
PORT=5001
"""
        with open('.env', 'w') as f:
            f.write(basic_env)
        logger.info("✅ Basic .env file created")

def main():
    """Main startup function"""
    logger.info("🚀 Starting Spam Detector Backend (Simplified Version)...")
    
    # Create basic environment if needed
    create_basic_env()
    
    # Import and run the Flask app
    try:
        from app_simple import app, config
        logger.info("✅ Simplified app imported successfully")
        
        logger.info(f"🌐 Starting server on {config.HOST}:{config.PORT}")
        logger.info(f"🔧 Debug mode: {config.DEBUG}")
        logger.info("📝 Using in-memory database (no PostgreSQL required)")
        
        app.run(
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG
        )
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.info("💡 Make sure basic dependencies are installed")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        logger.error("Full error:", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

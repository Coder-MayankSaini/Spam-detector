#!/usr/bin/env python3
"""
Diagnostic script for Spam Detector Backend
This script helps identify and fix common issues.
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Setup logging for diagnostics"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def check_environment():
    """Check environment variables and configuration"""
    logger = logging.getLogger(__name__)
    logger.info("🔍 Checking environment configuration...")
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        logger.warning("❌ .env file not found")
        logger.info("💡 Creating a basic .env file from template...")
        
        # Create basic .env file
        basic_env = """DEBUG=true
JWT_SECRET_KEY=dev-secret-key-change-in-production
CORS_ORIGINS=http://localhost:3000,https://spamwall.vercel.app
FRONTEND_URL=https://spamwall.vercel.app
"""
        with open('.env', 'w') as f:
            f.write(basic_env)
        logger.info("✅ Basic .env file created")
    else:
        logger.info("✅ .env file found")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("✅ Environment variables loaded")
    except ImportError:
        logger.error("❌ python-dotenv not installed")
        return False
    
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    logger = logging.getLogger(__name__)
    logger.info("📦 Checking dependencies...")
    
    required_packages = [
        'flask',
        'flask_cors',
        'sklearn',
        'joblib',
        'pandas',
        'numpy',
        'bcrypt',
        'PIL',
        'cv2'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            elif package == 'cv2':
                import cv2
            else:
                __import__(package)
            logger.info(f"✅ {package}")
        except ImportError:
            logger.error(f"❌ {package} not found")
            missing_packages.append(package)
    
    if missing_packages:
        logger.error("❌ Missing packages found")
        logger.info("💡 Install missing packages with: pip install -r requirements.txt")
        return False
    
    logger.info("✅ All dependencies are available")
    return True

def check_model():
    """Check if spam detection model exists or can be created"""
    logger = logging.getLogger(__name__)
    logger.info("🤖 Checking spam detection model...")
    
    model_path = 'spam_model.joblib'
    
    if os.path.exists(model_path):
        logger.info(f"✅ Model file found: {model_path}")
        try:
            import joblib
            model = joblib.load(model_path)
            test_prediction = model.predict(["test email"])[0]
            logger.info(f"✅ Model loaded and tested successfully")
        except Exception as e:
            logger.error(f"❌ Model loading failed: {e}")
            return False
    else:
        logger.warning(f"⚠️  Model file not found: {model_path}")
        logger.info("💡 Model will be created automatically on first run")
    
    return True

def check_database():
    """Check database connection (if configured)"""
    logger = logging.getLogger(__name__)
    logger.info("🗄️  Checking database configuration...")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.warning("⚠️  DATABASE_URL not set - using in-memory fallback")
        logger.info("💡 For production, set up PostgreSQL and configure DATABASE_URL")
        return True
    
    try:
        import psycopg2
        logger.info("✅ PostgreSQL driver (psycopg2) available")
        
        # Test connection
        conn = psycopg2.connect(database_url)
        conn.close()
        logger.info("✅ Database connection successful")
        
    except ImportError:
        logger.error("❌ psycopg2 not installed")
        logger.info("💡 Install with: pip install psycopg2-binary")
        return False
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.info("💡 Check your DATABASE_URL and ensure PostgreSQL is running")
        return False
    
    return True

def run_diagnostics():
    """Run all diagnostic checks"""
    logger = setup_logging()
    logger.info("🚀 Starting Spam Detector Backend Diagnostics")
    logger.info("=" * 50)
    
    checks = [
        ("Environment", check_environment),
        ("Dependencies", check_dependencies),
        ("Model", check_model),
        ("Database", check_database)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        logger.info(f"\n🔍 Running {check_name} Check...")
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            logger.error(f"❌ {check_name} check failed with exception: {e}")
            all_passed = False
    
    logger.info("\n" + "=" * 50)
    if all_passed:
        logger.info("✅ All checks passed! The backend should work correctly.")
        logger.info("🚀 You can now start the server with: python app.py")
    else:
        logger.error("❌ Some checks failed. Please fix the issues above.")
        logger.info("💡 Check the logs above for specific instructions.")
    
    return all_passed

if __name__ == "__main__":
    success = run_diagnostics()
    sys.exit(0 if success else 1)

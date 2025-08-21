#!/usr/bin/env python3
"""
Production startup script that mimics Railway environment
Use this for local testing before deploying
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    logger.info("Checking dependencies...")
    
    required_packages = [
        'flask', 'flask_cors', 'sklearn', 'pandas', 'numpy', 
        'PIL', 'pytesseract', 'cv2', 'nltk', 'bs4', 'bcrypt', 
        'jwt', 'joblib', 'gunicorn'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'PIL':
                from PIL import Image
            elif package == 'cv2':
                import cv2
            elif package == 'jwt':
                import jwt
            else:
                __import__(package)
            logger.info(f"✅ {package}")
        except ImportError:
            logger.error(f"❌ {package}")
            missing.append(package)
    
    if missing:
        logger.error("Missing packages found. Install with:")
        logger.error("pip install -r requirements.txt")
        return False
    
    logger.info("All dependencies available!")
    return True

def setup_environment():
    """Setup environment variables"""
    env_file = Path('.env')
    if not env_file.exists():
        logger.info("Creating development .env file...")
        dev_env = """DEBUG=true
JWT_SECRET_KEY=dev-secret-key-for-testing-only-64-characters-long-change-in-prod
CORS_ORIGINS=http://localhost:3000,https://spamwall.vercel.app
FRONTEND_URL=https://spamwall.vercel.app
HOST=0.0.0.0
PORT=5000
TESSERACT_PATH=/usr/bin/tesseract
"""
        with open('.env', 'w') as f:
            f.write(dev_env)
        logger.info("Development environment created")

def download_nltk_data():
    """Download required NLTK data"""
    logger.info("Downloading NLTK data...")
    try:
        import nltk
        nltk_downloads = ['punkt', 'stopwords', 'wordnet', 'vader_lexicon']
        for item in nltk_downloads:
            try:
                nltk.download(item, quiet=True)
                logger.info(f"Downloaded {item}")
            except Exception as e:
                logger.warning(f"Could not download {item}: {e}")
    except Exception as e:
        logger.error(f"NLTK setup failed: {e}")

def test_ocr():
    """Test OCR functionality"""
    logger.info("Testing OCR functionality...")
    try:
        from PIL import Image
        import pytesseract
        
        # Create test image
        test_img = Image.new('RGB', (200, 50), color='white')
        
        # Test Tesseract
        text = pytesseract.image_to_string(test_img)
        logger.info("✅ Tesseract OCR working")
        
        # Test EasyOCR
        try:
            import easyocr
            reader = easyocr.Reader(['en'], gpu=False)
            logger.info("✅ EasyOCR working")
        except Exception as e:
            logger.warning(f"EasyOCR not available: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"OCR test failed: {e}")
        return False

def test_spam_model():
    """Test spam detection model"""
    logger.info("Testing spam detection...")
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.naive_bayes import MultinomialNB
        from sklearn.pipeline import make_pipeline
        
        # Create test model
        model = make_pipeline(TfidfVectorizer(), MultinomialNB())
        model.fit(['spam email', 'normal email'], [1, 0])
        
        # Test prediction
        pred = model.predict(['test email'])[0]
        logger.info("✅ Spam detection model working")
        return True
        
    except Exception as e:
        logger.error(f"Spam model test failed: {e}")
        return False

def start_production_server():
    """Start with Gunicorn (production-like)"""
    logger.info("Starting production server with Gunicorn...")
    
    cmd = [
        sys.executable, '-m', 'gunicorn',
        'app_production:app',
        '--bind', '0.0.0.0:5000',
        '--workers', '2',
        '--timeout', '60',
        '--log-level', 'info',
        '--reload'  # For development
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Server failed to start: {e}")

def start_development_server():
    """Start with Flask development server"""
    logger.info("Starting development server...")
    
    try:
        from app_production import app, config
        app.run(
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG
        )
    except Exception as e:
        logger.error(f"Development server failed: {e}")

def main():
    """Main function"""
    logger.info("🚀 Spam Detector Production Setup")
    logger.info("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Please install missing dependencies first")
        return False
    
    # Download NLTK data
    download_nltk_data()
    
    # Test components
    test_ocr()
    test_spam_model()
    
    # Choose server type
    server_type = input("\nChoose server type:\n1. Production (Gunicorn)\n2. Development (Flask)\nChoice (1/2): ").strip()
    
    if server_type == '1':
        start_production_server()
    else:
        start_development_server()

if __name__ == '__main__':
    main()
